"""Precedence: the provider chain resolves in declared source order."""

from __future__ import annotations

from feature_flags.models import FlagSource
from feature_flags.providers.config_file import ConfigFileFlagProvider
from feature_flags.providers.database import DatabaseFlagProvider
from feature_flags.providers.env_var import EnvVarFlagProvider
from feature_flags.providers.memory import MemoryFlagProvider
from feature_flags.service import FeatureFlagService


def _service(
    definitions,
    providers,
) -> FeatureFlagService:
    return FeatureFlagService(definitions=definitions, providers=providers)


def _env() -> EnvVarFlagProvider:
    return EnvVarFlagProvider(environ={"FF_ENGINES_ML": "true"})


def _memory() -> MemoryFlagProvider:
    return MemoryFlagProvider({"engines.ml": True})


def test_default_when_no_provider_owns_flag(definitions) -> None:
    service = _service(definitions, [])
    state = service.get_state("engines.rule")
    assert state.enabled is False  # definition default
    assert state.source is FlagSource.DEFAULT


def test_config_file_beats_default(definitions, tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    path.write_text("overrides:\n  engines.rule: true\n", encoding="utf-8")
    service = _service(definitions, [ConfigFileFlagProvider(path)])
    state = service.get_state("engines.rule")
    assert state.enabled is True
    assert state.source is FlagSource.CONFIG_FILE


def test_database_beats_config_file(definitions, sqlite_engine, tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    path.write_text("overrides:\n  engines.rule: true\n", encoding="utf-8")
    db = DatabaseFlagProvider(sqlite_engine, create_schema=True)
    db.set("engines.rule", False)

    # Registered after the config provider, yet must still win.
    service = _service(definitions, [ConfigFileFlagProvider(path), db])
    state = service.get_state("engines.rule")
    assert state.enabled is False
    assert state.source is FlagSource.DATABASE


def test_memory_beats_database(definitions, sqlite_engine) -> None:
    db = DatabaseFlagProvider(sqlite_engine, create_schema=True)
    db.set("engines.rule", False)
    memory = MemoryFlagProvider({"engines.rule": True})

    # Memory registered first; database registered second.
    service = _service(definitions, [memory, db])
    assert service.get_state("engines.rule").source is FlagSource.MEMORY
    assert service.get_state("engines.rule").enabled is True


def test_env_beats_memory(definitions) -> None:
    memory = MemoryFlagProvider({"engines.ml": False})
    service = _service(definitions, [_env(), memory])
    state = service.get_state("engines.ml")
    assert state.enabled is True
    assert state.source is FlagSource.ENV


def test_precedence_is_registration_order_independent(definitions, sqlite_engine) -> None:
    """The same values must resolve identically regardless of wiring order."""
    db = DatabaseFlagProvider(sqlite_engine, create_schema=True)
    db.set("engines.ml", False)
    memory = MemoryFlagProvider({"engines.ml": True})
    env = _env()

    forward = _service(definitions, [env, memory, db])
    reverse = _service(definitions, [db, memory, env])

    assert forward.get_state("engines.ml").enabled == reverse.get_state("engines.ml").enabled
    assert forward.get_state("engines.ml").source == reverse.get_state("engines.ml").source


def test_provider_source_reported(definitions) -> None:
    service = _service(definitions, [MemoryFlagProvider({"engines.ml": True})])
    assert service.get_state("engines.ml").source is FlagSource.MEMORY
