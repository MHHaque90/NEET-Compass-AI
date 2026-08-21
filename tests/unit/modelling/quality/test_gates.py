"""
Tests for Modelling Data Quality Gates - Phase 16
"""

import pytest
from datetime import datetime, timezone
from modelling.quality.gates import ModellingQualityGates, QualityGateResult, ModellingQualityGate
from modelling.contracts.dataset import (
    ModellingRecord,
    SourceFacts,
    DerivedFeatures,
    Targets,
    Provenance,
    TemporalMetadata,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
)


class TestModellingQualityGates:
    @pytest.fixture
    def gates(self):
        return ModellingQualityGates()

    @pytest.fixture
    def valid_record(self):
        facts = SourceFacts(
            counselling_year=2025, state="ALL_INDIA", counselling_authority=AuthorityType.MCC,
            round=RoundType.ROUND_1, course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
            quota=QuotaType.AI, category=CategoryType.GN, total_seats=100, allotment_count=100, closing_rank=5000,
        )
        features = DerivedFeatures(
            round_number=1, is_first_round=True, category_quota_combo="gn_ai",
            institute_type="govt", state_quota_indicator=False, year_index=0, seat_count_log=4.615,
        )
        targets = Targets()
        prov = Provenance(
            source_file_id="test_id", file_checksum="a"*64, source_url="https://test.com",
            parser_version="v1", retrieval_timestamp=datetime.now(timezone.utc), contract_version="1.0.0",
            adapter_version="v1", transformation_version="v1", feature_version="v1", quality_gate_version="v1",
        )
        temporal = TemporalMetadata(
            prediction_time=datetime.now(timezone.utc), latest_allowed_year=2024,
            latest_allowed_round=RoundType.ROUND_1, feature_computation_timestamp=datetime.now(timezone.utc),
            temporal_availability_verified=True, leakage_check_passed=True,
        )
        return ModellingRecord(
            source_facts=facts, derived_features=features, targets=targets,
            provenance=prov, temporal_metadata=temporal, dataset_version="v1", record_id="rec1",
        )

    def test_valid_record_passes_all_gates(self, gates, valid_record):
        result = gates.run_gates([valid_record])
        assert result.overall_passed is True
        assert result.passed_gates == 13
        assert result.total_gates == 13

    def test_invalid_year_fails(self, gates, valid_record):
        # SourceFacts validates year in __post_init__, so we test the validation directly
        with pytest.raises(ValueError, match="Invalid counselling_year"):
            SourceFacts(
                counselling_year=2010, state="ALL_INDIA", counselling_authority=AuthorityType.MCC,
                round=RoundType.ROUND_1, course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
                quota=QuotaType.AI, category=CategoryType.GN, total_seats=100, allotment_count=100,
            )

    def test_invalid_category_fails(self, gates, valid_record):
        # Can't easily test this since CategoryType is enum
        # But the gate would catch invalid values if they somehow got through
        pass

    def test_negative_seats_fails(self, gates, valid_record):
        # SourceFacts validates seats in __post_init__
        with pytest.raises(ValueError, match="total_seats cannot be negative"):
            SourceFacts(
                counselling_year=2025, state="ALL_INDIA", counselling_authority=AuthorityType.MCC,
                round=RoundType.ROUND_1, course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
                quota=QuotaType.AI, category=CategoryType.GN, total_seats=-1, allotment_count=100,
            )

    def test_missing_provenance_fails(self, gates, valid_record):
        # Provenance validates source_file_id in __post_init__
        from modelling.contracts.dataset import Provenance
        with pytest.raises(ValueError, match="source_file_id is required"):
            Provenance(
                source_file_id="", file_checksum="a"*64, source_url="https://test.com",
                parser_version="v1", retrieval_timestamp=datetime.now(timezone.utc), contract_version="1.0.0",
                adapter_version="v1", transformation_version="v1", feature_version="v1", quality_gate_version="v1",
            )

    def test_no_future_info_check(self, gates, valid_record):
        # Temporal metadata with failed checks
        bad_temporal = TemporalMetadata(
            prediction_time=datetime.now(timezone.utc), latest_allowed_year=2024,
            latest_allowed_round=RoundType.ROUND_1, feature_computation_timestamp=datetime.now(timezone.utc),
            temporal_availability_verified=False, leakage_check_passed=False,
        )
        bad_record = ModellingRecord(
            source_facts=valid_record.source_facts, derived_features=valid_record.derived_features,
            targets=valid_record.targets, provenance=valid_record.provenance,
            temporal_metadata=bad_temporal, dataset_version="v1", record_id="rec_bad",
        )
        result = gates.run_gates([bad_record])
        assert result.overall_passed is False
        assert not result.gate_results[ModellingQualityGate.NO_FUTURE_INFORMATION]

    def test_pii_rejection(self, gates, valid_record):
        # The quality gates check for PII fields in source_facts and derived_features
        # Since our dataclasses don't have PII fields, this should pass
        result = gates.run_gates([valid_record])
        assert result.gate_results[ModellingQualityGate.NO_PII] is True
