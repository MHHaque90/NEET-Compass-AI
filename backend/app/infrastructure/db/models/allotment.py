"""Historical allotment (cut-off) table — the analytic core.

Each row is one published allotment line from MCC/state cut-off releases.
Heavy read workload: queried by (college, quota, category, gender, pwd,
year) hot paths. Indexed accordingly.
"""

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
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Category, Course, Gender, QuotaType
from app.infrastructure.db.models._base import Base, TimestampMixin


class AllotmentModel(Base, TimestampMixin):
    __tablename__ = "allotments"
    __table_args__ = (
        Index("ix_allotments_college_year_round", "college_id", "counselling_year", "round_number"),
        Index(
            "ix_allotments_cohort", "quota_type", "category", "gender", "is_pwd", "counselling_year"
        ),
        UniqueConstraint(
            "college_id",
            "counselling_year",
            "round_number",
            "quota_type",
            "category",
            "gender",
            "is_pwd",
            name="uq_allotments_college_round_cohort",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    college_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    college_code: Mapped[str] = mapped_column(String(20), nullable=False)
    course: Mapped[Course] = mapped_column(
        Enum(Course, name="course", native_enum=False, length=10, validate_strings=True),
        nullable=False,
    )
    counselling_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    counselling_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    round_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_stray_round: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quota_type: Mapped[QuotaType] = mapped_column(
        Enum(QuotaType, name="quota_type", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="category", native_enum=False, length=32, validate_strings=True),
        nullable=False,
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, name="gender", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    is_pwd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    opening_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    closing_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    opening_marks: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    closing_marks: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    seats_offered: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<AllotmentModel college={self.college_code} year={self.counselling_year} "
            f"round={self.round_number} closing_rank={self.closing_rank}>"
        )
