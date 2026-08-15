"""Database engine and session management.

The module owns the SQLAlchemy `Engine` and `SessionFactory` singletons and
exposes them to the rest of the application through a `SessionLocal` factory
and a FastAPI-compatible `get_db` dependency. Application code never creates
engines — it receives an injected session.

The import chain is arranged so that ORM models are registered on the shared
`Base.metadata` before Alembic or app startup reads it:
    app.core.database -> app.infrastructure.db.models (side-effect import)
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_pre_ping=True,
    echo=settings.database_echo,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped session.

    The session is always closed, rolling back any uncommitted work so a
    failure in a handler can never leak a half-open transaction.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
