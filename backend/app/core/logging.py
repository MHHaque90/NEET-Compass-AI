"""Structured logging configuration.

Logs are emitted as JSON lines in production (easy to ship to Datadog,
CloudWatch, Loki, etc.) and as human-readable text during local development.
Loggers are created per-module (`logging.getLogger(__name__)`) and the root
configuration below is installed once at application startup.
"""

from __future__ import annotations

import logging
import sys
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any
from app.core.config import Settings


class JsonFormatter(logging.Formatter):
    """Format log records as JSON lines."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string."""
        record_dict: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # Add extra fields from the record's __dict__, excluding internal attrs
        for key in dir(record):
            if key.islower() and not key.startswith("_") and key not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "stack_level",
            ):
                try:
                    val = getattr(record, key)
                    if isinstance(val, (str, int, float, bool, type(None))):
                        record_dict[key] = val
                except Exception:
                    pass
        return json.dumps(record_dict, default=str)


def _build_formatter(settings: Settings) -> logging.Formatter:
    if settings.is_testing:
        return logging.Formatter("%(levelname)s %(name)s: %(message)s")
    if settings.is_production:
        return JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
        )
    return logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")


def configure_logging(settings: Settings) -> None:
    """Install the process-wide logging configuration."""
    root = logging.getLogger()
    root.setLevel(settings.app_log_level)

    # Idempotent: avoid duplicate handlers when called more than once.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(_build_formatter(settings))
    root.addHandler(stream)

    # Third-party noise reduction.
    logging.getLogger("uvicorn.access").setLevel(
        logging.WARNING if settings.is_production else logging.INFO
    )
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database_echo else logging.WARNING
    )