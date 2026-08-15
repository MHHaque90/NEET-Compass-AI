"""Shared fixtures for feature flag tests."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from feature_flags.models import FlagDefinition


def build_definitions() -> dict[str, FlagDefinition]:
    """A small, representative flag catalogue used across tests."""
    return {
        "engines.rule": FlagDefinition(name="engines.rule", default=False),
        "engines.ml": FlagDefinition(name="engines.ml", default=True),
        "experimental.x": FlagDefinition(name="experimental.x", default=False),
    }


@pytest.fixture
def definitions() -> dict[str, FlagDefinition]:
    return build_definitions()


@pytest.fixture
def sqlite_engine() -> Engine:
    """In-memory SQLite engine with a single shared connection."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
