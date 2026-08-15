"""Log table — structured application logs for audit and debugging."""

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
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base


class LogLevel(StrEnum):
    """Standard log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogModel(Base):
    """Structured application logs — append-only, no updates, no deletes.

    Uses TimestampMixin for created_at only. No updated_at for logs.
    Partitioned by date in production (not shown here).
    """

    __tablename__ = "logs"
    __table_args__ = (
        Index("ix_logs_level_created", "level", "created_at"),
        Index("ix_logs_logger_created", "logger_name", "created_at"),
        Index("ix_logs_trace", "trace_id"),
        Index("ix_logs_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False, index=True
    )
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, name="log_level", native_enum=False, length=10, validate_strings=True),
        nullable=False,
    )
    logger_name: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(2000), nullable=False)

    # Structured context
    trace_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    span_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    request_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Exception details
    exception_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    exception_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Additional structured data
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"<LogModel level={self.level} logger={self.logger_name} trace={self.trace_id}>"
