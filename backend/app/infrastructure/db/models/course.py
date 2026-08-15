"""Course master table — normalized reference for MBBS/BDS programmes."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class CourseModel(Base, TimestampMixin):
    """Master list of NEET counselling courses (MBBS, BDS, future additions)."""

    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("code", name="uq_courses_code"),
        UniqueConstraint("name", name="uq_courses_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_years: Mapped[int] = mapped_column(default=5, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Soft delete

    def __repr__(self) -> str:
        return f"<CourseModel code={self.code!r} name={self.name!r}>"
