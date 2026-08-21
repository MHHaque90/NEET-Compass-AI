"""
Tests for Modelling Dataset Contract - Phase 2
"""

import pytest
from datetime import datetime, timezone
from modelling.contracts.dataset import (
    ModellingRecord,
    SourceFacts,
    DerivedFeatures,
    Targets,
    Provenance,
    TemporalMetadata,
    ModellingDatasetContract,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
    compute_record_id,
    compute_dataset_version,
)


class TestSourceFacts:
    def test_valid_source_facts(self):
        facts = SourceFacts(
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
            score=650.0,
        )
        assert facts.counselling_year == 2025
        assert facts.closing_rank == 5000

    def test_invalid_year_raises(self):
        with pytest.raises(ValueError):
            SourceFacts(
                counselling_year=2010,
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
            )

    def test_negative_seats_raises(self):
        with pytest.raises(ValueError):
            SourceFacts(
                counselling_year=2025,
                state="ALL_INDIA",
                counselling_authority=AuthorityType.MCC,
                round=RoundType.ROUND_1,
                course="MBBS",
                institute="AIIMS Delhi",
                institute_code="AIMS001",
                quota=QuotaType.AI,
                category=CategoryType.GN,
                total_seats=-1,
                allotment_count=100,
            )


class TestDerivedFeatures:
    def test_valid_derived_features(self):
        features = DerivedFeatures(
            round_number=1,
            is_first_round=True,
            category_quota_combo="gn_ai",
            institute_type="govt",
            state_quota_indicator=False,
            year_index=0,
            seat_count_log=4.615,
            historical_closing_rank_median=5000.0,
            feature_version="features_v1",
        )
        assert features.round_number == 1
        assert features.is_first_round is True

    def test_invalid_round_number_raises(self):
        with pytest.raises(ValueError):
            DerivedFeatures(
                round_number=5,
                is_first_round=False,
                category_quota_combo="gn_ai",
                institute_type="govt",
                state_quota_indicator=False,
                year_index=0,
                seat_count_log=4.615,
            )


class TestTargets:
    def test_no_target_ready_default(self):
        targets = Targets()
        assert targets.target_ready is False
        assert targets.target_readiness_reason == "NO_TARGET_READY"
        assert targets.closing_rank is None

    def test_target_ready_with_value(self):
        targets = Targets(
            closing_rank=5000,
            target_version="targets_v1",
            target_ready=True,
            target_readiness_reason="READY",
        )
        assert targets.target_ready is True
        assert targets.closing_rank == 5000


class TestProvenance:
    def test_valid_provenance(self):
        prov = Provenance(
            source_file_id="mcc_seat_matrix_2025_a1b2c3d4",
            file_checksum="a" * 64,
            source_url="https://mcc.nic.in/data.csv",
            parser_version="mcc_etl_v1",
            retrieval_timestamp=datetime.now(timezone.utc),
            contract_version="1.1.0",
            adapter_version="adapter_v1",
            transformation_version="modelling_dataset_v1",
            feature_version="features_v1",
            quality_gate_version="quality_gates_v1",
        )
        assert prov.source_file_id == "mcc_seat_matrix_2025_a1b2c3d4"

    def test_invalid_checksum_raises(self):
        with pytest.raises(ValueError):
            Provenance(
                source_file_id="test",
                file_checksum="invalid",
                source_url="https://test.com",
                parser_version="v1",
                retrieval_timestamp=datetime.now(timezone.utc),
                contract_version="1.0.0",
                adapter_version="v1",
                transformation_version="v1",
                feature_version="v1",
                quality_gate_version="v1",
            )


class TestTemporalMetadata:
    def test_valid_temporal_metadata(self):
        tm = TemporalMetadata(
            prediction_time=datetime.now(timezone.utc),
            latest_allowed_year=2024,
            latest_allowed_round=RoundType.ROUND_1,
            feature_computation_timestamp=datetime.now(timezone.utc),
        )
        assert tm.latest_allowed_year == 2024


