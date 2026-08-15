"""Engine capability gates and their composition bundle."""

from __future__ import annotations

import pytest
from feature_flags.errors import FeatureDisabledError
from feature_flags.models import FlagContext, FlagDefinition
from feature_flags.service import FeatureFlagService

from services.bundle import build_engine_gates
from services.gates import (
    ExperimentalFeatureGate,
    LLMEngineGate,
    MLEngineGate,
    RuleEngineGate,
)


def _service(**defaults: bool) -> FeatureFlagService:
    definitions = {
        "engines.rule": FlagDefinition(name="engines.rule", default=defaults.get("rule", False)),
        "engines.ml": FlagDefinition(name="engines.ml", default=defaults.get("ml", False)),
        "engines.llm": FlagDefinition(name="engines.llm", default=defaults.get("llm", False)),
    }
    return FeatureFlagService(definitions=definitions, providers=[])


def test_named_gates_reflect_definition_defaults() -> None:
    service = _service(rule=True, ml=True)
    assert RuleEngineGate(service).is_enabled() is True
    assert MLEngineGate(service).is_enabled() is True
    assert LLMEngineGate(service).is_enabled() is False


def test_require_enabled_passes_when_enabled() -> None:
    gate = RuleEngineGate(_service(rule=True))
    gate.require_enabled()


def test_require_enabled_raises_when_disabled() -> None:
    gate = LLMEngineGate(_service())
    with pytest.raises(FeatureDisabledError):
        gate.require_enabled()


def test_experimental_gate_builds_flag_name() -> None:
    gate = ExperimentalFeatureGate(_service(), "choice_filling_v2")
    assert gate.flag_name == "experimental.choice_filling_v2"


def test_experimental_gate_definitions_exist_before_eval() -> None:
    """Experimental gates still need a definition; unknown -> disabled (lenient)."""
    gate = ExperimentalFeatureGate(_service(), "choice_filling_v2")
    assert gate.is_enabled() is False


def test_gates_pass_context_to_rules() -> None:
    definition = FlagDefinition(
        name="experimental.x",
        default=True,
        rules=[{"type": "environment", "environments": ["production"]}],
    )
    service = FeatureFlagService(definitions={"experimental.x": definition}, providers=[])
    gate = ExperimentalFeatureGate(service, "x")

    assert gate.is_enabled(FlagContext(environment="production")) is True
    assert gate.is_enabled(FlagContext(environment="development")) is False


def test_bundle_exposes_all_gates() -> None:
    gates = build_engine_gates(_service(llm=True))
    assert gates.rule.is_enabled() is False
    assert gates.ml.is_enabled() is False
    assert gates.llm.is_enabled() is True
    assert gates.experimental_feature("choice_filling_v2").is_enabled() is False
