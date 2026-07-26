from __future__ import annotations
"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM — routed through the local `claude` CLI (Claude.ai subscription usage,
    # not Anthropic API credits). Requires `claude login` to have been run.
    llm_model: str = "claude-sonnet-4-20250514"

    # Search & Trend APIs
    serpapi_key: str = ""
    youtube_api_key: str = ""
    github_token: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    twitter_bearer_token: str = ""

    # Database
    database_url: str = "sqlite:///./tutorial_hunter.db"
    redis_url: str = "redis://localhost:6379"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

    # App
    crawl_interval_hours: int = 6
    max_results_per_source: int = 50
    quality_threshold: float = 60.0
    log_level: str = "INFO"

    # Scoring weights
    weight_relevance: float = Field(default=0.25)
    weight_freshness: float = Field(default=0.20)
    weight_engagement: float = Field(default=0.20)
    weight_depth: float = Field(default=0.25)
    weight_credibility: float = Field(default=0.10)


@lru_cache
def get_settings() -> Settings:
    return Settings()
