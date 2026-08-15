"""Database provider tests (in-memory SQLite)."""

from __future__ import annotations

from feature_flags.models import FlagSource
from feature_flags.providers.database import DatabaseFlagProvider


def test_reads_back_to_back(sqlite_engine) -> None:
    provider = DatabaseFlagProvider(sqlite_engine, create_schema=True)
    assert provider.get_enabled("engines.rule") is None  # empty table

    provider.set("engines.rule", True, comment="ops toggle")
    assert provider.get_enabled("engines.rule") is True

    provider.set("engines.rule", False)
    assert provider.get_enabled("engines.rule") is False


def test_ensure_schema_is_idempotent(sqlite_engine) -> None:
    provider = DatabaseFlagProvider(sqlite_engine)
    provider.ensure_schema()
    provider.ensure_schema()  # second call must not raise
    provider.set("engines.ml", True)


def test_missing_table_degrades_to_none(sqlite_engine) -> None:
    # create_schema=False and never call ensure_schema -> table does not exist.
    provider = DatabaseFlagProvider(sqlite_engine)
    assert provider.get_enabled("engines.rule") is None


def test_source_identity(sqlite_engine) -> None:
    assert DatabaseFlagProvider(sqlite_engine).source == FlagSource.DATABASE
