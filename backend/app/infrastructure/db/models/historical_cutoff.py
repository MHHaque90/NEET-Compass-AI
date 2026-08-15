"""Historical cutoffs table — derived historical cutoff facts for analytics.

This table represents normalized historical cutoff information, distinct from
the raw allotments table. It provides the prediction engine with properly-
referenced cutoff features via foreign keys to lookup tables.

Each row is a derived cutoff observation for a college/course/quota/category/round
combination, sourced from one or more allotment records.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class HistoricalCutoffModel(Base, TimestampMixin):
    """Derived historical cutoff facts for prediction engine analytics."""

    __tablename__ = "historical_cutoffs"
    __table_args__ = (
        Index(
            "ix_historical_cutoffs_college_year",
            "college_id",
            "year",
        ),
        Index(
            "ix_historical_cutoffs_course_round",
            "course_id",
            "round_id",
        ),
        Index(
            "ix_historical_cutoffs_quota_category",
            "quota_id",
            "category_id",
        ),
        UniqueConstraint(
            "college_id",
            "course_id",
            "year",
            "round_id",
            "quota_id",
            "category_id",
            name="uq_historical_cutoffs_college_course_year_round_quota_cat",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    college_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    round_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("rounds.id", ondelete="SET NULL"), nullable=True
    )
    quota_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("quotas.id", ondelete="SET NULL"), nullable=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    opening_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    closing_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    opening_marks: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    closing_marks: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<HistoricalCutoffModel college={self.college_id} "
            f"year={self.year} round={self.round_id} "
            f"opening_rank={self.opening_rank}>"
        )