class TestModellingRecord:
    def test_valid_record(self):
        facts = SourceFacts(
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
        )
        features = DerivedFeatures(
            round_number=1,
            is_first_round=True,
            category_quota_combo="gn_ai",
            institute_type="govt",
            state_quota_indicator=False,
            year_index=0,
            seat_count_log=4.615,
        )
        targets = Targets()
        prov = Provenance(
            source_file_id="test_id",
            file_checksum="a" * 64,
            source_url="https://test.com",
            parser_version="v1",
            retrieval_timestamp=datetime.now(timezone.utc),
            contract_version="1.0.0",
            adapter_version="v1",
            transformation_version="v1",
            feature_version="v1",
            quality_gate_version="v1",
        )
        temporal = TemporalMetadata(
            prediction_time=datetime.now(timezone.utc),
            latest_allowed_year=2024,
            latest_allowed_round=RoundType.ROUND_1,
            feature_computation_timestamp=datetime.now(timezone.utc),
        )

        record = ModellingRecord(
            source_facts=facts,
            derived_features=features,
            targets=targets,
            provenance=prov,
            temporal_metadata=temporal,
            dataset_version="abc123",
            record_id="rec123",
        )
        assert record.record_id == "rec123"
        assert record.dataset_version == "abc123"


class TestDatasetVersion:
    def test_compute_record_id_deterministic(self):
        facts = SourceFacts(
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
        )
        features = DerivedFeatures(
            round_number=1,
            is_first_round=True,
            category_quota_combo="gn_ai",
            institute_type="govt",
            state_quota_indicator=False,
            year_index=0,
            seat_count_log=4.615,
        )
        targets = Targets()
        prov = Provenance(
            source_file_id="test_id",
            file_checksum="a" * 64,
            source_url="https://test.com",
            parser_version="v1",
            retrieval_timestamp=datetime.now(timezone.utc),
            contract_version="1.0.0",
            adapter_version="v1",
            transformation_version="v1",
            feature_version="v1",
            quality_gate_version="v1",
        )
        temporal = TemporalMetadata(
            prediction_time=datetime.now(timezone.utc),
            latest_allowed_year=2024,
            latest_allowed_round=RoundType.ROUND_1,
            feature_computation_timestamp=datetime.now(timezone.utc),
        )
        record = ModellingRecord(
            source_facts=facts,
            derived_features=features,
            targets=targets,
            provenance=prov,
            temporal_metadata=temporal,
            dataset_version="abc123",
            record_id="rec123",
        )

        id1 = compute_record_id(record)
        id2 = compute_record_id(record)
        assert id1 == id2
        assert len(id1) == 16

    def test_compute_dataset_version_deterministic(self):
        source_ids = ["file1_a1b2c3", "file2_d4e5f6"]
        v1 = compute_dataset_version(source_ids, "trans_v1", "feat_v1", "qual_v1")
        v2 = compute_dataset_version(source_ids, "trans_v1", "feat_v1", "qual_v1")
        assert v1 == v2
        assert len(v1) == 16

    def test_dataset_version_changes_with_inputs(self):
        v1 = compute_dataset_version(["file1"], "trans_v1", "feat_v1", "qual_v1")
        v2 = compute_dataset_version(["file2"], "trans_v1", "feat_v1", "qual_v1")
        assert v1 != v2

        v3 = compute_dataset_version(["file1"], "trans_v2", "feat_v1", "qual_v1")
        assert v1 != v3


class TestModellingDatasetContract:
    def test_valid_contract(self):
        contract = ModellingDatasetContract(
            dataset_version="abc123",
            created_timestamp=datetime.now(timezone.utc),
            source_file_ids=["file1", "file2"],
            source_checksums={"file1": "a"*64, "file2": "b"*64},
            transformation_version="trans_v1",
            feature_version="feat_v1",
            quality_gate_version="qual_v1",
            quality_gate_results={},
            row_count=1000,
            column_count=50,
            year_range=(2025, 2025),
            authorities=[AuthorityType.MCC],
            target_variables=["closing_rank"],
            schema_hash="def456",
            modelling_ready=False,
            temporal_validation_blocked=True,
            target_readiness="NO_TARGET_READY",
        )
        assert contract.modelling_ready is False
        assert contract.temporal_validation_blocked is True
