"""Source file table — tracks individual files from data sources."""

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
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class SourceFileStatus(StrEnum):
    """Source file processing status."""

    DISCOVERED = "DISCOVERED"
    DOWNLOADED = "DOWNLOADED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    LOADED = "LOADED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class SourceFileModel(Base, TimestampMixin):
    """Individual files from data sources — tracks download, validation, and load status."""

    __tablename__ = "source_files"
    __table_args__ = (
        Index("ix_source_files_source_status", "data_source_id", "status"),
        Index("ix_source_files_academic_year", "academic_year"),
        Index("ix_source_files_checksum", "checksum_sha256"),
        UniqueConstraint(
            "data_source_id",
            "academic_year",
            "file_name",
            "file_version",
            name="uq_source_files_source_year_name_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_version: Mapped[str] = mapped_column(String(50), default="1", nullable=False)
    academic_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    counselling_round: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # File metadata
    remote_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_names: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Processing status
    status: Mapped[SourceFileStatus] = mapped_column(
        Enum(
            SourceFileStatus,
            name="source_file_status",
            native_enum=False,
            length=20,
            validate_strings=True,
        ),
        default=SourceFileStatus.DISCOVERED,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    validation_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    loaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Versioning
    source_version: Mapped[str] = mapped_column(String(50), nullable=True)
    etl_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SourceFileModel source={self.data_source_id} "
            f"file={self.file_name} year={self.academic_year}>"
        )
