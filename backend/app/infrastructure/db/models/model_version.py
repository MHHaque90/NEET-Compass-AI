"""Model version table — ML model registry with versioning."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class ModelType(StrEnum):
    """ML model types."""

    RULE_BASED = "RULE_BASED"
    LOGISTIC_REGRESSION = "LOGISTIC_REGRESSION"
    GRADIENT_BOOSTING = "GRADIENT_BOOSTING"
    RANDOM_FOREST = "RANDOM_FOREST"
    NEURAL_NETWORK = "NEURAL_NETWORK"
    ENSEMBLE = "ENSEMBLE"
    LLM = "LLM"


class ModelStatus(StrEnum):
    """Model lifecycle status."""

    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"


class ModelVersionModel(Base, TimestampMixin):
    """ML model registry — tracks every model version with metrics and artifacts."""

    __tablename__ = "model_versions"
    __table_args__ = (
        Index("ix_model_versions_name_status", "model_name", "status"),
        Index("ix_model_versions_production", "is_production", "model_name"),
        UniqueConstraint("model_name", "version", name="uq_model_versions_name_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[ModelType] = mapped_column(
        Enum(ModelType, name="model_type", native_enum=False, length=30, validate_strings=True),
        nullable=False,
    )
    status: Mapped[ModelStatus] = mapped_column(
        Enum(ModelStatus, name="model_status", native_enum=False, length=20, validate_strings=True),
        default=ModelStatus.TRAINING,
        nullable=False,
    )
    is_production: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Training metadata
    training_data_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    training_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    training_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    training_metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Validation metrics
    validation_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    validation_data_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Production deployment
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deployed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deployment_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Artifacts
    model_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    artifact_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    feature_names: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    target_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Performance thresholds
    min_accuracy: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    min_precision: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    min_recall: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    max_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Lineage
    parent_model_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True
    )
    experiment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    run_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Tags and description
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    deprecated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deprecated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deprecation_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ModelVersionModel name={self.model_name} v={self.version} "
            f"status={self.status} prod={self.is_production}>"
        )
