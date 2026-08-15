"""Prediction table — every prediction request and result."""

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
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Category, Gender, QuotaType, RecommendationStatus
from app.infrastructure.db.models._base import Base, TimestampMixin


class PredictionModel(Base, TimestampMixin):
    """Prediction requests and their results — core prediction audit table."""

    __tablename__ = "predictions"
    __table_args__ = (
        Index("ix_predictions_user_created", "user_id", "created_at"),
        Index("ix_predictions_session", "session_id"),
        Index("ix_predictions_engine_version", "engine_name", "engine_version"),
        UniqueConstraint(
            "user_id",
            "session_id",
            "counselling_year",
            "engine_name",
            "engine_version",
            name="uq_predictions_user_session_year_engine",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Candidate profile snapshot at prediction time
    air: Mapped[int] = mapped_column(Integer, nullable=False)
    marks: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="category", native_enum=False, length=32, validate_strings=True),
        nullable=False,
    )
    domicile_state_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("states.id", ondelete="SET NULL"), nullable=True
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, name="gender", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    is_pwd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_minority: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quota_type: Mapped[QuotaType] = mapped_column(
        Enum(QuotaType, name="quota_type", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    budget_inr: Mapped[int | None] = mapped_column(Numeric(12, 2), nullable=True)
    preferred_states: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Counselling context
    counselling_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    target_round: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # Engine provenance
    engine_name: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True
    )

    # Results summary
    total_colleges_evaluated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_recommendations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_probability: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    prediction_status: Mapped[RecommendationStatus] = mapped_column(
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

    # Metadata
    request_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    response_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PredictionModel user={self.user_id} "
            f"year={self.counselling_year} engine={self.engine_name}>"
        )
