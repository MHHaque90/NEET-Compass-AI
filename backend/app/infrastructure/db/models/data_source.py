"""Data source table — external data sources for ETL."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class DataSourceType(StrEnum):
    """Types of data sources."""

    MCC_OFFICIAL = "MCC_OFFICIAL"
    STATE_COUNSELLING = "STATE_COUNSELLING"
    COLLEGE_WEBSITE = "COLLEGE_WEBSITE"
    NMC_REGISTRY = "NMC_REGISTRY"
    USER_UPLOAD = "USER_UPLOAD"
    THIRD_PARTY_API = "THIRD_PARTY_API"
    MANUAL_ENTRY = "MANUAL_ENTRY"


class DataSourceStatus(StrEnum):
    """Data source status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class DataSourceModel(Base, TimestampMixin):
    """External data sources for ETL ingestion."""

    __tablename__ = "data_sources"
    __table_args__ = (
        Index("ix_data_sources_type_status", "source_type", "status"),
        UniqueConstraint("code", name="uq_data_sources_code"),
        UniqueConstraint("name", name="uq_data_sources_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[DataSourceType] = mapped_column(
        Enum(
            DataSourceType,
            name="data_source_type",
            native_enum=False,
            length=30,
            validate_strings=True,
        ),
        nullable=False,
    )
    status: Mapped[DataSourceStatus] = mapped_column(
        Enum(
            DataSourceStatus,
            name="data_source_status",
            native_enum=False,
            length=20,
            validate_strings=True,
        ),
        default=DataSourceStatus.ACTIVE,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    auth_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    schedule_cron: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    rate_limit_rpm: Mapped[int | None] = mapped_column(nullable=True)
    retry_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)

    # Quality tracking
    last_successful_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_failed_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consecutive_failures: Mapped[int] = mapped_column(default=0, nullable=False)
    success_rate: Mapped[float | None] = mapped_column(nullable=True)

    # Versioning
    schema_version: Mapped[str] = mapped_column(String(50), default="1.0", nullable=False)
    data_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<DataSourceModel code={self.code!r} type={self.source_type} status={self.status}>"
