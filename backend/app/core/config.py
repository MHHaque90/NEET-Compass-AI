"""Application settings.

All runtime configuration is environment-driven via pydantic-settings.
Every value can be overridden with an environment variable or the `.env`
file. The `Settings` instance is a process-wide singleton created once at
import time by the composition root (`app.core.config`), then injected into
every component that needs it — nothing ever reads `os.environ` directly.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass"


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────
    app_name: str = "NEET Compass AI"
    app_version: str = "0.1.0"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    app_debug: bool = False
    app_log_level: str = "INFO"

    # ── Database ───────────────────────────────────────────────────────────
    database_url: str = DEFAULT_DATABASE_URL
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_echo: bool = False

    # ── Security ───────────────────────────────────────────────────────────
    secret_key: str = "dev-only-secret"
    access_token_expire_minutes: int = 60

    # ── Cache ──────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300

    # ── ETL ────────────────────────────────────────────────────────────────
    etl_raw_root: str = "./data/raw"
    etl_processed_root: str = "./data/processed"
    etl_export_root: str = "./data/exports"
    etl_batch_size: int = 1000

    # ── ML ─────────────────────────────────────────────────────────────────
    # `unavailable` is the safe default: it refuses to fabricate scores.
    # Register engines in app.application.container.Container.
    ml_recommendation_engine: str = "unavailable"
    ml_model_registry_path: str = "./data/cache/models"

    # ── CORS ───────────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.strip("[]").split(",") if origin.strip()]
        return value

    @field_validator("app_log_level")
    @classmethod
    def _upper_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def is_production(self) -> bool:
        return self.app_env == AppEnv.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self.app_env == AppEnv.TESTING


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton (cached)."""
    return Settings()
