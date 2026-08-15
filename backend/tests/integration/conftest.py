"""Integration test fixtures for database tests.

PostgreSQL integration tests MUST use PostgreSQL — no silent SQLite fallback.
If PostgreSQL is unavailable or authentication fails, the test session
must raise/exit clearly rather than falling back to SQLite (which would
mask the failure).
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def pg_engine(tmp_path_factory: pytest.TempPathFactory) -> Engine:
    """Create a PostgreSQL test engine.

    Raises an explicit error if PostgreSQL is unavailable or authentication
    fails — never falls back to SQLite in-memory, which would mask the
    failure.
    """
    url = "postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass"
    try:
        engine = create_engine(url)
        # Verify connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except SQLAlchemyError as exc:
        raise RuntimeError(
            f"PostgreSQL integration unavailable: {exc}"
        ) from exc


@pytest.fixture(scope="function")
def db_session(pg_engine: Engine):
    """Provide a database session for testing.

    Creates all tables, provides a session, and cleans up after.
    """
    from sqlalchemy.orm import sessionmaker

    from app.core.database import Base
    from app.infrastructure import db as _models  # noqa: F401 (registers models)

    # Create tables
    Base.metadata.create_all(pg_engine)
    SessionLocal = sessionmaker(bind=pg_engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()
    # Drop all tables
    Base.metadata.drop_all(pg_engine)
