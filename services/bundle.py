"""Service-layer composition: a ready-to-use bundle of engine gates."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from feature_flags.service import FeatureFlagService

from services.gates import (
    ExperimentalFeatureGate,
    FeatureGate,
    LLMEngineGate,
    MLEngineGate,
    RuleEngineGate,
)


@dataclass(frozen=True)
class EngineGates:
    """Bundle of capability gates sharing one flag service.

    A single ``EngineGates`` is injected wherever the platform needs to ask
    *which* engine capabilities are enabled, so call sites never touch the
    flag system directly. ``experimental(name)`` creates a per-feature gate
    on demand.
    """

    rule: RuleEngineGate
    ml: MLEngineGate
    llm: LLMEngineGate
    experimental: Callable[[str], ExperimentalFeatureGate]

    def experimental_feature(self, feature_name: str) -> ExperimentalFeatureGate:
        """Return the gate for one experimental feature."""
        return self.experimental(feature_name)


def build_engine_gates(flags: FeatureFlagService) -> EngineGates:
    """Composition root for the services layer: gates share ``flags``."""
    return EngineGates(
        rule=RuleEngineGate(flags),
        ml=MLEngineGate(flags),
        llm=LLMEngineGate(flags),
        experimental=lambda name: ExperimentalFeatureGate(flags, name),
    )


__all__ = [
    "EngineGates",
    "ExperimentalFeatureGate",
    "FeatureGate",
    "LLMEngineGate",
    "MLEngineGate",
    "RuleEngineGate",
    "build_engine_gates",
]
