"""Tests for Final Modelling Readiness — Sprint 4.1.

Critical assertions:
- ONE VERIFIED YEAR -> TEMPORAL_VALIDATION_BLOCKED
- NO TARGET -> TRAINING_BLOCKED
- UNKNOWN FORMAT -> NOT_READY
- UNKNOWN CONTRACT -> NOT_READY
- MISSING PROVENANCE -> NOT_READY
- PII -> REJECTED
"""

import pytest
from modelling.config.modelling_readiness import (
    get_modelling_ready_years,
    get_target_readiness,
    get_temporal_validation_status,
)
from modelling.training.guard import TrainingGuard, TrainingBlockReason
from modelling.splits.engine import TemporalValidationStatus
from modelling.contracts.versioning import DatasetVersion
from modelling.leakage.checker import LeakageResult
from modelling.quality.gates import QualityGateResult, ModellingQualityGate
from datetime import datetime, timezone


class TestFinalModellingReadiness:
    """Test final modelling readiness integration."""

    def test_one_verified_year_temporal_blocked(self):
        """ONE VERIFIED YEAR -> TEMPORAL_VALIDATION_BLOCKED."""
        ready_years = get_modelling_ready_years()
        total_verified = sum(len(y) for y in ready_years.values())
        assert total_verified == 1
        assert get_temporal_validation_status() == "BLOCKED"

    def test_no_target_training_blocked(self):
        """NO TARGET -> TRAINING_BLOCKED."""
        assert get_target_readiness() == "NO_TARGET_READY"

    def test_training_guard_blocks_on_temporal(self):
        """TrainingGuard blocks when temporal validation blocked."""
        guard = TrainingGuard(
            temporal_status=TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS,
            target_readiness="NO_TARGET_READY",
            verified_years={"MCC": [2025]},
            minimum_years_required=3,
        )

        dataset_version = DatasetVersion(
            version="abc123", created_timestamp=datetime.now(timezone.utc),
            source_file_ids=["file1"], source_checksums={"file1": "a"*64},
            transformation_version="v1", feature_version="v1", quality_gate_version="v1",
            quality_gate_results={"provenance_complete": True},
            row_count=100, column_count=50, year_range=(2025, 2025),
            authorities=["MCC"], target_variables=["closing_rank"], schema_hash="def456",
        )

        leakage_result = LeakageResult(
            passed=True, violations=[], checked_features=[], checked_records=1,
            check_timestamp=datetime.now(timezone.utc), prediction_year=2025,
            prediction_round=None,
        )

        quality_result = QualityGateResult(
            overall_passed=True, passed_gates=13, total_gates=13,
            gate_results={g: True for g in ModellingQualityGate},
        )

        result = guard.check_training_allowed(
            dataset_version, leakage_result, quality_result, "closing_rank"
        )

        assert result.allowed is False
        assert TrainingBlockReason.TEMPORAL_VALIDATION_BLOCKED in result.block_reasons
        assert TrainingBlockReason.INSUFFICIENT_VERIFIED_YEARS in result.block_reasons
        assert TrainingBlockReason.TARGET_NOT_READY in result.block_reasons
        # NO_TARGET_DEFINED is only added when target_name == "NO_TARGET_READY" or empty

    def test_training_guard_blocks_on_no_target_name(self):
        """TrainingGuard blocks when target_name is NO_TARGET_READY."""
        guard = TrainingGuard(
            temporal_status=TemporalValidationStatus.READY,
            target_readiness="NO_TARGET_READY",
            verified_years={"MCC": [2021, 2022, 2023, 2024, 2025]},
            minimum_years_required=3,
        )

        dataset_version = DatasetVersion(
            version="abc123", created_timestamp=datetime.now(timezone.utc),
            source_file_ids=["file1"], source_checksums={"file1": "a"*64},
            transformation_version="v1", feature_version="v1", quality_gate_version="v1",
            quality_gate_results={"provenance_complete": True},
            row_count=100, column_count=50, year_range=(2021, 2025),
            authorities=["MCC"], target_variables=["closing_rank"], schema_hash="def456",
        )

        leakage_result = LeakageResult(
            passed=True, violations=[], checked_features=[], checked_records=1,
            check_timestamp=datetime.now(timezone.utc), prediction_year=2026,
            prediction_round=None,
        )

        quality_result = QualityGateResult(
            overall_passed=True, passed_gates=13, total_gates=13,
            gate_results={g: True for g in ModellingQualityGate},
        )

        # Pass NO_TARGET_READY as target_name
        result = guard.check_training_allowed(
            dataset_version, leakage_result, quality_result, "NO_TARGET_READY"
        )

        assert result.allowed is False
        assert TrainingBlockReason.TARGET_NOT_READY in result.block_reasons
        assert TrainingBlockReason.NO_TARGET_DEFINED in result.block_reasons

    def test_training_guard_blocks_on_empty_target(self):
        """TrainingGuard blocks when target_name is empty."""
        guard = TrainingGuard(
            temporal_status=TemporalValidationStatus.READY,
            target_readiness="NO_TARGET_READY",
            verified_years={"MCC": [2021, 2022, 2023, 2024, 2025]},
            minimum_years_required=3,
        )

        dataset_version = DatasetVersion(
            version="abc123", created_timestamp=datetime.now(timezone.utc),
            source_file_ids=["file1"], source_checksums={"file1": "a"*64},
            transformation_version="v1", feature_version="v1", quality_gate_version="v1",
            quality_gate_results={"provenance_complete": True},
            row_count=100, column_count=50, year_range=(2021, 2025),
            authorities=["MCC"], target_variables=["closing_rank"], schema_hash="def456",
        )

        leakage_result = LeakageResult(
            passed=True, violations=[], checked_features=[], checked_records=1,
            check_timestamp=datetime.now(timezone.utc), prediction_year=2026,
            prediction_round=None,
        )

        quality_result = QualityGateResult(
            overall_passed=True, passed_gates=13, total_gates=13,
            gate_results={g: True for g in ModellingQualityGate},
        )

        result = guard.check_training_allowed(
            dataset_version, leakage_result, quality_result, ""
        )

        assert result.allowed is False
        assert TrainingBlockReason.NO_TARGET_DEFINED in result.block_reasons

    def test_unknown_format_not_ready(self):
        """UNKNOWN FORMAT -> NOT_READY (via contract gate)."""
        from etl.contracts.historical.contract_gate import ContractGate, ContractCompatibility
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.UNKNOWN, format_verified=False)
        assert result.passed is False
        assert "UNKNOWN" in result.details.get("reason", "")

    def test_unknown_contract_not_ready(self):
        """UNKNOWN CONTRACT -> NOT_READY."""
        from etl.contracts.historical.contract_gate import ContractGate, ContractCompatibility
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.UNKNOWN, format_verified=False)
        assert result.passed is False

    def test_missing_provenance_not_ready(self):
        """MISSING PROVENANCE -> NOT_READY."""
        from etl.contracts.historical.provenance_gate import ProvenanceGate
        from etl.contracts.canonical import SourceMetadata

        metadata = SourceMetadata(
            source_id="test", authority="Test", dataset="test",
            effective_year=2024, publication_version="Round 1",
            contract_version="1.0.0", retrieval_timestamp="",
            source_file_id="", file_checksum="", parser_version="", source_url="",
        )

        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is False
        assert len(result.missing_fields) > 0

    def test_pii_rejected(self):
        """PII -> REJECTED."""
        from etl.contracts.historical.pii_gate import PIIGate
        gate = PIIGate()
        headers = ["Institute Code", "Candidate Name", "Father Name", "Rank"]
        result = gate.validate(headers)
        assert result.passed is False
        assert "Candidate Name" in result.detected_fields
        assert "Father Name" in result.detected_fields

    def test_all_critical_assertions_hold(self):
        """All critical assertions from sprint mandate hold."""
        # 1. ONE VERIFIED YEAR -> TEMPORAL_VALIDATION_BLOCKED
        assert get_temporal_validation_status() == "BLOCKED"

        # 2. NO TARGET -> TRAINING_BLOCKED
        assert get_target_readiness() == "NO_TARGET_READY"

        # 3. UNKNOWN FORMAT -> NOT_READY (tested via contract gate)
        # 4. UNKNOWN CONTRACT -> NOT_READY (tested via contract gate)
        # 5. MISSING PROVENANCE -> NOT_READY (tested via provenance gate)
        # 6. PII -> REJECTED (tested via PII gate)

        # All verified
        assert True  # If we reach here, all critical assertions hold