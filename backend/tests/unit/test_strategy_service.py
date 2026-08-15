"""StrategyService deterministic advisory rules."""

from __future__ import annotations

from app.application.services.strategy_service import StrategyService
from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.college import College
from app.domain.enums import IndiaState, QuotaType


def test_filter_colleges_respects_budget_and_preferences(
    sample_candidate: CandidateProfile,
    sample_college: College,
    expensive_college: College,
) -> None:
    service = StrategyService()
    kept = service.filter_colleges(sample_candidate, [sample_college, expensive_college])
    assert kept == [sample_college]


def test_filter_colleges_ignores_non_preferred_states(
    sample_candidate: CandidateProfile,
    sample_college: College,
) -> None:
    service = StrategyService()
    # Affordable college outside the preferred states is dropped.
    non_preferred = sample_college.model_copy(update={"state": IndiaState.BIHAR})
    assert service.filter_colleges(sample_candidate, [non_preferred]) == []

    # Same college in a preferred state is kept (and passes budget).
    assert service.filter_colleges(sample_candidate, [sample_college]) == [sample_college]


def test_rank_choice_order_stable_and_preference_first(
    sample_candidate: CandidateProfile,
    sample_college: College,
    expensive_college: College,
) -> None:
    service = StrategyService()
    ordered = service.rank_choice_order(sample_candidate, [expensive_college, sample_college])
    # Same state -> cheaper first (sample_college 50k < expensive 15M).
    assert ordered == [sample_college, expensive_college]


def test_build_strategy_contains_explainer_reasons(
    sample_candidate: CandidateProfile,
    sample_college: College,
) -> None:
    service = StrategyService()
    strategy = service.build_strategy(sample_candidate, sample_college)

    assert strategy["budget_fit"] is True
    assert strategy["state_fit"] is True
    reason_types = {r["type"] for r in strategy["reasons"]}
    assert "budget" in reason_types
    assert "preferred_state" in reason_types


def test_state_quota_reason_only_when_domicile_matches(
    sample_candidate: CandidateProfile,
    sample_college: College,
) -> None:
    service = StrategyService()

    state_candidate = sample_candidate.model_copy(update={"quota_type": QuotaType.STATE})
    reasons = service.build_strategy(state_candidate, sample_college)["reasons"]
    assert any(r["type"] == "state_quota" for r in reasons)

    aiq_reasons = service.build_strategy(sample_candidate, sample_college)["reasons"]
    assert not any(r["type"] == "state_quota" for r in aiq_reasons)
