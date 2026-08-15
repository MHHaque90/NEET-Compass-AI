"""Logging configuration behaviour."""

from __future__ import annotations

import logging

from app.core.config import AppEnv, Settings
from app.core.logging import configure_logging


def test_configure_logging_is_idempotent() -> None:
    root = logging.getLogger()
    configure_logging(Settings(_env_file=None, app_env=AppEnv.DEVELOPMENT))
    handler_count_after_first = len(root.handlers)
    assert handler_count_after_first >= 1

    configure_logging(Settings(_env_file=None, app_env=AppEnv.DEVELOPMENT))
    assert len(root.handlers) == handler_count_after_first
