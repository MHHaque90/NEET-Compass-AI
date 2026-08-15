"""Seat matrix table — sanctioned seat counts per college, course, quota, category, year."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Category, Course, QuotaType
from app.infrastructure.db.models._base import Base, TimestampMixin


class SeatMatrixModel(Base, TimestampMixin):
    """Sanctioned seat matrix per college/course/quota/category/year.

    This is the authoritative source for how many seats exist in each cohort.
    Historical seat matrix entries are immutable once published.
    """

    __tablename__ = "seat_matrix"
    __table_args__ = (
        Index("ix_seat_matrix_college_year", "college_id", "academic_year"),
        Index("ix_seat_matrix_cohort", "quota_type", "category", "academic_year"),
        UniqueConstraint(
            "college_id",
            "course",
            "quota_type",
            "category",
            "academic_year",
            name="uq_seat_matrix_college_course_quota_cat_year",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    college_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    course: Mapped[Course] = mapped_column(
        Enum(Course, name="course", native_enum=False, length=10, validate_strings=True),
        nullable=False,
    )
    quota_type: Mapped[QuotaType] = mapped_column(
        Enum(QuotaType, name="quota_type", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="category", native_enum=False, length=32, validate_strings=True),
        nullable=False,
    )
    academic_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    notification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    seats_sanctioned: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_filled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<SeatMatrixModel college={self.college_id} year={self.academic_year} "
            f"quota={self.quota_type} cat={self.category} seats={self.seats_sanctioned}>"
        )
