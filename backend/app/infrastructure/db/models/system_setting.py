"""System settings table — key-value configuration with versioning."""

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
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class SettingType(StrEnum):
    """System setting value types."""

    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    LIST = "LIST"


class SettingScope(StrEnum):
    """System setting scope."""

    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"
    FEATURE_FLAG = "FEATURE_FLAG"


class SystemSettingModel(Base, TimestampMixin):
    """System configuration settings with versioning and audit trail."""

    __tablename__ = "system_settings"
    __table_args__ = (
        Index("ix_system_settings_scope_key", "scope", "key"),
        Index("ix_system_settings_feature", "feature_flag_id"),
        UniqueConstraint("scope", "key", "version", name="uq_system_settings_scope_key_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    scope: Mapped[SettingScope] = mapped_column(
        Enum(
            SettingScope, name="setting_scope", native_enum=False, length=20, validate_strings=True
        ),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False)  # Stored as JSON string
    value_type: Mapped[SettingType] = mapped_column(
        Enum(SettingType, name="setting_type", native_enum=False, length=10, validate_strings=True),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Feature flag linkage
    feature_flag_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("feature_flags.id", ondelete="SET NULL"), nullable=True
    )

    # Validation
    validation_rules: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    allowed_values: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<SystemSettingModel scope={self.scope} key={self.key} v={self.version}>"
