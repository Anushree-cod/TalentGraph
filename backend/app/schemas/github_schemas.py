"""
Pydantic models for request/response schemas.
Defines the data structures used throughout the application.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
import re


# ─── Request Models ───────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""
    github_url: str = Field(
        ...,
        description="GitHub profile URL (e.g., https://github.com/username)",
        examples=["https://github.com/torvalds"]
    )
    job_description: Optional[str] = Field(
        default=None,
        description="Job description to match against the candidate's profile"
    )

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Extract and validate GitHub username from URL."""
        v = v.strip().rstrip("/")
        # Support both full URLs and plain usernames
        patterns = [
            r"https?://github\.com/([a-zA-Z0-9\-]+)/?$",
            r"^([a-zA-Z0-9\-]+)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, v)
            if match:
                return v
        raise ValueError(
            "Invalid GitHub URL. Expected format: https://github.com/username or just username"
        )

    def get_username(self) -> str:
        """Extract username from the GitHub URL."""
        url = self.github_url.strip().rstrip("/")
        match = re.match(r"https?://github\.com/([a-zA-Z0-9\-]+)", url)
        if match:
            return match.group(1)
        return url  # Assume it's already a username


class MatchRequest(BaseModel):
    """Request body for matching existing profile data against a new JD."""
    username: str
    job_description: str


# ─── GitHub Data Models ───────────────────────────────────────────────────────

class GitHubProfile(BaseModel):
    """Core GitHub user profile data."""
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    email: Optional[str] = None
    twitter_username: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: str = ""
    followers: int = 0
    following: int = 0
    public_repos: int = 0
    public_gists: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    hireable: Optional[bool] = None


class RepoDetail(BaseModel):
    """Detailed information about a single repository."""
    name: str
    full_name: str = ""
    description: Optional[str] = None
    html_url: str = ""
    language: Optional[str] = None
    languages: dict[str, int] = Field(default_factory=dict)  # language -> bytes
    topics: list[str] = Field(default_factory=list)
    stars: int = Field(default=0, alias="stargazers_count")
    forks: int = Field(default=0, alias="forks_count")
    watchers: int = Field(default=0, alias="watchers_count")
    open_issues: int = Field(default=0, alias="open_issues_count")
    size: int = 0  # KB
    is_fork: bool = Field(default=False, alias="fork")
    is_archived: bool = Field(default=False, alias="archived")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    default_branch: str = "main"
    has_wiki: bool = False
    has_pages: bool = False
    license_name: Optional[str] = None
    readme_excerpt: Optional[str] = None
    commit_count: int = 0

    model_config = {"populate_by_name": True}


class LanguageStat(BaseModel):
    """Aggregated language statistics across all repos."""
    language: str
    total_bytes: int
    percentage: float
    repo_count: int  # How many repos use this language


class ContributionData(BaseModel):
    """Contribution calendar and streak data."""
    total_contributions: int = 0
    contribution_calendar: list[dict[str, Any]] = Field(default_factory=list)
    longest_streak: int = 0
    current_streak: int = 0
    avg_contributions_per_week: float = 0.0


# ─── Analysis & Scoring Models ───────────────────────────────────────────────

class RepoScore(BaseModel):
    """Quality score for a single repository."""
    repo_name: str
    score: float
    breakdown: dict[str, float] = Field(default_factory=dict)


class ProfileScores(BaseModel):
    """Aggregated scoring across the entire profile."""
    overall_score: float = 0.0  # 0-100
    activity_score: float = 0.0  # 0-100
    quality_score: float = 0.0  # 0-100
    diversity_score: float = 0.0  # 0-100
    consistency_score: float = 0.0  # 0-100
    profile_completeness: float = 0.0  # 0-100
    top_repo_scores: list[RepoScore] = Field(default_factory=list)


class SkillMatch(BaseModel):
    """Individual skill match result."""
    skill: str
    found: bool
    evidence: list[str] = Field(default_factory=list)  # Repo names demonstrating this skill


class AIAnalysis(BaseModel):
    """AI-generated analysis of candidate vs job description."""
    match_percentage: float = 0.0
    matching_skills: list[SkillMatch] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    relevant_projects: list[dict[str, str]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str = ""  # Strong Match / Good Match / Partial Match / Weak Match
    summary: str = ""
    analysis_method: str = "keyword"  # "gemini" or "keyword"


# ─── Visualization Models ────────────────────────────────────────────────────

class Visualizations(BaseModel):
    """Base64-encoded chart images."""
    language_chart: Optional[str] = None
    contribution_heatmap: Optional[str] = None
    stars_chart: Optional[str] = None
    activity_timeline: Optional[str] = None
    skill_radar: Optional[str] = None


# ─── Full Analysis Response ──────────────────────────────────────────────────

class ProfileAnalysis(BaseModel):
    """Complete analysis response — the main output of the system."""
    profile: GitHubProfile
    repositories: list[RepoDetail] = Field(default_factory=list)
    language_stats: list[LanguageStat] = Field(default_factory=list)
    contributions: ContributionData = Field(default_factory=ContributionData)
    scores: ProfileScores = Field(default_factory=ProfileScores)
    extracted_skills: list[str] = Field(default_factory=list)
    ai_analysis: Optional[AIAnalysis] = None
    visualizations: Visualizations = Field(default_factory=Visualizations)
    metadata: dict[str, Any] = Field(default_factory=dict)  # timing, rate limits, etc.
