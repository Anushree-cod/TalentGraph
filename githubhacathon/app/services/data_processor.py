"""
Data Processor — aggregates raw GitHub data into meaningful metrics and scores.

Takes raw fetched data and produces:
- Language distribution and statistics
- Activity and quality scores
- Skill extraction
- Profile completeness assessment
"""

import re
import logging
from datetime import datetime, timezone
from typing import Any

from app.models.schemas import (
    RepoDetail,
    GitHubProfile,
    ContributionData,
    LanguageStat,
    ProfileScores,
    RepoScore,
)

logger = logging.getLogger(__name__)

# ─── Known Technology Taxonomy ─────────────────────────────────────────────────
# Used for skill extraction from READMEs and topics

TECH_KEYWORDS = {
    # Languages
    "python", "javascript", "typescript", "java", "kotlin", "swift", "go",
    "golang", "rust", "c++", "cpp", "c#", "csharp", "ruby", "php", "scala",
    "r", "dart", "lua", "perl", "haskell", "elixir", "clojure", "julia",
    "objective-c", "shell", "bash", "powershell", "sql", "html", "css",

    # Frontend Frameworks
    "react", "reactjs", "react-native", "angular", "vue", "vuejs", "svelte",
    "nextjs", "next.js", "nuxt", "gatsby", "remix", "astro", "solid",

    # Backend Frameworks
    "django", "flask", "fastapi", "express", "expressjs", "nestjs", "spring",
    "spring-boot", "rails", "laravel", "gin", "fiber", "actix", "rocket",

    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "sqlite", "cassandra", "dynamodb", "firebase", "supabase", "neo4j",
    "mariadb", "couchdb", "influxdb",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google-cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "jenkins", "github-actions", "ci-cd", "cicd",
    "nginx", "apache", "serverless", "lambda", "cloudflare",

    # AI/ML
    "machine-learning", "deep-learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "sklearn", "pandas", "numpy", "opencv", "nlp",
    "computer-vision", "transformers", "huggingface", "langchain", "llm",
    "openai", "gpt", "bert", "generative-ai", "rag",

    # Mobile
    "android", "ios", "flutter", "react-native", "swiftui", "jetpack-compose",
    "xamarin", "ionic", "capacitor",

    # Tools & Misc
    "graphql", "rest", "api", "microservices", "websocket", "grpc",
    "rabbitmq", "kafka", "celery", "oauth", "jwt", "webpack", "vite",
    "tailwind", "tailwindcss", "bootstrap", "material-ui", "sass",
    "testing", "jest", "pytest", "cypress", "selenium",
    "git", "linux", "agile", "scrum",

    # Data
    "data-science", "data-engineering", "etl", "airflow", "spark",
    "hadoop", "tableau", "power-bi", "dbt",

    # Blockchain
    "blockchain", "solidity", "ethereum", "web3", "smart-contracts",
    "defi", "nft",
}


