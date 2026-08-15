"""Model validation: definitions, rules, contexts, states."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from feature_flags.models import (
    EnvironmentRule,
    FlagContext,
    FlagDefinition,
    FlagSource,
    FlagState,
    PercentageRule,
    SegmentRule,
)


@pytest.mark.parametrize(
    "name",
    [
        "engines.rule",
        "experimental.choice_filling_v2",
        "a",
        "a_b.c_d",
    ],
)
def test_valid_flag_names(name: str) -> None:
    assert FlagDefinition(name=name).name == name


@pytest.mark.parametrize("name", ["Engines.Rule", "engines rule", "engines-rule", "1x", "a..b", ""])
def test_invalid_flag_names(name: str) -> None:
    with pytest.raises(ValidationError):
        FlagDefinition(name=name)


def test_definition_defaults() -> None:
    flag = FlagDefinition(name="engines.ml")
    assert flag.default is False
    assert flag.category.value == "GENERAL"
    assert flag.is_experimental is False


def test_experimental_category_marked() -> None:
    from feature_flags.models import FlagCategory

    flag = FlagDefinition(name="experimental.x", category=FlagCategory.EXPERIMENTAL)
    assert flag.is_experimental is True


def test_environment_rule_matches_and_not() -> None:
    rule = EnvironmentRule(environments=["production", "staging"])
    assert rule.matches(FlagContext(environment="production")) is True
    assert rule.matches(FlagContext(environment="development")) is False
    assert rule.matches(FlagContext()) is False  # missing attribute


def test_percentage_rule_is_deterministic() -> None:
    rule = PercentageRule(percentage=50, key="request_id")
    context = FlagContext(request_id="fixed-key-123")
    assert rule.matches(context) == rule.matches(context)


def test_percentage_rule_edges() -> None:
    assert (
        PercentageRule(percentage=0, key="request_id").matches(FlagContext(request_id="x"))
        is False
    )
    assert (
        PercentageRule(percentage=100, key="request_id").matches(FlagContext(request_id="x"))
        is True
    )
    assert PercentageRule(percentage=50, key="request_id").matches(FlagContext()) is False


def test_percentage_rule_rolls_out_roughly_evenly() -> None:
    rule = PercentageRule(percentage=50, key="request_id")
    keys = [f"key-{i}" for i in range(200)]
    enabled = sum(rule.matches(FlagContext(request_id=k)) for k in keys)
    assert 40 <= enabled <= 160  # loose sanity band for determinism


def test_segment_rule_matches() -> None:
    rule = SegmentRule(key="user_id", segments=["u-1", "u-2"])
    assert rule.matches(FlagContext(user_id="u-1")) is True
    assert rule.matches(FlagContext(user_id="u-9")) is False


def test_discriminated_rule_union_rejects_unknown_type() -> None:
    with pytest.raises(ValidationError):
        FlagDefinition(
            name="x.y",
            rules=[{"type": "magic", "key": "k", "segments": ["s"]}],
        )


def test_flag_context_allows_extra_attributes() -> None:
    context = FlagContext(environment="prod", tenant_id="t-1", count=3)
    assert context.get("tenant_id") == "t-1"
    assert context.get("count") == 3
    assert context.get("missing", "fallback") == "fallback"


def test_flag_state_carries_provenance() -> None:
    state = FlagState(
        name="engines.rule",
        enabled=True,
        source=FlagSource.DATABASE,
        rule_matched=None,
    )
    assert state.enabled is True
    assert state.source == FlagSource.DATABASE
    assert state.evaluated_at is not None
