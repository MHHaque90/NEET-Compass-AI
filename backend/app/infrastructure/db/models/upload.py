"""Upload table — tracks file uploads for ETL and user data."""

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
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class UploadStatus(StrEnum):
    """Upload processing status."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class UploadType(StrEnum):
    """Type of upload."""

    ETL_SOURCE = "ETL_SOURCE"
    USER_DATA = "USER_DATA"
    BULK_PREDICTION = "BULK_PREDICTION"
    FEEDBACK = "FEEDBACK"


class UploadModel(Base, TimestampMixin):
    """Tracks all file uploads for audit and reprocessing."""

    __tablename__ = "uploads"
    __table_args__ = (
        Index("ix_uploads_user", "user_id"),
        Index("ix_uploads_source_file", "source_file_id"),
        Index("ix_uploads_status_type", "status", "upload_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
    )
    upload_type: Mapped[UploadType] = mapped_column(
        Enum(UploadType, name="upload_type", native_enum=False, length=20, validate_strings=True),
        nullable=False,
    )
    status: Mapped[UploadStatus] = mapped_column(
        Enum(
            UploadStatus, name="upload_status", native_enum=False, length=16, validate_strings=True
        ),
        default=UploadStatus.PENDING,
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<UploadModel id={self.id} type={self.upload_type} status={self.status}>"
