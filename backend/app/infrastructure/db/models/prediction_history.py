"""Prediction history table — individual college recommendations per prediction."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Course, RecommendationStatus
from app.infrastructure.db.models._base import Base, TimestampMixin


class PredictionHistoryModel(Base, TimestampMixin):
    """Individual college recommendation within a prediction — granular audit trail."""

    __tablename__ = "prediction_history"
    __table_args__ = (
        Index("ix_prediction_history_prediction", "prediction_id"),
        Index("ix_prediction_history_college", "college_id"),
        Index("ix_prediction_history_rank", "prediction_id", "probability"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False
    )
    college_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True
    )
    course: Mapped[Course] = mapped_column(
        Enum(Course, name="course", native_enum=False, length=10, validate_strings=True),
        nullable=False,
    )

    # Prediction output
    probability: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    expected_round: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(
            RecommendationStatus,
            name="recommendation_status",
            native_enum=False,
            length=16,
            validate_strings=True,
        ),
        default=RecommendationStatus.PENDING,
        nullable=False,
    )

    # Explainability
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    strategy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    choice_filling_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Quota/category context for this recommendation
    quota_type: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    is_pwd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Historical reference
    historical_closing_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    historical_closing_marks: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    seats_available: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Feature attribution (for ML models)
    feature_contributions: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PredictionHistoryModel prediction={self.prediction_id} "
            f"college={self.college_id} prob={self.probability} order={self.choice_filling_order}>"
        )
