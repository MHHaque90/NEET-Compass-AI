"""Capability gates built on top of the feature flag system.

Each gate is a thin, dependency-injected wrapper over a ``FeatureFlagService``
that answers a single question for one engine capability: *"may this
capability run?"*. There is deliberately no prediction or business logic here
— the gates exist so the platform's engine layer has a stable, observable
interface to feature flags.

The four supported capabilities (per the platform roadmap):

- ``RuleEngineGate``   — the deterministic rule-based scoring engine
- ``MLEngineGate``     — the machine-learning scoring engine
- ``LLMEngineGate``    — the language-model explanation engine
- ``ExperimentalFeatureGate`` — per-feature experimental rollouts
"""

from feature_flags.errors import FeatureDisabledError
from feature_flags.models import FlagContext
from feature_flags.service import FeatureFlagService


class FeatureGate:
    """Base gate: exposes a flag through ``is_enabled`` / ``require_enabled``."""

    flag_name: str

    def __init__(self, flags: FeatureFlagService) -> None:
        self._flags = flags

    def is_enabled(self, context: FlagContext | None = None) -> bool:
        return self._flags.is_enabled(self.flag_name, context)

    def require_enabled(self, context: FlagContext | None = None) -> None:
        """Raise ``FeatureDisabledError`` when the capability is disabled."""
        if not self.is_enabled(context):
            raise FeatureDisabledError(self.flag_name)


class RuleEngineGate(FeatureGate):
    """Gates the rule-based scoring engine."""

    flag_name = "engines.rule"


class MLEngineGate(FeatureGate):
    """Gates the machine-learning scoring engine."""

    flag_name = "engines.ml"


class LLMEngineGate(FeatureGate):
    """Gates the language-model explanation engine."""

    flag_name = "engines.llm"


class ExperimentalFeatureGate(FeatureGate):
    """Gates one experimental feature by name.

    A feature named ``choice_filling_v2`` is gated by the flag
    ``experimental.choice_filling_v2``. Keeping a prefix per category lets
    operators filter experimental flags in one glance.
    """

    def __init__(self, flags: FeatureFlagService, feature_name: str) -> None:
        super().__init__(flags)
        self.feature_name = feature_name
        self.flag_name = f"experimental.{feature_name}"
