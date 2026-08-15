"""Config loading and container wiring."""

from __future__ import annotations

import pytest

from feature_flags.container import FeatureFlagContainer, build_feature_flags
from feature_flags.errors import FlagConfigurationError
from feature_flags.models import FlagCategory
from feature_flags.providers.database import DatabaseFlagProvider
from feature_flags.providers.env_var import EnvVarFlagProvider
from feature_flags.providers.memory import MemoryFlagProvider

_FLAGS_YAML = """
version: 1
definitions:
  engines.rule:
    description: Rule engine
    category: RULE_ENGINE
    default: false
    owner: data-science
  engines.ml:
    description: ML engine
    category: ML_ENGINE
    default: true
  experimental.choice_filling_v2:
    category: EXPERIMENTAL
    default: false
    rules:
      - type: percentage
        key: request_id
        percentage: 10
"""


@pytest.fixture
def flags_file(tmp_path):
    path = tmp_path / "flags.yaml"
    path.write_text(_FLAGS_YAML, encoding="utf-8")
    return path


def test_loads_definitions_from_yaml(flags_file) -> None:
    container = FeatureFlagContainer(flags_path=flags_file, strict=True)
    service = container.service

    assert service.is_enabled("engines.rule") is False
    assert service.is_enabled("engines.ml") is True
    definition = service.definitions["engines.rule"]
    assert definition.category is FlagCategory.RULE_ENGINE
    assert definition.owner == "data-science"
    assert len(service.definitions["experimental.choice_filling_v2"].rules) == 1


def test_missing_file_yields_empty_catalogue(tmp_path) -> None:
    service = FeatureFlagContainer(flags_path=tmp_path / "missing.yaml", strict=False).service
    assert service.definitions == {}
    assert service.is_enabled("anything") is False


def test_default_provider_chain(flags_file) -> None:
    container = FeatureFlagContainer(flags_path=flags_file)
    assert any(isinstance(p, EnvVarFlagProvider) for p in container.service._providers)
    assert any(isinstance(p, MemoryFlagProvider) for p in container.service._providers)


def test_database_provider_wired_when_engine_present(flags_file, sqlite_engine) -> None:
    container = FeatureFlagContainer(flags_path=flags_file, engine=sqlite_engine)
    assert any(isinstance(p, DatabaseFlagProvider) for p in container.service._providers)
    container.ensure_schema()


def test_injected_providers_used_verbatim(flags_file) -> None:
    memory = MemoryFlagProvider({"engines.ml": False})
    container = FeatureFlagContainer(flags_path=flags_file, providers=[memory])
    assert container.service._providers == [memory]
    assert container.service.is_enabled("engines.ml") is False  # override wins over default


def test_container_exposes_singleton_service(flags_file) -> None:
    container = FeatureFlagContainer(flags_path=flags_file)
    assert container.service is container.service


def test_malformed_definition_fails_fast(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    path.write_text("definitions:\n  Bad.Name:\n    default: true\n", encoding="utf-8")
    with pytest.raises(FlagConfigurationError):
        FeatureFlagContainer(flags_path=path)


def test_build_feature_flags_convenience(flags_file) -> None:
    service = build_feature_flags(flags_path=flags_file)
    assert service.is_enabled("engines.rule") is False
