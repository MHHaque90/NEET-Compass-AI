"""Feature flag table — feature flag definitions and state."""

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
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class FlagType(StrEnum):
    """Feature flag types."""

    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    JSON = "JSON"


class FlagSource(StrEnum):
    """Feature flag value sources (precedence order)."""

    ENV = "ENV"
    MEMORY = "MEMORY"
    DATABASE = "DATABASE"
    CONFIG_FILE = "CONFIG_FILE"
    DEFAULT = "DEFAULT"


class FeatureFlagModel(Base, TimestampMixin):
    """Feature flag definitions with multi-source value resolution."""

    __tablename__ = "feature_flags"
    __table_args__ = (
        Index("ix_feature_flags_enabled", "is_enabled"),
        Index("ix_feature_flags_type", "flag_type"),
        UniqueConstraint("key", name="uq_feature_flags_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    flag_type: Mapped[FlagType] = mapped_column(
        Enum(FlagType, name="flag_type", native_enum=False, length=10, validate_strings=True),
        default=FlagType.BOOLEAN,
        nullable=False,
    )

    # Default value (lowest precedence)
    default_value: Mapped[str] = mapped_column(nullable=False)
    default_value_parsed: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Current resolved value (cached for introspection)
    current_value: Mapped[str] = mapped_column(nullable=False)
    current_value_parsed: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    current_source: Mapped[FlagSource] = mapped_column(
        Enum(FlagSource, name="flag_source", native_enum=False, length=20, validate_strings=True),
        default=FlagSource.DEFAULT,
        nullable=False,
    )

    # Targeting rules
    targeting_rules: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Metadata
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Ownership
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    team: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_modified_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_modified_source: Mapped[FlagSource | None] = mapped_column(
        Enum(FlagSource, name="flag_source", native_enum=False, length=20, validate_strings=True),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<FeatureFlagModel key={self.key} "
            f"enabled={self.is_enabled} source={self.current_source}>"
        )
