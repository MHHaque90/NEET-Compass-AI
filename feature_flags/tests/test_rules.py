"""Targeting rules: narrowing semantics at the service level."""

from __future__ import annotations

from feature_flags.models import FlagContext, FlagDefinition
from feature_flags.service import FeatureFlagService

_RULE_FLAG = FlagDefinition(
    name="experimental.x",
    default=True,
    rules=[
        {"type": "environment", "environments": ["production", "staging"]},
        {"type": "percentage", "key": "request_id", "percentage": 100},
        {"type": "segment", "key": "team", "segments": ["core"]},
    ],
)


def _service() -> FeatureFlagService:
    return FeatureFlagService(definitions={"experimental.x": _RULE_FLAG}, providers=[])


def _context(**extra) -> FlagContext:
    base = FlagContext(environment="production", request_id="r-1", team="core")
    return base.model_copy(update=extra)


def test_all_rules_match_enables() -> None:
    assert _service().is_enabled("experimental.x", _context()) is True


def test_any_rule_fail_disables() -> None:
    assert _service().is_enabled("experimental.x", _context(team="other")) is False
    assert _service().is_enabled("experimental.x", _context(environment="dev")) is False


def test_no_context_skips_rules() -> None:
    state = _service().get_state("experimental.x")
    assert state.enabled is True  # default applies
    assert state.rule_matched is None


def test_rule_result_reported_in_state() -> None:
    state = _service().get_state("experimental.x", _context(team="other"))
    assert state.rule_matched is False
    assert state.enabled is False


def test_rules_narrow_but_never_widen_a_disabled_flag() -> None:
    disabled = FlagDefinition(
        name="experimental.y",
        default=False,
        rules=[{"type": "environment", "environments": ["production"]}],
    )
    service = FeatureFlagService(definitions={"experimental.y": disabled}, providers=[])
    assert service.is_enabled("experimental.y", _context()) is False


def test_missing_context_attribute_is_false() -> None:
    rule_only = FlagDefinition(
        name="experimental.z",
        default=True,
        rules=[{"type": "percentage", "key": "missing_key", "percentage": 100}],
    )
    service = FeatureFlagService(definitions={"experimental.z": rule_only}, providers=[])
    assert service.is_enabled("experimental.z", _context()) is False
