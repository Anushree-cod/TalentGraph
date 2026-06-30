"""
GitHub analyzer configuration — settings for fetcher, processor, and AI modules.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub Personal Access Token for higher rate limits (5000/hr vs 60/hr)",
    )
    github_api_base: str = Field(
        default="https://api.github.com",
        description="GitHub REST API base URL",
    )
    github_graphql_url: str = Field(
        default="https://api.github.com/graphql",
        description="GitHub GraphQL API endpoint",
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for AI-powered analysis",
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model to use",
    )
    max_repos_to_analyze: int = Field(
        default=50,
        description="Maximum number of repos to fetch detailed data for",
    )
    max_readme_repos: int = Field(
        default=15,
        description="Max repos to fetch README content for (API-heavy)",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def github_headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TalentGraph-GitHub-Analyzer",
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    @property
    def github_graphql_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TalentGraph-GitHub-Analyzer",
        }
        if self.github_token:
            headers["Authorization"] = f"bearer {self.github_token}"
        return headers

    @property
    def is_authenticated(self) -> bool:
        return bool(self.github_token)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)


settings = Settings()
