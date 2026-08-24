"""Tests for Temporal Coverage — Sprint 4.1.

Critical assertions:
- ONE VERIFIED YEAR -> TEMPORAL_VALIDATION_BLOCKED
- Minimum 3 verified years required
- Chronological ordering required
"""

import pytest
from etl.contracts.historical.temporal_gate import (
    TemporalReadinessGate,
    TemporalReadinessResult,
    compute_temporal_readiness,
    MINIMUM_VERIFIED_YEARS,
    PREFERRED_VERIFIED_YEARS,
)


class TestTemporalReadinessGate:
    """Test temporal readiness validation."""

    def test_minimum_years_constant(self):
        """MINIMUM_VERIFIED_YEARS should be 3."""
        assert MINIMUM_VERIFIED_YEARS == 3

    def test_preferred_years_constant(self):
        """PREFERRED_VERIFIED_YEARS should be 4."""
        assert PREFERRED_VERIFIED_YEARS == 4

    def test_one_verified_year_blocked(self):
        """1 verified year -> TEMPORAL_VALIDATION_BLOCKED."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2025]})
        assert result.passed is False
        assert result.verified_count == 1
        assert result.minimum_required == 3
        assert result.can_split_train_val_test is False
        assert result.details["temporal_validation_status"] == "BLOCKED"

    def test_two_verified_years_blocked(self):
        """2 verified years -> TEMPORAL_VALIDATION_BLOCKED."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2024, 2025]})
        assert result.passed is False
        assert result.verified_count == 2
        assert result.can_split_train_val_test is False

    def test_three_verified_years_ready(self):
        """3 verified years -> READY (minimum met)."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2023, 2024, 2025]})
        assert result.passed is True
        assert result.verified_count == 3
        assert result.can_split_train_val_test is True
        assert result.details["temporal_validation_status"] == "READY"

    def test_four_verified_years_ready(self):
        """4 verified years -> READY (preferred met)."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2022, 2023, 2024, 2025]})
        assert result.passed is True
        assert result.verified_count == 4
        assert result.can_split_train_val_test is True

    def test_gap_detection(self):
        """Should detect gaps in verified years."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2022, 2024, 2025]})  # Missing 2023
        assert result.has_gaps is True
        assert 2023 in result.gap_years

    def test_no_gaps_when_continuous(self):
        """Continuous years should have no gaps."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2022, 2023, 2024, 2025]})
        assert result.has_gaps is False
        assert result.gap_years == ()

    def test_chronological_ordering(self):
        """Verified years should be chronologically ordered."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2025, 2023, 2024]})  # Out of order input
        assert result.chronologically_ordered is True  # Sorted internally
        assert result.verified_years == (2023, 2024, 2025)

    def test_cross_authority_aggregation(self):
        """Should aggregate unique years across authorities."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({
            "MCC": [2024, 2025],
            "Maharashtra": [2025],
        })
        # Unique years: 2024, 2025 = 2
        assert result.verified_count == 2
        assert result.verified_years == (2024, 2025)

    def test_cross_authority_unique_years(self):
        """Should count unique years across authorities."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({
            "MCC": [2023, 2024, 2025],
            "Maharashtra": [2024, 2025],
        })
        assert result.verified_count == 3  # 2023, 2024, 2025
        assert result.verified_years == (2023, 2024, 2025)

    def test_convenience_function(self):
        """compute_temporal_readiness convenience function."""
        result = compute_temporal_readiness({"MCC": [2025]}, minimum_years=3)
        assert isinstance(result, TemporalReadinessResult)
        assert result.passed is False
        assert result.verified_count == 1

    def test_result_boolean_conversion(self):
        """TemporalReadinessResult converts to bool."""
        result_pass = TemporalReadinessResult(
            passed=True, verified_years=(2023, 2024, 2025), verified_count=3,
            minimum_required=3, has_gaps=False, gap_years=(),
            chronologically_ordered=True, can_split_train_val_test=True, details={}
        )
        result_fail = TemporalReadinessResult(
            passed=False, verified_years=(2025,), verified_count=1,
            minimum_required=3, has_gaps=False, gap_years=(),
            chronologically_ordered=True, can_split_train_val_test=False, details={}
        )
        assert bool(result_pass) is True
        assert bool(result_fail) is False

    def test_details_include_required_info(self):
        """Result details should include all required information."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2025]})
        assert "verified_years_per_authority" in result.details
        assert "total_verified_years" in result.details
        assert "minimum_required" in result.details
        assert "gap_years" in result.details
        assert "can_forward_chain" in result.details
        assert "temporal_validation_status" in result.details
        assert result.details["temporal_validation_status"] == "BLOCKED"