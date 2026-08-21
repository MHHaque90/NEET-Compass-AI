"""
Tests for Baseline Framework - Phase 9
"""

import pytest
from modelling.baselines.engine import BaselineEngine, BaselineResult, BaselineStatus
from modelling.splits.engine import TemporalValidationStatus
from modelling.contracts.dataset import (
    SourceFacts,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
)
from datetime import datetime, timezone


class TestBaselineEngine:
    @pytest.fixture
    def blocked_engine(self):
        return BaselineEngine(temporal_status=TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS)

    @pytest.fixture
    def ready_engine(self):
        return BaselineEngine(temporal_status=TemporalValidationStatus.READY)

    @pytest.fixture
    def sample_train_records(self):
        return [
            SourceFacts(
                counselling_year=2024, state="ALL_INDIA", counselling_authority=AuthorityType.MCC,
                round=RoundType.ROUND_1, course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
                quota=QuotaType.AI, category=CategoryType.GN, total_seats=100, allotment_count=100, closing_rank=5200,
            ),
        ]

    @pytest.fixture
    def sample_test_records(self):
        return [
            SourceFacts(
                counselling_year=2025, state="ALL_INDIA", counselling_authority=AuthorityType.MCC,
                round=RoundType.ROUND_1, course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
                quota=QuotaType.AI, category=CategoryType.GN, total_seats=100, allotment_count=100, closing_rank=5000,
            ),
        ]

    @pytest.fixture
    def historical_data(self):
        return {
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {2024: 5200},
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {2024: 100},
            },
            "pool_closing_ranks": {
                "gn|ai|round_1": {2024: 5500},
            },
        }

    def test_blocked_temporal_returns_blocked(self, blocked_engine, sample_train_records, sample_test_records, historical_data):
        results = blocked_engine.evaluate_all_baselines(sample_train_records, sample_test_records, historical_data)
        for name, result in results.items():
            assert result.status == BaselineStatus.BLOCKED_INSUFFICIENT_DATA
            assert "Temporal validation blocked" in result.abstention_reason
            assert result.mae is None

    def test_previous_year_baseline(self, ready_engine, sample_train_records, sample_test_records, historical_data):
        results = ready_engine.evaluate_all_baselines(sample_train_records, sample_test_records, historical_data)
        result = results["previous_year"]
        assert result.status == BaselineStatus.COMPUTED
        assert result.predictions["AIMS001|MBBS|ai|gn|round_1"] == 5200
        assert result.mae == 200  # |5200 - 5000|

    def test_multiyear_median_insufficient_history(self, ready_engine, sample_train_records, sample_test_records, historical_data):
        # Only 1 prior year - insufficient for median (needs 2+)
        results = ready_engine.evaluate_all_baselines(sample_train_records, sample_test_records, historical_data)
        result = results["multiyear_median"]
        assert result.status == BaselineStatus.ABSTAINED
        assert result.records_abstained == 1

    def test_seat_ratio_baseline(self, ready_engine, sample_train_records, sample_test_records, historical_data):
        results = ready_engine.evaluate_all_baselines(sample_train_records, sample_test_records, historical_data)
        result = results["seat_ratio"]
        # Prior year: rank=5200, seats=100, ratio=52
        # Current year: seats=100, prediction=52*100=5200
        assert result.status == BaselineStatus.COMPUTED
        assert result.predictions["AIMS001|MBBS|ai|gn|round_1"] == 5200

    def test_pool_level_insufficient_data(self, ready_engine, sample_train_records, sample_test_records, historical_data):
        # Only 1 pool record - insufficient (needs 5+)
        results = ready_engine.evaluate_all_baselines(sample_train_records, sample_test_records, historical_data)
        result = results["pool_level"]
        assert result.status == BaselineStatus.ABSTAINED
