"""ETL run table — tracks every ETL pipeline execution."""

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
    SmallInteger,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class ETLRunStatus(StrEnum):
    """ETL run status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"


class ETLRunType(StrEnum):
    """ETL run type."""

    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    BACKFILL = "BACKFILL"
    REPROCESS = "REPROCESS"
    VALIDATION = "VALIDATION"


class ETLRunModel(Base, TimestampMixin):
    """ETL pipeline execution runs — complete audit trail."""

    __tablename__ = "etl_runs"
    __table_args__ = (
        Index("ix_etl_runs_source_status", "data_source_id", "status"),
        Index("ix_etl_runs_started", "started_at"),
        Index("ix_etl_runs_pipeline", "pipeline_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    data_source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True
    )
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
    )
    pipeline_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    run_type: Mapped[ETLRunType] = mapped_column(
        Enum(ETLRunType, name="etl_run_type", native_enum=False, length=20, validate_strings=True),
        default=ETLRunType.INCREMENTAL,
        nullable=False,
    )
    status: Mapped[ETLRunStatus] = mapped_column(
        Enum(
            ETLRunStatus, name="etl_run_status", native_enum=False, length=20, validate_strings=True
        ),
        default=ETLRunStatus.PENDING,
        nullable=False,
    )

    # Configuration
    config_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    academic_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, index=True)
    counselling_round: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Progress tracking
    total_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_files: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    loaded_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    error_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Data quality metrics
    quality_score: Mapped[float | None] = mapped_column(nullable=True)
    validation_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validation_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Versioning
    etl_version: Mapped[str] = mapped_column(String(50), nullable=False)
    code_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Trigger info
    triggered_by: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # user_id, scheduler, api
    trigger_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # manual, scheduled, webhook

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ETLRunModel pipeline={self.pipeline_name} "
            f"status={self.status} rows={self.loaded_rows}>"
        )
