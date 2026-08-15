"""Service facade policy: strict mode, overrides, snapshots."""

from __future__ import annotations

import pytest

from feature_flags.errors import FlagConfigurationError, UnknownFlagError
from feature_flags.models import FlagSource
from feature_flags.providers.memory import MemoryFlagProvider
from feature_flags.service import FeatureFlagService


def _service(
    strict: bool = False,
    with_memory: bool = True,
    definitions=None,
) -> FeatureFlagService:
    return FeatureFlagService(
        definitions=definitions or {},
        providers=[MemoryFlagProvider()] if with_memory else [],
        strict=strict,
    )


def test_unknown_flag_lenient_defaults_disabled(definitions) -> None:
    service = FeatureFlagService(definitions=definitions, providers=[])
    state = service.get_state("no.such.flag")
    assert state.enabled is False
    assert state.source is FlagSource.UNKNOWN


def test_unknown_flag_strict_raises(definitions) -> None:
    service = FeatureFlagService(definitions=definitions, providers=[], strict=True)
    with pytest.raises(UnknownFlagError):
        service.get_state("no.such.flag")


def test_set_and_clear_override(definitions) -> None:
    service = FeatureFlagService(definitions=definitions, providers=[MemoryFlagProvider()])
    assert service.is_enabled("engines.rule") is False

    service.set_override("engines.rule", True)
    assert service.is_enabled("engines.rule") is True
    assert service.get_state("engines.rule").source is FlagSource.MEMORY

    service.clear_override("engines.rule")
    assert service.is_enabled("engines.rule") is False


def test_clear_all_overrides(definitions) -> None:
    service = FeatureFlagService(definitions=definitions, providers=[MemoryFlagProvider()])
    service.set_override("engines.rule", True)
    service.set_override("engines.ml", False)
    service.clear_override()
    assert service.get_state("engines.rule").source is FlagSource.DEFAULT


def test_set_override_without_memory_provider_raises(definitions) -> None:
    service = FeatureFlagService(definitions=definitions, providers=[])
    with pytest.raises(FlagConfigurationError):
        service.set_override("engines.rule", True)
    with pytest.raises(FlagConfigurationError):
        service.clear_override()


def test_all_states_ordered_snapshot(definitions) -> None:
    service = FeatureFlagService(definitions=definitions, providers=[MemoryFlagProvider()])
    states = service.all_states()
    assert list(states.keys()) == sorted(definitions)
    assert all(isinstance(s.source, FlagSource) for s in states.values())
