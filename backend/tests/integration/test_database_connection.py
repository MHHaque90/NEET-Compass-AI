"""Database connection tests."""

from __future__ import annotations

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration


class TestDatabaseConnection:
    """Tests for database connectivity and configuration."""

    def test_database_url_is_configured(self):
        """DATABASE_URL should be properly configured."""
        from app.core.config import get_settings

        settings = get_settings()
        assert settings.database_url is not None
        assert "postgresql" in settings.database_url

    def test_engine_creation_succeeds(self):
        """Database engine should be created successfully."""
        from app.core.database import engine

        assert engine is not None
        assert engine.pool is not None

    def test_engine_pool_settings(self):
        """Engine should have correct pool settings."""
        from app.core.config import get_settings
        from app.core.database import engine

        settings = get_settings()
        assert engine.pool.size() == settings.database_pool_size
        assert engine.pool._max_overflow == settings.database_max_overflow

    def test_session_factory_creates_sessions(self):
        """SessionLocal should create valid sessions."""
        from sqlalchemy.orm import Session

        from app.core.database import SessionLocal

        session = SessionLocal()
        assert isinstance(session, Session)
        session.close()

    def test_get_db_dependency_returns_session(self):
        """get_db should yield a valid session."""
        from sqlalchemy.orm import Session

        from app.core.database import get_db

        session = next(get_db())
        assert isinstance(session, Session)
        session.close()

    def test_database_is_postgresql(self):
        """Database should be PostgreSQL."""
        from app.core.config import get_settings

        settings = get_settings()
        assert "postgresql" in settings.database_url

    def test_database_echo_setting(self):
        """Database echo should be configurable."""
        from app.core.config import get_settings

        settings = get_settings()
        assert hasattr(settings, "database_echo")
        assert isinstance(settings.database_echo, bool)

    def test_connection_with_valid_credentials(self, pg_engine):
        """Database connection should succeed with valid credentials."""
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_connection_with_invalid_credentials(self):
        """Database connection should fail with invalid credentials."""
        from sqlalchemy import create_engine
        from sqlalchemy.exc import OperationalError

        engine = create_engine(
            "postgresql+psycopg://invalid:invalid@localhost:9999/invalid",
            pool_timeout=2,
        )
        with pytest.raises(OperationalError), engine.connect() as conn:
            conn.execute(text("SELECT 1"))
