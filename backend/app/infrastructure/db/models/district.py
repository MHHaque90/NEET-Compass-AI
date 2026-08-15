"""District master table — districts within states for NEET counselling."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class DistrictModel(Base, TimestampMixin):
    """Master list of districts within states for granular counselling data."""

    __tablename__ = "districts"
    __table_args__ = (
        Index("ix_districts_state", "state_id"),
        UniqueConstraint("state_id", "code", name="uq_districts_state_code"),
        UniqueConstraint("state_id", "name", name="uq_districts_state_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    state_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("states.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<DistrictModel state={self.state_id} code={self.code!r} name={self.name!r}>"
