"""State master table — Indian states and union territories for NEET counselling."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class StateModel(Base, TimestampMixin):
    """Master list of Indian states and UTs (NEET counselling jurisdictions)."""

    __tablename__ = "states"
    __table_args__ = (
        UniqueConstraint("code", name="uq_states_code"),
        UniqueConstraint("name", name="uq_states_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_ut: Mapped[bool] = mapped_column(default=False, nullable=False)
    neet_counselling_authority: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<StateModel code={self.code!r} name={self.name!r} ut={self.is_ut}>"
