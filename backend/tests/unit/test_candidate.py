"""CandidateProfile invariants and helper behaviour."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.entities.candidate import CandidateProfile
from app.domain.enums import Category, Gender, IndiaState, QuotaType


def _base(**overrides) -> dict:
    return {
        "air": 100,
        "marks": 650,
        "category": Category.GENERAL,
        "domicile_state": IndiaState.KARNATAKA,
        "gender": Gender.NEUTRAL,
        "quota_type": QuotaType.AIQ,
        **overrides,
    }


def test_valid_candidate_constructs() -> None:
    profile = CandidateProfile(**_base())
    assert profile.air == 100
    assert profile.budget is None


@pytest.mark.parametrize("air", [0, -5])
def test_air_must_be_positive(air: int) -> None:
    with pytest.raises(ValidationError):
        CandidateProfile(**_base(air=air))


@pytest.mark.parametrize("marks", [-1, 721])
def test_marks_must_be_within_720(marks: int) -> None:
    with pytest.raises(ValidationError):
        CandidateProfile(**_base(marks=marks))


def test_prefers_state() -> None:
    profile = CandidateProfile(**_base(preferred_states=(IndiaState.TAMIL_NADU,)))
    assert profile.prefers_state(IndiaState.TAMIL_NADU)
    assert not profile.prefers_state(IndiaState.KERALA)


def test_feature_vector_is_deterministic_and_stable() -> None:
    profile = CandidateProfile(**_base(budget=1_000_000))
    features = profile.feature_vector()
    assert features["air"] == 100
    assert features["category"] == "GENERAL"
    assert features["budget"] == 1_000_000
    assert features["preferred_states"] == []
    assert features == CandidateProfile(**_base(budget=1_000_000)).feature_vector()
