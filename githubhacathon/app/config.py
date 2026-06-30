"""
Application configuration — loads settings from environment variables.
Supports both authenticated (GitHub PAT) and unauthenticated modes.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    # GitHub Configuration
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub Personal Access Token for higher rate limits (5000/hr vs 60/hr)"
    )
    github_api_base: str = Field(
        default="https://api.github.com",
        description="GitHub REST API base URL"
    )
    github_graphql_url: str = Field(
        default="https://api.github.com/graphql",
        description="GitHub GraphQL API endpoint"
    )

    # Gemini AI Configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for AI-powered analysis"
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model to use"
    )

    # Analysis Configuration
    max_repos_to_analyze: int = Field(
        default=50,
        description="Maximum number of repos to fetch detailed data for"
    )
    max_readme_repos: int = Field(
        default=15,
        description="Max repos to fetch README content for (API-heavy)"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=True)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def github_headers(self) -> dict:
        """Build GitHub API request headers. Works with or without token."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Recruiter-GitHub-Analyzer",
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    @property
    def github_graphql_headers(self) -> dict:
        """Build GitHub GraphQL API headers. Requires token for GraphQL."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Recruiter-GitHub-Analyzer",
        }
        if self.github_token:
            headers["Authorization"] = f"bearer {self.github_token}"
        return headers

    @property
    def is_authenticated(self) -> bool:
        """Check if a GitHub token is configured."""
        return bool(self.github_token)

    @property
    def has_gemini(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.gemini_api_key)


# Singleton settings instance
settings = Settings()
