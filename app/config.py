"""Application configuration settings using pydantic-settings."""

from functools import lru_cache
from typing import Any, Dict
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Agentic Web Research Engine.

    All properties can be overridden by environment variables or values in a .env file.
    No secrets or API keys are stored in source code.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(
        default="Agentic Web Research Engine",
        description="Public display name of the application.",
    )
    app_env: str = Field(
        default="development",
        description="Execution environment (e.g., development, production, test).",
    )
    search_provider: str = Field(
        default="duckduckgo",
        description="Default search discovery provider ('duckduckgo' or 'searxng').",
    )
    duckduckgo_url: str = Field(
        default="https://html.duckduckgo.com/html/",
        description="DuckDuckGo HTML search endpoint URL.",
    )
    database_path: str = Field(
        default="research.db",
        description="File path for the SQLite database.",
    )
    searxng_url: str = Field(
        default="http://localhost:8080",
        description="Base URL for the self-hosted SearXNG instance (optional).",
    )
    request_timeout: int = Field(
        default=15,
        ge=1,
        le=120,
        description="HTTP request timeout in seconds.",
    )
    max_sources: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of candidate web sources to fetch per query.",
    )
    max_search_rounds: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Maximum query expansion / search iterations.",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for local Ollama service.",
    )
    ollama_model: str = Field(
        default="qwen2.5:7b",
        description="Target local model identifier.",
    )
    user_agent: str = Field(
        default="AgenticWebResearchBot/0.1 (+https://github.com/example/agentic-web-research-engine)",
        description="User-Agent header sent when fetching web pages.",
    )
    max_content_size_bytes: int = Field(
        default=2 * 1024 * 1024,
        description="Maximum page response size to download (2 MB default).",
    )
    safe_crawl_delay_seconds: float = Field(
        default=0.5,
        description="Per-domain polite delay between requests.",
    )

    def get_public_config(self) -> Dict[str, Any]:
        """Return non-sensitive configuration values safe for public API exposure."""
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "search_provider": self.search_provider,
            "max_sources": self.max_sources,
            "max_search_rounds": self.max_search_rounds,
            "request_timeout": self.request_timeout,
            "ollama_model": self.ollama_model,
        }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
