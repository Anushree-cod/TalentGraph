"""
GitHub Data Fetcher — fetches comprehensive profile data via REST and GraphQL APIs.

Supports both authenticated (PAT) and unauthenticated modes.
- Authenticated: 5,000 requests/hour, GraphQL access
- Unauthenticated: 60 requests/hour, REST only (no GraphQL)
"""

import asyncio
import base64
import math
import re
import time
import logging
from typing import Any, Optional

import httpx

from backend.app.services.github_analyzer.config import settings
from backend.app.schemas.github_schemas import (
    GitHubProfile,
    RepoDetail,
    ContributionData,
)

logger = logging.getLogger(__name__)


class GitHubFetcher:
    """Async GitHub data fetcher using REST + GraphQL APIs."""

    def __init__(self):
        self.base_url = settings.github_api_base
        self.graphql_url = settings.github_graphql_url
        self.headers = settings.github_headers
        self.graphql_headers = settings.github_graphql_headers
        self.is_authenticated = settings.is_authenticated
        self.rate_limit_remaining: Optional[int] = None
        self.rate_limit_reset: Optional[int] = None

    def _update_rate_limit(self, response: httpx.Response):
        """Track GitHub API rate limit from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining:
            self.rate_limit_remaining = int(remaining)
        if reset:
            self.rate_limit_reset = int(reset)

    async def fetch_all(self, username: str) -> dict[str, Any]:
        """
        Fetch ALL available data for a GitHub user.
        Returns a dict with profile, repos, contributions, and metadata.
        """
        start_time = time.time()
        result = {
            "profile": None,
            "repositories": [],
            "contributions": None,
            "pinned_repos": [],
            "metadata": {
                "fetch_time_seconds": 0,
                "authenticated": self.is_authenticated,
                "rate_limit_remaining": None,
                "errors": [],
            },
        }

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        ) as client:
            # ── Step 1: Fetch profile ──────────────────────────────────────
            profile = await self._fetch_profile(client, username)
            if not profile:
                result["metadata"]["errors"].append("Failed to fetch user profile")
                return result
            result["profile"] = profile

            # ── Step 2: Fetch repos (paginated) ───────────────────────────
            repos = await self._fetch_all_repos(client, username)
            result["metadata"]["total_repos_found"] = len(repos)

            # Sort by stars+recency and limit
            repos = self._prioritize_repos(repos)
            limited_repos = repos[: settings.max_repos_to_analyze]

            # ── Step 3: Fetch detailed repo data in parallel ──────────────
            detailed_repos = await self._fetch_repo_details(
                client, username, limited_repos
            )
            result["repositories"] = detailed_repos

            # ── Step 4: Fetch contributions via GraphQL (if authenticated)
            if self.is_authenticated:
                contributions = await self._fetch_contributions_graphql(
                    client, username
                )
                if contributions:
                    result["contributions"] = contributions

                # Also fetch pinned repos
                pinned = await self._fetch_pinned_repos_graphql(client, username)
                result["pinned_repos"] = pinned
            else:
                # Fallback: estimate contributions from events
                contributions = await self._fetch_contributions_from_events(
                    client, username
                )
                result["contributions"] = contributions

            # ── Metadata ──────────────────────────────────────────────────
            result["metadata"]["fetch_time_seconds"] = round(
                time.time() - start_time, 2
            )
            result["metadata"]["rate_limit_remaining"] = self.rate_limit_remaining
            result["metadata"]["repos_analyzed"] = len(detailed_repos)

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # REST API Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def _fetch_profile(
        self, client: httpx.AsyncClient, username: str
    ) -> Optional[GitHubProfile]:
        """Fetch basic user profile via REST API."""
        try:
            response = await client.get(
                f"{self.base_url}/users/{username}",
                headers=self.headers,
            )
            self._update_rate_limit(response)

            if response.status_code == 404:
                logger.error(f"GitHub user '{username}' not found")
                return None
            response.raise_for_status()

            data = response.json()
            return GitHubProfile(
                username=data.get("login", username),
                name=data.get("name"),
                bio=data.get("bio"),
                location=data.get("location"),
                company=data.get("company"),
                blog=data.get("blog"),
                email=data.get("email"),
                twitter_username=data.get("twitter_username"),
                avatar_url=data.get("avatar_url"),
                html_url=data.get("html_url", f"https://github.com/{username}"),
                followers=data.get("followers", 0),
                following=data.get("following", 0),
                public_repos=data.get("public_repos", 0),
                public_gists=data.get("public_gists", 0),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                hireable=data.get("hireable"),
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching profile: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching profile for {username}: {e}")
            return None

    async def _fetch_all_repos(
        self, client: httpx.AsyncClient, username: str
    ) -> list[dict]:
        """Fetch all public repositories with pagination."""
        all_repos = []
        page = 1
        per_page = 100

        while True:
            try:
                response = await client.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "direction": "desc",
                        "type": "owner",  # Only repos owned by user, not forks
                    },
                )
                self._update_rate_limit(response)
                response.raise_for_status()

                repos = response.json()
                if not repos:
                    break

                all_repos.extend(repos)
                page += 1

                # Safety: don't paginate more than 10 pages (1000 repos)
                if page > 10:
                    break

            except Exception as e:
                logger.error(f"Error fetching repos page {page}: {e}")
                break

        return all_repos

    def _prioritize_repos(self, repos: list[dict]) -> list[dict]:
        """Sort repos by a priority score (stars, recency, activity)."""

        def repo_priority(repo: dict) -> float:
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            is_fork = repo.get("fork", False)

            # Penalize forks
            fork_penalty = 0.3 if is_fork else 1.0

            # Recency bonus (pushed_at)
            recency = 0
            pushed_at = repo.get("pushed_at")
            if pushed_at:
                try:
                    from datetime import datetime, timezone

                    pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                    days_ago = (
                        datetime.now(timezone.utc) - pushed
                    ).days
                    recency = max(0, 100 - days_ago)  # 0-100, higher = more recent
                except Exception:
                    recency = 0

            score = (stars * 3 + forks * 2 + recency * 0.5) * fork_penalty
            return score

        repos.sort(key=repo_priority, reverse=True)
        return repos

    async def _fetch_repo_details(
        self,
        client: httpx.AsyncClient,
        username: str,
        repos: list[dict],
    ) -> list[RepoDetail]:
        """Fetch detailed data for each repo (languages, topics, README) in parallel."""

        async def fetch_single_repo_detail(repo_data: dict) -> RepoDetail:
            repo_name = repo_data.get("name", "")
            full_name = repo_data.get("full_name", f"{username}/{repo_name}")

            # Build base RepoDetail from list data
            detail = RepoDetail(
                name=repo_name,
                full_name=full_name,
                description=repo_data.get("description"),
                html_url=repo_data.get("html_url", ""),
                language=repo_data.get("language"),
                topics=repo_data.get("topics", []),
                stargazers_count=repo_data.get("stargazers_count", 0),
                forks_count=repo_data.get("forks_count", 0),
                watchers_count=repo_data.get("watchers_count", 0),
                open_issues_count=repo_data.get("open_issues_count", 0),
                size=repo_data.get("size", 0),
                fork=repo_data.get("fork", False),
                archived=repo_data.get("archived", False),
                created_at=repo_data.get("created_at"),
                updated_at=repo_data.get("updated_at"),
                pushed_at=repo_data.get("pushed_at"),
                default_branch=repo_data.get("default_branch", "main"),
                has_wiki=repo_data.get("has_wiki", False),
                has_pages=repo_data.get("has_pages", False),
                license_name=(
                    repo_data.get("license", {}) or {}
                ).get("spdx_id"),
            )

            # Fetch languages for this repo
            try:
                lang_resp = await client.get(
                    f"{self.base_url}/repos/{full_name}/languages",
                    headers=self.headers,
                )
                self._update_rate_limit(lang_resp)
                if lang_resp.status_code == 200:
                    detail.languages = lang_resp.json()
            except Exception as e:
                logger.warning(f"Failed to fetch languages for {full_name}: {e}")

            # Fetch README (only for top repos)
            if repos.index(repo_data) < settings.max_readme_repos:
                try:
                    readme_resp = await client.get(
                        f"{self.base_url}/repos/{full_name}/readme",
                        headers=self.headers,
                    )
                    self._update_rate_limit(readme_resp)
                    if readme_resp.status_code == 200:
                        readme_data = readme_resp.json()
                        content_b64 = readme_data.get("content", "")
                        if content_b64:
                            content = base64.b64decode(content_b64).decode(
                                "utf-8", errors="replace"
                            )
                            # Take first 500 chars as excerpt
                            detail.readme_excerpt = content[:500]
                except Exception as e:
                    logger.warning(f"Failed to fetch README for {full_name}: {e}")

            # Estimate commit count from the commits endpoint
            try:
                commits_resp = await client.get(
                    f"{self.base_url}/repos/{full_name}/commits",
                    headers=self.headers,
                    params={"per_page": 1},
                )
                self._update_rate_limit(commits_resp)
                if commits_resp.status_code == 200:
                    # Parse total from Link header pagination
                    link_header = commits_resp.headers.get("Link", "")
                    last_page_match = re.search(
                        r'page=(\d+)>; rel="last"', link_header
                    )
                    if last_page_match:
                        detail.commit_count = int(last_page_match.group(1))
                    else:
                        # Only one page, count the results
                        detail.commit_count = len(commits_resp.json())
            except Exception as e:
                logger.warning(f"Failed to fetch commit count for {full_name}: {e}")

            return detail

        # Run all repo detail fetches concurrently (with semaphore to limit concurrency)
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

        async def limited_fetch(repo_data: dict) -> RepoDetail:
            async with semaphore:
                return await fetch_single_repo_detail(repo_data)

        tasks = [limited_fetch(repo) for repo in repos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        detailed_repos = []
        for result in results:
            if isinstance(result, RepoDetail):
                detailed_repos.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error fetching repo details: {result}")

        return detailed_repos

    # ═══════════════════════════════════════════════════════════════════════════
    # GraphQL API Methods (require authentication)
    # ═══════════════════════════════════════════════════════════════════════════

    async def _fetch_contributions_graphql(
        self, client: httpx.AsyncClient, username: str
    ) -> Optional[ContributionData]:
        """Fetch contribution calendar via GitHub GraphQL API."""
        query = """
        query($username: String!) {
            user(login: $username) {
                contributionsCollection {
                    contributionCalendar {
                        totalContributions
                        weeks {
                            contributionDays {
                                contributionCount
                                date
                                color
                                weekday
                            }
                        }
                    }
                    totalCommitContributions
                    totalPullRequestContributions
                    totalPullRequestReviewContributions
                    totalIssueContributions
                    totalRepositoryContributions
                }
            }
        }
        """
        try:
            response = await client.post(
                self.graphql_url,
                headers=self.graphql_headers,
                json={"query": query, "variables": {"username": username}},
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return None

            user_data = data.get("data", {}).get("user", {})
            contrib_collection = user_data.get("contributionsCollection", {})
            calendar = contrib_collection.get("contributionCalendar", {})

            weeks = calendar.get("weeks", [])

            # Calculate streaks
            all_days = []
            for week in weeks:
                for day in week.get("contributionDays", []):
                    all_days.append(day)

            longest_streak, current_streak = self._calculate_streaks(all_days)
            total_weeks = max(len(weeks), 1)
            total_contributions = calendar.get("totalContributions", 0)

            return ContributionData(
                total_contributions=total_contributions,
                contribution_calendar=[
                    {
                        "week_index": i,
                        "days": week.get("contributionDays", []),
                    }
                    for i, week in enumerate(weeks)
                ],
                longest_streak=longest_streak,
                current_streak=current_streak,
                avg_contributions_per_week=round(
                    total_contributions / total_weeks, 1
                ),
            )
        except Exception as e:
            logger.error(f"Error fetching contributions via GraphQL: {e}")
            return None

    async def _fetch_pinned_repos_graphql(
        self, client: httpx.AsyncClient, username: str
    ) -> list[dict]:
        """Fetch user's pinned repositories via GraphQL."""
        query = """
        query($username: String!) {
            user(login: $username) {
                pinnedItems(first: 6, types: REPOSITORY) {
                    nodes {
                        ... on Repository {
                            name
                            description
                            url
                            stargazerCount
                            forkCount
                            primaryLanguage {
                                name
                                color
                            }
                        }
                    }
                }
            }
        }
        """
        try:
            response = await client.post(
                self.graphql_url,
                headers=self.graphql_headers,
                json={"query": query, "variables": {"username": username}},
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors (pinned): {data['errors']}")
                return []

            pinned_items = (
                data.get("data", {})
                .get("user", {})
                .get("pinnedItems", {})
                .get("nodes", [])
            )
            return pinned_items
        except Exception as e:
            logger.error(f"Error fetching pinned repos: {e}")
            return []

    # ═══════════════════════════════════════════════════════════════════════════
    # Fallback Methods (unauthenticated)
    # ═══════════════════════════════════════════════════════════════════════════

    async def _fetch_contributions_from_events(
        self, client: httpx.AsyncClient, username: str
    ) -> ContributionData:
        """
        Fallback: estimate contribution activity from public events.
        Only gets last 90 days of events (300 max).
        """
        total_events = 0
        push_events = 0
        daily_counts: dict[str, int] = {}

        try:
            for page in range(1, 4):  # Max 3 pages of events
                response = await client.get(
                    f"{self.base_url}/users/{username}/events/public",
                    headers=self.headers,
                    params={"per_page": 100, "page": page},
                )
                self._update_rate_limit(response)
                if response.status_code != 200:
                    break

                events = response.json()
                if not events:
                    break

                for event in events:
                    total_events += 1
                    event_type = event.get("type", "")
                    created_at = event.get("created_at", "")[:10]  # YYYY-MM-DD

                    if event_type == "PushEvent":
                        commits = (
                            event.get("payload", {}).get("commits", [])
                        )
                        count = len(commits)
                        push_events += count
                        daily_counts[created_at] = (
                            daily_counts.get(created_at, 0) + count
                        )
                    elif event_type in (
                        "PullRequestEvent",
                        "IssuesEvent",
                        "CreateEvent",
                    ):
                        daily_counts[created_at] = (
                            daily_counts.get(created_at, 0) + 1
                        )
                        push_events += 1

        except Exception as e:
            logger.error(f"Error fetching events: {e}")

        # Calculate streaks from daily counts
        sorted_dates = sorted(daily_counts.keys())
        longest_streak = 0
        current_streak = 0
        prev_date = None

        for date_str in sorted_dates:
            if daily_counts[date_str] > 0:
                from datetime import datetime, timedelta

                current_date = datetime.strptime(date_str, "%Y-%m-%d")
                if prev_date and (current_date - prev_date).days == 1:
                    current_streak += 1
                else:
                    current_streak = 1
                longest_streak = max(longest_streak, current_streak)
                prev_date = current_date

        weeks = max(len(set(d[:7] for d in daily_counts.keys())), 1)

        return ContributionData(
            total_contributions=push_events,
            contribution_calendar=[],  # Not available without GraphQL
            longest_streak=longest_streak,
            current_streak=current_streak,
            avg_contributions_per_week=round(push_events / max(weeks, 1), 1),
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _calculate_streaks(days: list[dict]) -> tuple[int, int]:
        """Calculate longest and current contribution streaks from calendar days."""
        if not days:
            return 0, 0

        longest = 0
        current = 0

        for day in days:
            if day.get("contributionCount", 0) > 0:
                current += 1
                longest = max(longest, current)
            else:
                current = 0

        # Current streak: count backwards from the end
        current_streak = 0
        for day in reversed(days):
            if day.get("contributionCount", 0) > 0:
                current_streak += 1
            else:
                break

        return longest, current_streak

    @staticmethod
    def extract_username_from_url(url: str) -> Optional[str]:
        """Extract GitHub username from various URL formats."""
        url = url.strip().rstrip("/")
        patterns = [
            r"https?://github\.com/([a-zA-Z0-9\-]+)/?$",
            r"https?://github\.com/([a-zA-Z0-9\-]+)/.*",
            r"^([a-zA-Z0-9\-]+)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        return None
