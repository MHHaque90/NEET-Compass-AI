"""Deterministic strategy service.

Generates the *advisory* parts of a recommendation that do not require
prediction: budget filtering, state-preference filtering, quota eligibility
facts, and a stable choice-filling order. The probabilistic side
(probability, expected round, confidence) is owned exclusively by the
``RecommendationEngine`` port — this service never fabricates numbers.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.college import College
from app.domain.enums import QuotaType

# Rationale strings are data, kept here so the strategy payload stays
# self-explanatory and i18n-able later.
_REASON_BUDGET = "College annual fee ({fee} INR) is within the candidate budget ({budget} INR)."
_REASON_BUDGET_EXCEEDED = (
    "College annual fee ({fee} INR) exceeds the candidate budget ({budget} INR)."
)
_REASON_STATE = "College is located in a preferred state ({state})."
_REASON_STATE_QUOTA = (
    "Candidate domicile ({state}) matches this college's state, "
    "so State Quota seats are open to them."
)


class StrategyService:
    """Advisory rules that do not depend on historical prediction."""

    def filter_colleges(
        self,
        candidate: CandidateProfile,
        colleges: Sequence[College],
    ) -> list[College]:
        """Keep only colleges the candidate could realistically consider."""
        eligible: list[College] = []
        for college in colleges:
            if not college.is_within_budget(candidate.budget):
                continue
            if candidate.preferred_states and not candidate.prefers_state(college.state):
                continue
            eligible.append(college)
        return eligible

    def rank_choice_order(
        self,
        candidate: CandidateProfile,
        colleges: Sequence[College],
    ) -> list[College]:
        """Stable, deterministic ordering for choice filling.

        Rule-based baseline — preferred-state colleges first, then cheaper
        colleges first, preserving input order for ties. Replaced/augmented
        by the ML engine's ordering once trained.
        """
        return sorted(
            colleges,
            key=lambda c: (
                0 if candidate.prefers_state(c.state) else 1,
                c.annual_fee_inr,
            ),
        )

    def build_strategy(
        self,
        candidate: CandidateProfile,
        college: College,
    ) -> dict[str, object]:
        """Factual strategy payload for a single candidate/college pair."""
        reasons: list[dict[str, object]] = []

        if college.is_within_budget(candidate.budget):
            reasons.append(
                {
                    "type": "budget",
                    "message": _REASON_BUDGET.format(
                        fee=college.annual_fee_inr, budget=candidate.budget
                    ),
                }
            )
        else:
            reasons.append(
                {
                    "type": "budget_warning",
                    "message": _REASON_BUDGET_EXCEEDED.format(
                        fee=college.annual_fee_inr, budget=candidate.budget
                    ),
                }
            )

        if candidate.prefers_state(college.state):
            reasons.append(
                {
                    "type": "preferred_state",
                    "message": _REASON_STATE.format(state=college.state.value),
                }
            )

        if candidate.quota_type == QuotaType.STATE and college.state == candidate.domicile_state:
            reasons.append(
                {
                    "type": "state_quota",
                    "message": _REASON_STATE_QUOTA.format(state=college.state.value),
                }
            )

        return {
            "quota_type": candidate.quota_type.value,
            "budget_fit": college.is_within_budget(candidate.budget),
            "state_fit": not candidate.preferred_states or candidate.prefers_state(college.state),
            "reasons": reasons,
            "note": (
                "Probabilistic strategy (expected round, upgrades, risks) becomes available "
                "once a scoring engine is registered."
            ),
        }
