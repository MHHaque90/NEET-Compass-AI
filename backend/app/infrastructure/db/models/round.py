"""Round master table — counselling rounds for NEET."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class RoundModel(Base, TimestampMixin):
    """Master list of counselling rounds (Round 1-5, Stray, etc.)."""

    __tablename__ = "rounds"
    __table_args__ = (
        UniqueConstraint("code", name="uq_rounds_code"),
        UniqueConstraint("name", name="uq_rounds_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    round_number: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True)
    is_stray_round: Mapped[bool] = mapped_column(default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RoundModel code={self.code!r} "
            f"number={self.round_number} stray={self.is_stray_round}>"
        )
