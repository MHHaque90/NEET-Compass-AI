"""College entity behaviour."""

from __future__ import annotations

from app.domain.entities.college import College


def test_state_quota_seats_is_derived(sample_college: College) -> None:
    assert sample_college.state_quota_seats == 120


def test_budget_none_means_unlimited(sample_college: College) -> None:
    assert sample_college.is_within_budget(None) is True


def test_budget_boundary_inclusive(sample_college: College) -> None:
    assert sample_college.is_within_budget(50_000) is True
    assert sample_college.is_within_budget(49_999) is False
