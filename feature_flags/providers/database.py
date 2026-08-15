"""Database provider.

The dynamic source: flags toggled at runtime (via ops tooling) take effect
immediately on every instance without a redeploy. Backed by a small
``feature_flags`` table that this package owns and can create on demand.

Two degradation rules keep the flag system resilient:
- if the table/schema is missing, reads return ``None`` (fall through to the
  config file / defaults) and a warning is logged — the platform must not
  crash because a toggle table was not provisioned;
- if the database is unreachable, the same fall-through applies, so a DB
  outage can never lock features into an unknown state.

The schema is intentionally tiny and stable. Managed databases should apply
``feature_flags/schema.sql`` through the platform's migration tooling; local
dev and tests may call ``ensure_schema()`` to create it on demand.
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from feature_flags.models import FlagSource
from feature_flags.provider import FlagProvider

logger = logging.getLogger(__name__)


class _Base(DeclarativeBase):
    """Metadata owner for the feature flag table (isolated from the platform)."""


class FeatureFlagRecord(_Base):
    __tablename__ = "feature_flags"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class DatabaseFlagProvider(FlagProvider):
    """Reads and writes flag states in the ``feature_flags`` table."""

    source = FlagSource.DATABASE

    def __init__(self, engine: Engine, *, create_schema: bool = False) -> None:
        self._engine = engine
        if create_schema:
            self.ensure_schema()

    def ensure_schema(self) -> None:
        """Create the feature flag table if it does not exist (idempotent)."""
        _Base.metadata.create_all(self._engine)

    def get_enabled(self, name: str) -> bool | None:
        try:
            with Session(self._engine) as session:
                row = session.get(FeatureFlagRecord, name)
        except OperationalError:
            logger.warning("feature_flags table unavailable; falling through for %r", name)
            return None
        return row.enabled if row is not None else None

    def get_updated_at(self, name: str) -> datetime | None:
        """Return the row's ``updated_at``, or ``None`` when absent/unreadable."""
        try:
            with Session(self._engine) as session:
                row = session.get(FeatureFlagRecord, name)
        except OperationalError:
            logger.warning("feature_flags table unavailable; cannot read updated_at for %r", name)
            return None
        return row.updated_at if row is not None else None

    def set(
        self,
        name: str,
        enabled: bool,
        *,
        comment: str | None = None,
        commit: bool = True,
    ) -> None:
        """Upsert a flag state (dynamic runtime toggle)."""
        with Session(self._engine) as session:
            row = session.get(FeatureFlagRecord, name)
            if row is None:
                session.add(FeatureFlagRecord(name=name, enabled=enabled, comment=comment))
            else:
                row.enabled = enabled
                if comment is not None:
                    row.comment = comment
            if commit:
                session.commit()
