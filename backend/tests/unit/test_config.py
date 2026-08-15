"""Settings parsing, environment override, and profile behaviour."""

from __future__ import annotations

from app.core.config import AppEnv, Settings


def test_defaults_when_no_env() -> None:
    settings = Settings(_env_file=None)
    assert settings.app_name == "NEET Compass AI"
    assert settings.app_env == AppEnv.DEVELOPMENT
    assert settings.is_production is False
    assert settings.is_testing is False
    assert settings.ml_recommendation_engine == "unavailable"


def test_environment_override() -> None:
    settings = Settings(_env_file=None, app_env="production", database_pool_size=20)
    assert settings.app_env == AppEnv.PRODUCTION
    assert settings.is_production is True
    assert settings.database_pool_size == 20


def test_cors_origins_accepts_json_string(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["http://a.example", "http://b.example"]')
    settings = Settings(_env_file=None)
    assert settings.cors_origins == ["http://a.example", "http://b.example"]


def test_log_level_is_upper_cased(monkeypatch) -> None:
    monkeypatch.setenv("APP_LOG_LEVEL", "debug")
    settings = Settings(_env_file=None)
    assert settings.app_log_level == "DEBUG"
