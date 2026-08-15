"""Introspection service: full catalogue listing with per-source provenance."""

from __future__ import annotations

import pytest

from feature_flags.errors import UnknownFlagError
from feature_flags.introspection import FeatureFlagIntrospection
from feature_flags.models import FlagContext, FlagDefinition, FlagSource
from feature_flags.providers.config_file import ConfigFileFlagProvider
from feature_flags.providers.database import DatabaseFlagProvider
from feature_flags.providers.env_var import EnvVarFlagProvider
from feature_flags.providers.memory import MemoryFlagProvider
from feature_flags.service import FeatureFlagService


def _introspection(definitions, providers, *, strict: bool = False) -> FeatureFlagIntrospection:
    return FeatureFlagIntrospection(definitions=definitions, providers=providers, strict=strict)


def test_report_lists_every_flag_with_core_fields(definitions) -> None:
    report = _introspection(definitions, []).all_flags()

    assert [flag.name for flag in report.flags] == sorted(definitions)
    assert report.total == len(definitions)
    assert all(flag.description == "" for flag in report.flags)
    assert all(flag.source is FlagSource.DEFAULT for flag in report.flags)
    assert report.generated_at is not None


def test_default_value_priority_and_source_provider(definitions) -> None:
    flag = _introspection(definitions, []).introspect_flag("engines.rule")
    assert flag is not None
    assert flag.default_value is False
    assert flag.current_value is False
    assert flag.source is FlagSource.DEFAULT
    assert flag.source_provider == "definition-default"
    assert flag.priority == 4


def test_environment_override_reported(definitions) -> None:
    env = EnvVarFlagProvider(environ={"FF_ENGINES_RULE": "true"})
    flag = _introspection(definitions, [env]).introspect_flag("engines.rule")

    assert flag is not None
    assert flag.current_value is True
    assert flag.source is FlagSource.ENV
    assert flag.source_provider == "EnvVarFlagProvider"
    assert flag.priority == 0
    assert flag.environment_override is True
    assert flag.environment_var == "FF_ENGINES_RULE"


def test_database_override_and_last_modified(definitions, sqlite_engine) -> None:
    db = DatabaseFlagProvider(sqlite_engine, create_schema=True)
    db.set("engines.rule", True, comment="ops toggle")
    flag = _introspection(definitions, [db]).introspect_flag("engines.rule")

    assert flag is not None
    assert flag.database_override is True
    assert flag.source is FlagSource.DATABASE
    assert flag.source_provider == "DatabaseFlagProvider"
    assert flag.priority == 2
    assert flag.last_modified is not None


def test_config_override_reported(definitions, tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    path.write_text("overrides:\n  engines.rule: true\n", encoding="utf-8")
    flag = _introspection(definitions, [ConfigFileFlagProvider(path)]).introspect_flag(
        "engines.rule"
    )

    assert flag is not None
    assert flag.config_override is True
    assert flag.source is FlagSource.CONFIG_FILE
    assert flag.priority == 3


def test_memory_override_reported(definitions) -> None:
    memory = MemoryFlagProvider({"engines.rule": True})
    flag = _introspection(definitions, [memory]).introspect_flag("engines.rule")

    assert flag is not None
    assert flag.memory_override is True
    assert flag.source is FlagSource.MEMORY
    assert flag.priority == 1


def test_unset_sources_report_none(definitions) -> None:
    flag = _introspection(definitions, []).introspect_flag("engines.rule")

    assert flag is not None
    assert flag.environment_var is None
    assert flag.environment_override is None
    assert flag.database_override is None
    assert flag.config_override is None
    assert flag.memory_override is None
    assert flag.last_modified is None


def test_last_modified_requires_database_row(definitions, sqlite_engine) -> None:
    db = DatabaseFlagProvider(sqlite_engine)  # no schema created -> no rows
    flag = _introspection(definitions, [db]).introspect_flag("engines.rule")
    assert flag is not None
    assert flag.last_modified is None


def test_priority_follows_winning_source(definitions, sqlite_engine) -> None:
    db = DatabaseFlagProvider(sqlite_engine, create_schema=True)
    db.set("engines.rule", False)
    env = EnvVarFlagProvider(environ={"FF_ENGINES_RULE": "true"})
    flag = _introspection(definitions, [db, env]).introspect_flag("engines.rule")

    assert flag is not None
    assert flag.source is FlagSource.ENV
    assert flag.priority == 0
    assert flag.database_override is False  # lower source still reported


def test_unknown_flag_lenient_returns_none(definitions) -> None:
    assert _introspection(definitions, []).introspect_flag("no.such.flag") is None


def test_unknown_flag_strict_raises(definitions) -> None:
    with pytest.raises(UnknownFlagError):
        _introspection(definitions, [], strict=True).introspect_flag("no.such.flag")


def test_rules_narrow_current_value_with_context(definitions) -> None:
    flag = FlagDefinition(
        name="experimental.y",
        default=True,
        rules=[{"type": "environment", "environments": ["production"]}],
    )
    introspection = FeatureFlagIntrospection(definitions={"experimental.y": flag}, providers=[])

    on = introspection.introspect_flag("experimental.y", FlagContext(environment="production"))
    off = introspection.introspect_flag("experimental.y", FlagContext(environment="dev"))
    assert on is not None and on.current_value is True
    assert off is not None and off.current_value is False


def test_introspection_matches_evaluation_service(definitions) -> None:
    providers = [
        EnvVarFlagProvider(environ={"FF_ENGINES_ML": "false"}),
        MemoryFlagProvider({"engines.rule": True}),
    ]
    service = FeatureFlagService(definitions=definitions, providers=providers)
    introspection = FeatureFlagIntrospection(definitions=definitions, providers=providers)

    for flag in introspection.all_flags().flags:
        assert flag.current_value == service.is_enabled(flag.name)


def test_build_flag_introspection_convenience(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    path.write_text(
        "definitions:\n"
        "  engines.rule:\n"
        "    description: Rule engine\n"
        "    default: false\n",
        encoding="utf-8",
    )
    from feature_flags.container import build_flag_introspection

    introspection = build_flag_introspection(flags_path=path)
    report = introspection.all_flags()
    assert [flag.name for flag in report.flags] == ["engines.rule"]
    assert report.total == 1


def test_container_exposes_introspection_shared_with_service(tmp_path) -> None:
    from feature_flags.container import FeatureFlagContainer

    path = tmp_path / "flags.yaml"
    path.write_text(
        "definitions:\n"
        "  engines.rule:\n"
        "    default: false\n"
        "  engines.ml:\n"
        "    default: true\n",
        encoding="utf-8",
    )
    container = FeatureFlagContainer(flags_path=path)
    report = container.introspection().all_flags()

    assert [flag.name for flag in report.flags] == sorted(container.service.definitions)
    by_name = {flag.name: flag for flag in report.flags}
    assert by_name["engines.ml"].current_value is True
    assert by_name["engines.rule"].current_value is False
