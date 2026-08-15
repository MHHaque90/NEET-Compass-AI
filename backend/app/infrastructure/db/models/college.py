"""College master table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import CollegeOwnership, Course, IndiaState
from app.infrastructure.db.models._base import Base, TimestampMixin

_STATE_ENUM = Enum(IndiaState, name="state", native_enum=False, length=40, validate_strings=True)
_COURSE_ENUM = Enum(Course, name="course", native_enum=False, length=10, validate_strings=True)
_OWNERSHIP_ENUM = Enum(
    CollegeOwnership, name="college_ownership", native_enum=False, length=32, validate_strings=True
)


class CollegeModel(Base, TimestampMixin):
    __tablename__ = "colleges"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[IndiaState] = mapped_column(_STATE_ENUM, nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    course: Mapped[Course] = mapped_column(_COURSE_ENUM, nullable=False, index=True)
    ownership: Mapped[CollegeOwnership] = mapped_column(_OWNERSHIP_ENUM, nullable=False)
    annual_fee_inr: Mapped[int] = mapped_column(Numeric(12, 2), nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    aiq_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CollegeModel code={self.code!r} name={self.name!r}>"
