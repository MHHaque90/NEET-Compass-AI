"""Fee structure table — comprehensive fee breakdown per college, course, year, category."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import (
    Date,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Category, CollegeOwnership, Course
from app.infrastructure.db.models._base import Base, TimestampMixin


class FeeModel(Base, TimestampMixin):
    """Fee structure per college/course/ownership/category/year.

    Stores complete fee breakdown: tuition, hostel, security deposit, miscellaneous.
    Fee structures are published annually and are immutable once notified.
    """

    __tablename__ = "fees"
    __table_args__ = (
        Index("ix_fees_college_year", "college_id", "academic_year"),
        Index("ix_fees_ownership_year", "ownership", "academic_year"),
        UniqueConstraint(
            "college_id",
            "course",
            "category",
            "academic_year",
            name="uq_fees_college_course_cat_year",
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
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="category", native_enum=False, length=32, validate_strings=True),
        nullable=False,
    )
    ownership: Mapped[CollegeOwnership] = mapped_column(
        Enum(
            CollegeOwnership,
            name="college_ownership",
            native_enum=False,
            length=32,
            validate_strings=True,
        ),
        nullable=False,
    )
    academic_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    notification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    tuition_fee_inr: Mapped[int] = mapped_column(Numeric(12, 2), nullable=False)
    hostel_fee_inr: Mapped[int] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    security_deposit_inr: Mapped[int] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    miscellaneous_fee_inr: Mapped[int] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_annual_fee_inr: Mapped[int] = mapped_column(Numeric(12, 2), nullable=False)
    is_notified: Mapped[bool] = mapped_column(default=False, nullable=False)
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<FeeModel college={self.college_id} year={self.academic_year} "
            f"course={self.course} cat={self.category} total={self.total_annual_fee_inr}>"
        )
