"""
Tests for Uncertainty and Abstention - Phase 11
"""

import pytest
from modelling.uncertainty.engine import UncertaintyEngine, ConfidenceLevel, AbstentionReason
from modelling.splits.engine import TemporalValidationStatus
from modelling.contracts.dataset import (
    SourceFacts,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
)
from datetime import datetime, timezone


class TestUncertaintyEngine:
    @pytest.fixture
    def blocked_engine(self):
        return UncertaintyEngine(temporal_status=TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS)

    @pytest.fixture
    def ready_engine(self):
        return UncertaintyEngine(temporal_status=TemporalValidationStatus.READY)

    @pytest.fixture
    def sample_source_facts(self):
        return SourceFacts(
            counselling_year=2025, state="ALL_INDIA", counselling_authority=AuthorityType.MCC,
            round=RoundType.ROUND_1, course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
            quota=QuotaType.AI, category=CategoryType.GN, total_seats=100, allotment_count=100, closing_rank=5000,
        )

    def test_temporal_blocked_abstains(self, blocked_engine, sample_source_facts):
        estimate = blocked_engine.estimate_uncertainty(5000, sample_source_facts, {})
        assert estimate.confidence_level == ConfidenceLevel.NONE
        assert AbstentionReason.TEMPORAL_VALIDATION_BLOCKED in estimate.abstention_reasons

    def test_insufficient_history_abstains(self, ready_engine, sample_source_facts):
        estimate = ready_engine.estimate_uncertainty(5000, sample_source_facts, {})
        assert estimate.confidence_level == ConfidenceLevel.NONE
        assert AbstentionReason.INSUFFICIENT_HISTORICAL_DATA in estimate.abstention_reasons

    def test_new_college_abstains(self, ready_engine, sample_source_facts):
        historical = {"closing_ranks": {}, "seat_counts": {}, "pool_closing_ranks": {}}
        estimate = ready_engine.estimate_uncertainty(5000, sample_source_facts, historical)
        assert estimate.confidence_level == ConfidenceLevel.NONE
        assert AbstentionReason.NEW_COLLEGE in estimate.abstention_reasons

    def test_sufficient_history_computes_confidence(self, ready_engine, sample_source_facts):
        historical = {
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 6200, 2021: 6000, 2022: 5800, 2023: 5500, 2024: 5200},
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 100, 2021: 100, 2022: 100, 2023: 100, 2024: 100},
            },
            "pool_closing_ranks": {
                "gn|ai|round_1": {2020: 7200, 2021: 7000, 2022: 6500, 2023: 6000, 2024: 5500},
            },
        }
        estimate = ready_engine.estimate_uncertainty(5000, sample_source_facts, historical, calibration_error=0.02)
        assert estimate.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        assert estimate.composite_score > 0
        assert estimate.lower_bound is not None
        assert estimate.upper_bound is not None

    def test_calibration_failure_abstains(self, ready_engine, sample_source_facts):
        historical = {
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 6200, 2021: 6000, 2022: 5800, 2023: 5500, 2024: 5200},
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 100, 2021: 100, 2022: 100, 2023: 100, 2024: 100},
            },
            "pool_closing_ranks": {
                "gn|ai|round_1": {2020: 7200, 2021: 7000, 2022: 6500, 2023: 6000, 2024: 5500},
            },
        }
        estimate = ready_engine.estimate_uncertainty(5000, sample_source_facts, historical, calibration_error=0.15)
        assert AbstentionReason.CALIBRATION_FAILURE in estimate.abstention_reasons

    def test_seat_matrix_change_abstains(self, ready_engine, sample_source_facts):
        historical = {
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {2021: 6000, 2022: 5800, 2023: 5500, 2024: 5200},
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 100, 2021: 100, 2022: 100, 2023: 100, 2024: 50},
            },
            "pool_closing_ranks": {
                "gn|ai|round_1": {2020: 7200, 2021: 7000, 2022: 6500, 2023: 6000, 2024: 5500},
            },
        }
        estimate = ready_engine.estimate_uncertainty(5000, sample_source_facts, historical, calibration_error=0.02)
        assert AbstentionReason.SEAT_MATRIX_CHANGE in estimate.abstention_reasons

    def test_user_display_format(self, ready_engine, sample_source_facts):
        historical = {
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 6200, 2021: 6000, 2022: 5800, 2023: 5500, 2024: 5200},
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {2020: 100, 2021: 100, 2022: 100, 2023: 100, 2024: 100},
            },
            "pool_closing_ranks": {
                "gn|ai|round_1": {2020: 7200, 2021: 7000, 2022: 6500, 2023: 6000, 2024: 5500},
            },
        }
        estimate = ready_engine.estimate_uncertainty(5000, sample_source_facts, historical, calibration_error=0.02)
        display = ready_engine.format_user_display(estimate)
        assert "badge" in display
        assert "text" in display
        assert "confidence" in display