class DataProcessor:
    """Processes raw GitHub data into aggregated metrics and scores."""

    def process_languages(self, repos: list[RepoDetail]) -> list[LanguageStat]:
        """Aggregate language usage across all repositories."""
        lang_totals: dict[str, dict] = {}  # lang -> {bytes, repo_count}

        for repo in repos:
            if repo.languages:
                for lang, byte_count in repo.languages.items():
                    if lang not in lang_totals:
                        lang_totals[lang] = {"bytes": 0, "repo_count": 0}
                    lang_totals[lang]["bytes"] += byte_count
                    lang_totals[lang]["repo_count"] += 1
            elif repo.language:
                # Fallback: use primary language with estimated bytes from size
                lang = repo.language
                if lang not in lang_totals:
                    lang_totals[lang] = {"bytes": 0, "repo_count": 0}
                lang_totals[lang]["bytes"] += repo.size * 1024  # size is in KB
                lang_totals[lang]["repo_count"] += 1

        # Calculate percentages
        total_bytes = sum(v["bytes"] for v in lang_totals.values())
        if total_bytes == 0:
            return []

        stats = []
        for lang, data in lang_totals.items():
            percentage = round((data["bytes"] / total_bytes) * 100, 2)
            stats.append(
                LanguageStat(
                    language=lang,
                    total_bytes=data["bytes"],
                    percentage=percentage,
                    repo_count=data["repo_count"],
                )
            )

        # Sort by percentage descending
        stats.sort(key=lambda x: x.percentage, reverse=True)
        return stats

    def calculate_scores(
        self,
        profile: GitHubProfile,
        repos: list[RepoDetail],
        contributions: ContributionData | None,
        language_stats: list[LanguageStat],
    ) -> ProfileScores:
        """Calculate comprehensive profile scores."""

        # ── Individual repo scores ─────────────────────────────────────
        repo_scores = []
        for repo in repos:
            score = self._score_repo(repo)
            repo_scores.append(score)

        repo_scores.sort(key=lambda x: x.score, reverse=True)

        # ── Activity Score (0-100) ─────────────────────────────────────
        activity_score = self._calculate_activity_score(repos, contributions)

        # ── Quality Score (0-100) ──────────────────────────────────────
        quality_score = self._calculate_quality_score(repos, repo_scores)

        # ── Diversity Score (0-100) ────────────────────────────────────
        diversity_score = self._calculate_diversity_score(language_stats, repos)

        # ── Consistency Score (0-100) ──────────────────────────────────
        consistency_score = self._calculate_consistency_score(
            repos, contributions
        )

        # ── Profile Completeness (0-100) ──────────────────────────────
        completeness = self._calculate_profile_completeness(profile)

        # ── Overall Score (weighted) ──────────────────────────────────
        overall = (
            activity_score * 0.25
            + quality_score * 0.20
            + diversity_score * 0.10
            + consistency_score * 0.25
            + completeness * 0.10
            + min(len(repos), 30) / 30 * 10  # repo count bonus (up to 10pts)
        )
        overall = min(100, round(overall, 1))

        return ProfileScores(
            overall_score=overall,
            activity_score=round(activity_score, 1),
            quality_score=round(quality_score, 1),
            diversity_score=round(diversity_score, 1),
            consistency_score=round(consistency_score, 1),
            profile_completeness=round(completeness, 1),
            top_repo_scores=repo_scores[:10],
        )

    def extract_skills(
        self,
        repos: list[RepoDetail],
        language_stats: list[LanguageStat],
    ) -> list[str]:
        """Extract skills/technologies from repos (languages, topics, READMEs)."""
        skills: set[str] = set()

        # From languages
        for stat in language_stats:
            lang_lower = stat.language.lower()
            if lang_lower in TECH_KEYWORDS or stat.percentage >= 1.0:
                skills.add(stat.language)

        # From topics
        for repo in repos:
            for topic in repo.topics:
                topic_lower = topic.lower().replace(" ", "-")
                if topic_lower in TECH_KEYWORDS:
                    skills.add(topic)
                # Also add as-is if it looks like a tech term
                elif len(topic) > 1 and not topic.startswith("."):
                    skills.add(topic)

        # From READMEs (basic keyword extraction)
        for repo in repos:
            if repo.readme_excerpt:
                readme_lower = repo.readme_excerpt.lower()
                for tech in TECH_KEYWORDS:
                    # Match whole words only
                    pattern = r"\b" + re.escape(tech) + r"\b"
                    if re.search(pattern, readme_lower):
                        skills.add(tech)

        # Clean up and sort
        cleaned = set()
        for skill in skills:
            s = skill.strip().lower()
            if len(s) > 1:
                cleaned.add(s)

        return sorted(cleaned)

    # ═══════════════════════════════════════════════════════════════════════════
    # Private Scoring Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _score_repo(self, repo: RepoDetail) -> RepoScore:
        """Calculate a quality score for a single repository."""
        breakdown = {}

        # Stars (max 30 pts)
        breakdown["stars"] = min(repo.stars * 3, 30)

        # Forks (max 15 pts)
        breakdown["forks"] = min(repo.forks * 2, 15)

        # Has description (5 pts)
        breakdown["description"] = 5 if repo.description else 0

        # Has README (5 pts)
        breakdown["readme"] = 5 if repo.readme_excerpt else 0

        # Topics/tags (max 10 pts)
        breakdown["topics"] = min(len(repo.topics) * 2, 10)

        # Commit activity (max 15 pts)
        if repo.commit_count > 0:
            breakdown["commits"] = min(repo.commit_count * 0.5, 15)
        else:
            breakdown["commits"] = 0

        # Has license (5 pts)
        breakdown["license"] = 5 if repo.license_name else 0

        # Size (non-trivial project, max 5 pts)
        if repo.size > 100:  # > 100 KB
            breakdown["size"] = 5
        elif repo.size > 10:
            breakdown["size"] = 2
        else:
            breakdown["size"] = 0

        # Not a fork bonus (5 pts)
        breakdown["original"] = 5 if not repo.is_fork else 0

        # Recency bonus (max 5 pts)
        if repo.pushed_at:
            try:
                pushed = datetime.fromisoformat(
                    repo.pushed_at.replace("Z", "+00:00")
                )
                days_ago = (datetime.now(timezone.utc) - pushed).days
                if days_ago < 30:
                    breakdown["recency"] = 5
                elif days_ago < 90:
                    breakdown["recency"] = 3
                elif days_ago < 365:
                    breakdown["recency"] = 1
                else:
                    breakdown["recency"] = 0
            except Exception:
                breakdown["recency"] = 0
        else:
            breakdown["recency"] = 0

        total = sum(breakdown.values())

        return RepoScore(
            repo_name=repo.name,
            score=round(total, 1),
            breakdown={k: round(v, 1) for k, v in breakdown.items()},
        )

    def _calculate_activity_score(
        self,
        repos: list[RepoDetail],
        contributions: ContributionData | None,
    ) -> float:
        """Score based on contribution frequency, recency, and streaks."""
        score = 0.0

        if contributions:
            # Total contributions (max 30 pts)
            total = contributions.total_contributions
            if total > 1000:
                score += 30
            elif total > 500:
                score += 25
            elif total > 200:
                score += 20
            elif total > 50:
                score += 15
            elif total > 10:
                score += 8
            else:
                score += total * 0.5

            # Streak (max 20 pts)
            score += min(contributions.longest_streak * 0.5, 20)

            # Current streak (max 10 pts)
            score += min(contributions.current_streak * 1.0, 10)

            # Average per week (max 15 pts)
            avg = contributions.avg_contributions_per_week
            if avg > 20:
                score += 15
            elif avg > 10:
                score += 12
            elif avg > 5:
                score += 8
            else:
                score += avg * 1.5

        # Recent repo updates (max 25 pts)
        recent_repos = 0
        for repo in repos:
            if repo.pushed_at:
                try:
                    pushed = datetime.fromisoformat(
                        repo.pushed_at.replace("Z", "+00:00")
                    )
                    days_ago = (datetime.now(timezone.utc) - pushed).days
                    if days_ago < 90:
                        recent_repos += 1
                except Exception:
                    pass
        score += min(recent_repos * 2.5, 25)

        return min(100, score)

    def _calculate_quality_score(
        self,
        repos: list[RepoDetail],
        repo_scores: list[RepoScore],
    ) -> float:
        """Score based on code quality indicators across repos."""
        if not repos:
            return 0.0

        score = 0.0

        # Average repo score (max 40 pts)
        if repo_scores:
            avg_repo_score = sum(rs.score for rs in repo_scores) / len(
                repo_scores
            )
            score += min(avg_repo_score * 0.6, 40)

        # Total stars across repos (max 20 pts)
        total_stars = sum(r.stars for r in repos)
        if total_stars > 100:
            score += 20
        elif total_stars > 50:
            score += 15
        elif total_stars > 10:
            score += 10
        else:
            score += total_stars * 0.5

        # Repos with descriptions (max 15 pts)
        with_desc = sum(1 for r in repos if r.description)
        desc_ratio = with_desc / len(repos)
        score += desc_ratio * 15

        # Repos with topics (max 10 pts)
        with_topics = sum(1 for r in repos if r.topics)
        topics_ratio = with_topics / len(repos)
        score += topics_ratio * 10

        # Non-trivial repos (>100KB, max 15 pts)
        substantial = sum(1 for r in repos if r.size > 100)
        score += min(substantial * 3, 15)

        return min(100, score)

    def _calculate_diversity_score(
        self,
        language_stats: list[LanguageStat],
        repos: list[RepoDetail],
    ) -> float:
        """Score based on language and topic diversity."""
        score = 0.0

        # Number of languages (max 40 pts)
        num_langs = len(language_stats)
        if num_langs >= 8:
            score += 40
        elif num_langs >= 5:
            score += 30
        elif num_langs >= 3:
            score += 20
        else:
            score += num_langs * 7

        # Language distribution evenness (max 30 pts)
        # A more even distribution = higher score
        if language_stats and len(language_stats) > 1:
            top_pct = language_stats[0].percentage
            if top_pct < 40:
                score += 30  # Very balanced
            elif top_pct < 60:
                score += 20
            elif top_pct < 80:
                score += 10
            else:
                score += 5

        # Unique topics across repos (max 30 pts)
        all_topics: set[str] = set()
        for repo in repos:
            all_topics.update(repo.topics)
        topic_count = len(all_topics)
        score += min(topic_count * 2, 30)

        return min(100, score)

    def _calculate_consistency_score(
        self,
        repos: list[RepoDetail],
        contributions: ContributionData | None,
    ) -> float:
        """Score based on consistency of activity over time."""
        score = 0.0

        # Account age and activity spread
        if repos:
            dates = []
            for repo in repos:
                if repo.created_at:
                    try:
                        dt = datetime.fromisoformat(
                            repo.created_at.replace("Z", "+00:00")
                        )
                        dates.append(dt)
                    except Exception:
                        pass

            if dates:
                oldest = min(dates)
                newest = max(dates)
                span_days = (newest - oldest).days

                # Long history (max 30 pts)
                if span_days > 365 * 3:
                    score += 30
                elif span_days > 365 * 2:
                    score += 25
                elif span_days > 365:
                    score += 20
                elif span_days > 180:
                    score += 10
                else:
                    score += 5

                # Repos created across different years (max 25 pts)
                years = set(d.year for d in dates)
                score += min(len(years) * 5, 25)

        # Contribution consistency (max 25 pts)
        if contributions and contributions.contribution_calendar:
            weeks_with_activity = 0
            for week_data in contributions.contribution_calendar:
                days = week_data.get("days", [])
                if any(d.get("contributionCount", 0) > 0 for d in days):
                    weeks_with_activity += 1

            total_weeks = max(len(contributions.contribution_calendar), 1)
            activity_ratio = weeks_with_activity / total_weeks
            score += activity_ratio * 25

        # Streak bonus (max 20 pts)
        if contributions:
            score += min(contributions.longest_streak * 0.5, 20)

        return min(100, score)

    def _calculate_profile_completeness(
        self, profile: GitHubProfile
    ) -> float:
        """Score how complete the profile information is."""
        score = 0.0
        fields = {
            "name": 15,
            "bio": 20,
            "location": 10,
            "company": 10,
            "blog": 15,
            "email": 10,
            "twitter_username": 5,
            "hireable": 5,
            "avatar_url": 10,
        }

        for field, points in fields.items():
            value = getattr(profile, field, None)
            if value:
                score += points

        return min(100, score)
