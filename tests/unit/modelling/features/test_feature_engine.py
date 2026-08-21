"""
Tests for Feature Engineering Architecture - Phase 3
"""

import pytest
from datetime import datetime, timezone
from modelling.contracts.dataset import (
    SourceFacts,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
)
from modelling.features.registry import FeatureRegistry
from modelling.features.engine import FeatureEngine
from modelling.features.engine import TemporalAvailability, LeakageStatus


class TestFeatureEngine:
    @pytest.fixture
    def registry(self):
        return FeatureRegistry.create_default_registry()

    @pytest.fixture
    def engine(self, registry):
        return FeatureEngine(registry=registry)

    @pytest.fixture
    def sample_source_facts(self):
        return SourceFacts(
            counselling_year=2025,
            state="ALL_INDIA",
            counselling_authority=AuthorityType.MCC,
            round=RoundType.ROUND_1,
            course="MBBS",
            institute="AIIMS Delhi",
            institute_code="AIMS001",
            quota=QuotaType.AI,
            category=CategoryType.GN,
            total_seats=100,
            allotment_count=100,
            closing_rank=5000,
        )

    @pytest.fixture
    def historical_data(self):
        return {
            "years": [2021, 2022, 2023, 2024, 2025],
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {
                    2021: 6000,
                    2022: 5800,
                    2023: 5500,
                    2024: 5200,
                }
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {
                    2021: 100,
                    2022: 100,
                    2023: 100,
                    2024: 100,
                }
            },
        }

    def test_compute_core_features(self, engine, sample_source_facts, historical_data):
        features = engine.compute_features(
            sample_source_facts,
            historical_data,
            prediction_year=2025,
            prediction_round=RoundType.ROUND_1,
        )
        assert features.round_number == 1
        assert features.is_first_round is True
        assert features.category_quota_combo == "gn_ai"
        assert features.state_quota_indicator is False
        assert features.year_index == 4  # 2025 - 2021
        assert features.seat_count_log > 0

    def test_historical_features_computed(self, engine, sample_source_facts, historical_data):
        features = engine.compute_features(
            sample_source_facts,
            historical_data,
            prediction_year=2025,
            prediction_round=RoundType.ROUND_1,
        )
        # With 4 prior years, median should be computable
        assert features.historical_closing_rank_median is not None
        assert features.historical_closing_rank_p10 is not None
        assert features.historical_closing_rank_p90 is not None

    def test_insufficient_history_returns_none(self, engine, sample_source_facts):
        # Only 1 prior year - insufficient for median
        sparse_data = {
            "years": [2024, 2025],
            "closing_ranks": {
                "AIMS001|MBBS|ai|gn|round_1": {2024: 5200},
            },
            "seat_counts": {
                "AIMS001|MBBS|ai|gn|round_1": {2024: 100},
            },
        }
        features = engine.compute_features(
            sample_source_facts,
            sparse_data,
            prediction_year=2025,
            prediction_round=RoundType.ROUND_1,
        )
        assert features.historical_closing_rank_median is None
        assert features.prior_year_closing_rank == 5200

    def test_seat_count_change_pct(self, engine, sample_source_facts, historical_data):
        # Modify historical to have different seat count
        historical_data["seat_counts"]["AIMS001|MBBS|ai|gn|round_1"][2024] = 120
        features = engine.compute_features(
            sample_source_facts,
            historical_data,
            prediction_year=2025,
            prediction_round=RoundType.ROUND_1,
        )
        # (100 - 120) / 120 * 100 = -16.67%
        assert features.seat_count_change_pct is not None
        assert abs(features.seat_count_change_pct - (-16.67)) < 0.1

    def test_seat_availability_ratio_not_computable(self, engine, sample_source_facts, historical_data):
        features = engine.compute_features(
            sample_source_facts,
            historical_data,
            prediction_year=2025,
            prediction_round=RoundType.ROUND_1,
        )
        # Applicants unknown at prediction time
        assert features.seat_availability_ratio is None

    def test_feature_version_metadata_generated(self, engine):
        metadata = engine.get_feature_version_metadata()
        assert metadata.version == "features_v1"
        assert "round_number" in metadata.feature_definitions
        assert "historical_closing_rank_median" in metadata.feature_definitions
        assert metadata.feature_computation_code_hash is not None


class TestFeatureRegistry:
    def test_default_registry_created(self):
        registry = FeatureRegistry.create_default_registry()
        assert len(registry.features) > 0
        assert "round_number" in registry.features
        assert "historical_closing_rank_median" in registry.features
        assert "seat_availability_ratio" in registry.features

    def test_feature_leakage_status(self):
        registry = FeatureRegistry.create_default_registry()
        # Core features should be SAFE
        assert registry.features["round_number"].leakage_status == LeakageStatus.SAFE
        assert registry.features["is_first_round"].leakage_status == LeakageStatus.SAFE

        # Historical features should be CONDITIONAL
        assert registry.features["historical_closing_rank_median"].leakage_status == LeakageStatus.CONDITIONAL
        assert registry.features["prior_year_closing_rank"].leakage_status == LeakageStatus.CONDITIONAL

        # Forbidden feature
        assert registry.features["seat_availability_ratio"].leakage_status == LeakageStatus.FORBIDDEN
        assert registry.features["seat_availability_ratio"].temporal_availability == TemporalAvailability.NOT_ALLOWED

    def test_register_duplicate_raises(self):
        registry = FeatureRegistry()
        from modelling.features.engine import FeatureDefinition
        from modelling.features.provenance import FeatureProvenance

        feat = FeatureDefinition(
            name="test_feature",
            definition="Test",
            source_fields=[],
            transformation="test",
            temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
            version="v1",
            provenance=None,
            leakage_status=LeakageStatus.SAFE,
        )
        registry.register(feat)
        with pytest.raises(ValueError):
            registry.register(feat)

    def test_unknown_leakage_rejected(self):
        registry = FeatureRegistry()
        from modelling.features.engine import FeatureDefinition
        with pytest.raises(ValueError):
            feat = FeatureDefinition(
                name="bad_feature",
                definition="Test",
                source_fields=[],
                transformation="test",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="v1",
                provenance=None,
                leakage_status=LeakageStatus.UNKNOWN,
            )
            registry.register(feat)
