"""ETL error table — granular error tracking for ETL runs."""

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
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class ETLErrorSeverity(StrEnum):
    """ETL error severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ETLErrorStage(StrEnum):
    """ETL pipeline stage where error occurred."""

    EXTRACT = "EXTRACT"
    TRANSFORM = "TRANSFORM"
    VALIDATE = "VALIDATE"
    LOAD = "LOAD"
    POST_LOAD = "POST_LOAD"


class ETLErrorModel(Base, TimestampMixin):
    """Granular ETL errors for debugging and alerting."""

    __tablename__ = "etl_errors"
    __table_args__ = (
        Index("ix_etl_errors_run_severity", "etl_run_id", "severity"),
        Index("ix_etl_errors_stage", "stage"),
        Index("ix_etl_errors_code", "error_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    etl_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("etl_runs.id", ondelete="CASCADE"), nullable=False
    )
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
    )

    # Error classification
    stage: Mapped[ETLErrorStage] = mapped_column(
        Enum(
            ETLErrorStage,
            name="etl_error_stage",
            native_enum=False,
            length=20,
            validate_strings=True,
        ),
        nullable=False,
    )
    severity: Mapped[ETLErrorSeverity] = mapped_column(
        Enum(
            ETLErrorSeverity,
            name="etl_error_severity",
            native_enum=False,
            length=10,
            validate_strings=True,
        ),
        default=ETLErrorSeverity.ERROR,
        nullable=False,
    )
    error_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    error_message: Mapped[str] = mapped_column(String(2000), nullable=False)
    error_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Context
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expected_value: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Resolution
    is_resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Stack trace
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ETLErrorModel run={self.etl_run_id} "
            f"stage={self.stage} code={self.error_code} "
            f"severity={self.severity}>"
        )
