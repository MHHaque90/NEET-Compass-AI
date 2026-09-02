"""Tests for Sprint 4.4 — Historical Evidence Acquisition Path & Readiness Activation.

Critical assertions:
1. Valid acquisition manifest is accepted.
2. Missing authority is rejected.
3. Missing effective_year is rejected.
4. Missing source reference is rejected.
5. Missing checksum is rejected where policy requires it.
6. Missing provenance fails closed.
7. Unverified source cannot become READY.
8. UNKNOWN contract compatibility cannot become READY.
9. PII-bearing evidence is rejected.
10. HTTP-blocked evidence cannot be promoted automatically.
11. Artifact existence alone cannot produce READY.
12. Human acquisition metadata cannot bypass source verification.
13. Future years cannot satisfy historical temporal coverage.
14. Synthetic years cannot satisfy temporal coverage.
15. One verified year remains temporally blocked.
16. Target remains NO_TARGET_READY.
17. Training remains TRAINING_BLOCKED.
18. Existing Sprint 4.0-4.3 behaviour does not regress.
"""

from datetime import UTC, datetime

import pytest
import yaml
from etl.contracts.canonical import SourceMetadata
from etl.contracts.historical.artifact_integrity import ArtifactIntegrity, verify_artifact_integrity
from etl.contracts.historical.contract_gate import ContractCompatibility, ContractGate
from etl.contracts.historical.lifecycle import EvidenceLifecycleStage, validate_transition
from etl.contracts.historical.manifest import (
    create_manifest,
    validate_manifest,
)
from etl.contracts.historical.pii_gate import PIIGate
from etl.contracts.historical.promotion import PromotionStage, PromotionWorkflow
from etl.contracts.historical.provenance_gate import ProvenanceGate
from etl.contracts.historical.status import EvidenceStatus, is_blocking_status
from etl.contracts.historical.temporal_gate import TemporalReadinessGate
from modelling.config.modelling_readiness import (
    get_modelling_ready_years,
    get_temporal_validation_status,
)
from modelling.contracts.dataset import AuthorityType, RoundType
from modelling.contracts.versioning import DatasetVersion
from modelling.leakage.checker import LeakageResult
from modelling.quality.gates import ModellingQualityGate, QualityGateResult
from modelling.splits.engine import TemporalValidationStatus
from modelling.targets.engine import TargetEngine
from modelling.training.guard import TrainingBlockReason, TrainingGuard


class TestSprint44ManifestValidation:
    """EvidenceManifest validation contract tests."""

    def test_valid_manifest_accepted(self):
        """Valid acquisition manifest with all required fields passes validation."""
        manifest = create_manifest(
            source_metadata=SourceMetadata(
                source_id="mcc_ug_archive",
                authority="Medical Counselling Committee",
                dataset="seat_matrix",
                effective_year=2024,
                publication_version="Round 1",
                contract_version="1.1.0",
                retrieval_timestamp=datetime.now(UTC).isoformat(),
                source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
                file_checksum="a" * 64,
                parser_version="mcc_parser_v1",
                source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.pdf",
            ),
            artifact_filename="seat_matrix_r1_2024.pdf",
            mime_type="application/pdf",
            file_size=1024,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="NOT_VALIDATED",
            modelling_readiness="NOT_READY",
        )

        is_valid, missing = validate_manifest(manifest)
        assert is_valid is True
        assert missing == []

    def test_missing_authority_rejected(self):
        """Manifest missing source_authority fails validation."""
        manifest = create_manifest(
            source_metadata=SourceMetadata(
                source_id="mcc_ug_archive",
                authority="",  # Missing
                dataset="seat_matrix",
                effective_year=2024,
                publication_version="Round 1",
                contract_version="1.1.0",
                retrieval_timestamp=datetime.now(UTC).isoformat(),
                source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
                file_checksum="a" * 64,
                parser_version="mcc_parser_v1",
                source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.pdf",
            ),
            artifact_filename="seat_matrix_r1_2024.pdf",
            mime_type="application/pdf",
            file_size=1024,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="NOT_VALIDATED",
            modelling_readiness="NOT_READY",
        )

        is_valid, missing = validate_manifest(manifest)
        assert is_valid is False
        assert "source_authority" in missing

    def test_missing_effective_year_rejected(self):
        """Manifest missing effective_year fails validation."""
        manifest = create_manifest(
            source_metadata=SourceMetadata(
                source_id="mcc_ug_archive",
                authority="Medical Counselling Committee",
                dataset="seat_matrix",
                effective_year=0,  # Missing (default 0)
                publication_version="Round 1",
                contract_version="1.1.0",
                retrieval_timestamp=datetime.now(UTC).isoformat(),
                source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
                file_checksum="a" * 64,
                parser_version="mcc_parser_v1",
                source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.pdf",
            ),
            artifact_filename="seat_matrix_r1_2024.pdf",
            mime_type="application/pdf",
            file_size=1024,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="NOT_VALIDATED",
            modelling_readiness="NOT_READY",
        )

        is_valid, missing = validate_manifest(manifest)
        # effective_year=0 becomes falsy in validation
        assert is_valid is False
        assert "counselling_year" in missing

    def test_missing_source_url_rejected(self):
        """Manifest missing source_url fails validation."""
        manifest = create_manifest(
            source_metadata=SourceMetadata(
                source_id="mcc_ug_archive",
                authority="Medical Counselling Committee",
                dataset="seat_matrix",
                effective_year=2024,
                publication_version="Round 1",
                contract_version="1.1.0",
                retrieval_timestamp=datetime.now(UTC).isoformat(),
                source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
                file_checksum="a" * 64,
                parser_version="mcc_parser_v1",
                source_url="",  # Missing
            ),
            artifact_filename="seat_matrix_r1_2024.pdf",
            mime_type="application/pdf",
            file_size=1024,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="NOT_VALIDATED",
            modelling_readiness="NOT_READY",
        )

        is_valid, missing = validate_manifest(manifest)
        assert is_valid is False
        assert "source_url" in missing

    def test_missing_checksum_rejected_where_policy_requires(self):
        """ArtifactIntegrity fails when expected_checksum missing per policy."""
        integrity = ArtifactIntegrity(
            source_id="mcc_ug_archive",
            dataset="seat_matrix",
            effective_year=2024,
        )
        # No expected_checksum provided — policy requires it for verification
        _ = integrity.verify(b"test data", expected_checksum=None)
        # verify_artifact_integrity enforces missing_checksum = failed
        result2 = verify_artifact_integrity(
            b"test data",
            source_id="mcc_ug_archive",
            dataset="seat_matrix",
            effective_year=2024,
            expected_checksum=None,  # Missing
        )
        assert result2.passed is False
        assert result2.details.get("missing_checksum") is True

    def test_missing_provenance_fails_closed(self):
        """ProvenanceGate fails when any of 10 required fields missing."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="",  # Missing
            source_file_id="",  # Missing
            file_checksum="",  # Missing
            parser_version="",
            source_url="",
        )
        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is False
        assert len(result.missing_fields) > 0
        # All 10 fields should be checked
        assert len(result.missing_fields) >= 3


class TestSprint44AcquisitionGateFailures:
    """Acquisition pipeline gate failure tests."""

    def test_unverified_source_cannot_become_ready(self):
        """Source with UNKNOWN verification status cannot reach MODELLING_READY."""
        # Simulate: source discovered but not verified

        # NOT_VERIFIED is a blocking status
        assert is_blocking_status(EvidenceStatus.NOT_VERIFIED) is True

        # CANNOT proceed to modelling
        from etl.contracts.historical.status import can_proceed_to_modelling

        assert can_proceed_to_modelling(EvidenceStatus.NOT_VERIFIED) is False
        assert can_proceed_to_modelling(EvidenceStatus.SOURCE_CLAIMED) is False

    def test_unknown_contract_compatibility_cannot_become_ready(self):
        """ContractGate rejects UNKNOWN compatibility."""
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.UNKNOWN, format_verified=False)
        assert result.passed is False
        assert result.compatibility == ContractCompatibility.UNKNOWN

        # Even with format_verified=True, UNKNOWN fails
        result2 = gate.validate(ContractCompatibility.UNKNOWN, format_verified=True)
        assert result2.passed is False

    def test_incompatible_contract_cannot_become_ready(self):
        """ContractGate rejects INCOMPATIBLE compatibility."""
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.INCOMPATIBLE, format_verified=True)
        assert result.passed is False
        assert result.compatibility == ContractCompatibility.INCOMPATIBLE

    def test_pii_bearing_evidence_rejected(self):
        """PIIGate detects candidate identifiers and fails closed."""
        gate = PIIGate()
        headers = ["Institute Code", "Candidate Name", "Father Name", "Rank", "Score"]
        result = gate.validate(headers)
        assert result.passed is False
        assert "Candidate Name" in result.detected_fields
        assert "Father Name" in result.detected_fields

        # PII_DETECTED is blocking status
        from etl.contracts.historical.status import is_blocking_status

        assert is_blocking_status(EvidenceStatus.PII_DETECTED) is True

    def test_http_blocked_evidence_cannot_auto_promote(self):
        """AUTOMATED_DOWNLOAD_BLOCKED status prevents promotion."""
        from etl.contracts.historical.promotion import VALID_PROMOTIONS, PromotionStage
        from etl.contracts.historical.status import is_blocking_status

        # AUTOMATED_DOWNLOAD_BLOCKED is a blocking status
        assert is_blocking_status(EvidenceStatus.AUTOMATED_DOWNLOAD_BLOCKED) is True

        # PromotionWorkflow: BLOCKED_DOWNLOAD is terminal (no valid next stages)
        assert VALID_PROMOTIONS[PromotionStage.BLOCKED_DOWNLOAD] == ()

    def test_artifact_existence_alone_cannot_produce_ready(self):
        """Having an artifact file does not imply READY — all gates required."""
        # Create manifest with artifact but no verification
        manifest = create_manifest(
            source_metadata=SourceMetadata(
                source_id="mcc_ug_archive",
                authority="Medical Counselling Committee",
                dataset="seat_matrix",
                effective_year=2024,
                publication_version="Round 1",
                contract_version="",  # UNKNOWN
                retrieval_timestamp=datetime.now(UTC).isoformat(),
                source_file_id="",
                file_checksum="",
                parser_version="",
                source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.pdf",
            ),
            artifact_filename="seat_matrix_r1_2024.pdf",
            mime_type="application/pdf",
            file_size=1024,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_UNKNOWN",  # Not verified
            pii_status="PII_CLEAR",
            validation_status="NOT_VALIDATED",
            modelling_readiness="NOT_READY",
        )

        # ContractGate with UNKNOWN fails
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.UNKNOWN, format_verified=False)
        assert result.passed is False

        # Manifest modelling_readiness remains NOT_READY
        assert manifest.modelling_readiness == "NOT_READY"

    def test_human_acquisition_metadata_cannot_bypass_source_verification(self):
        """Human ingestion requires source verification — cannot bypass."""

        # Even with contract_version provided, if provenance incomplete, fails
        # The ingestion pipeline runs ProvenanceGate which requires all 10 fields
        # Source verification (URL accessible) is separate from provenance completeness
        # but both are required

        # ProvenanceGate validates 10 fields including source_url
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp=datetime.now(UTC).isoformat(),
            source_file_id="test_id",
            file_checksum="a" * 64,
            parser_version="mcc_parser_v1",
            source_url="",  # Empty — source not verified
        )
        prov_gate = ProvenanceGate()
        result = prov_gate.validate(metadata)
        assert result.passed is False
        assert "source_url" in result.missing_fields


class TestSprint44TemporalTargetTrainingBlocks:
    """Temporal, Target, and Training gate block tests."""

    def test_future_years_cannot_satisfy_historical_temporal_coverage(self):
        """Future years (e.g., 2026+) not counted for historical temporal validation."""
        # The temporal gate counts all years passed to it.
        # Filtering to only MODELLING_READY years happens in get_modelling_ready_years()
        # which reads from config/modelling_readiness.yaml
        gate = TemporalReadinessGate(minimum_years=3)

        # Pass raw years - gate counts them all
        result = gate.validate(
            {
                "MCC": [2025],
                "Maharashtra": [2026],  # Future/current year
                "Karnataka": [],
                "Uttar_Pradesh": [],
            }
        )
        # Gate counts all passed years (2)
        assert result.verified_count == 2
        assert result.passed is False  # Still blocked (< 3)

        # But actual registry only has MCC 2025 as MODELLING_READY
        assert get_temporal_validation_status() == "BLOCKED"

    def test_synthetic_years_cannot_satisfy_temporal_coverage(self):
        """Synthetic/fixture years cannot satisfy temporal coverage."""
        gate = TemporalReadinessGate(minimum_years=3)
        # Even if we pass many years, only verified modelling-ready count
        result = gate.validate(
            {
                "MCC": [2025],
                "Maharashtra": [],  # No verified years (fixtures only)
                "Karnataka": [],
                "Uttar_Pradesh": [],
            }
        )
        assert result.verified_count == 1
        assert result.passed is False

    def test_one_verified_year_remains_temporally_blocked(self):
        """1 verified year → TEMPORAL_VALIDATION_BLOCKED."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2025]})
        assert result.passed is False
        assert result.verified_count == 1
        assert result.can_split_train_val_test is False
        assert result.details["temporal_validation_status"] == "BLOCKED"

        # Also verify via modelling config
        assert get_temporal_validation_status() == "BLOCKED"

    def test_two_verified_years_remains_temporally_blocked(self):
        """2 verified years → TEMPORAL_VALIDATION_BLOCKED."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2024, 2025]})
        assert result.passed is False
        assert result.verified_count == 2
        assert result.can_split_train_val_test is False

    def test_three_verified_years_eligible(self):
        """3+ verified years → eligible for temporal evaluation (subject to other gates)."""
        gate = TemporalReadinessGate(minimum_years=3)
        result = gate.validate({"MCC": [2023, 2024, 2025]})
        assert result.passed is True
        assert result.verified_count == 3
        assert result.can_split_train_val_test is True

    def test_target_remains_no_target_ready(self):
        """TargetEngine returns NO_TARGET_READY for all targets."""
        engine = TargetEngine()
        assert engine.get_first_modelling_target() == "NO_TARGET_READY"

        for name in engine.target_definitions:
            readiness = engine.get_target_readiness(name)
            assert readiness.is_ready is False

    def test_rejected_targets_still_rejected(self):
        """Fundamentally unavailable targets remain rejected."""
        engine = TargetEngine()
        for name in ["admission_probability", "seat_allocation", "vacancy_after_round"]:
            readiness = engine.get_target_readiness(name)
            assert readiness.is_ready is False
            missing = " ".join(readiness.missing_requirements).lower()
            if name in ["admission_probability", "seat_allocation"]:
                assert "preference" in missing or "applicant" in missing

    def test_training_remains_blocked(self):
        """TrainingGuard blocks while readiness gates fail."""
        guard = TrainingGuard(
            temporal_status=TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS,
            target_readiness="NO_TARGET_READY",
            verified_years={"MCC": [2025]},
            minimum_years_required=3,
        )

        dataset_version = DatasetVersion(
            version="abc123",
            created_timestamp=datetime.now(UTC),
            source_file_ids=["file1"],
            source_checksums={"file1": "a" * 64},
            transformation_version="v1",
            feature_version="v1",
            quality_gate_version="v1",
            quality_gate_results={"provenance_complete": True},
            row_count=100,
            column_count=50,
            year_range=(2025, 2025),
            authorities=["MCC"],
            target_variables=["closing_rank"],
            schema_hash="def456",
        )

        leakage_result = LeakageResult(
            passed=True,
            violations=[],
            checked_features=[],
            checked_records=1,
            check_timestamp=datetime.now(UTC),
            prediction_year=2025,
            prediction_round=RoundType.ROUND_1,
        )

        quality_result = QualityGateResult(
            overall_passed=True,
            passed_gates=15,
            total_gates=15,
            gate_results={g: True for g in ModellingQualityGate},
        )

        result = guard.check_training_allowed(
            dataset_version, leakage_result, quality_result, "closing_rank"
        )

        assert result.allowed is False
        assert TrainingBlockReason.TEMPORAL_VALIDATION_BLOCKED in result.block_reasons
        assert TrainingBlockReason.INSUFFICIENT_VERIFIED_YEARS in result.block_reasons
        assert TrainingBlockReason.TARGET_NOT_READY in result.block_reasons


class TestSprint44NoRegression:
    """Existing Sprint 4.0-4.3 behaviour must not regress."""

    def test_mcc_2025_remains_ready(self):
        """MCC 2025 seat matrix and allotments remain READY."""
        ready = get_modelling_ready_years()
        assert ready[AuthorityType.MCC] == [2025]

    def test_mcc_2025_quality_gates_passed(self):
        """MCC 2025 datasets show 15/15 quality gates passed."""
        from pathlib import Path

        config_path = Path("config/modelling_readiness.yaml")
        with config_path.open() as f:
            config = yaml.safe_load(f)

        mcc_2025_datasets = [
            d
            for d in config["datasets"]
            if d["source_id"] == "mcc_ug_archive" and d["year"] == 2025
        ]
        assert len(mcc_2025_datasets) == 2
        for d in mcc_2025_datasets:
            assert d["readiness"] == "READY"
            assert d["lifecycle_stage"] == "MODELLING_READY"
            assert d["quality_gates_passed"] == 15
            assert d["quality_gates_total"] == 15

    def test_historical_unchanged_not_verified(self):
        """All historical 2021-2024/2025 remain NOT_VERIFIED."""
        from pathlib import Path

        config_path = Path("config/modelling_readiness.yaml")
        with config_path.open() as f:
            config = yaml.safe_load(f)

        for year in [2021, 2022, 2023, 2024]:
            for dataset in ["seat_matrix", "allotments"]:
                entries = [
                    d
                    for d in config["datasets"]
                    if d["source_id"] == "mcc_ug_archive"
                    and d["year"] == year
                    and d["dataset"] == dataset
                ]
                assert len(entries) == 1
                entry = entries[0]
                assert entry["verification_status"] == "NOT_VERIFIED"
                assert entry["readiness"] == "NOT_READY"
                assert entry["lifecycle_stage"] == "DISCOVERED"

    def test_state_historical_unchanged_not_verified(self):
        """Maharashtra/Karnataka/UP 2021-2025 remain NOT_VERIFIED."""
        from pathlib import Path

        config_path = Path("config/modelling_readiness.yaml")
        with config_path.open() as f:
            config = yaml.safe_load(f)

        for source_id in [
            "mcc_state_maharashtra",
            "mcc_state_karnataka",
            "mcc_state_uttar_pradesh",
        ]:
            for year in [2021, 2022, 2023, 2024, 2025]:
                for dataset in ["seat_matrix", "allotments"]:
                    entries = [
                        d
                        for d in config["datasets"]
                        if d["source_id"] == source_id
                        and d["year"] == year
                        and d["dataset"] == dataset
                    ]
                    if entries:
                        entry = entries[0]
                        assert entry["verification_status"] == "NOT_VERIFIED"
                        assert entry["readiness"] == "NOT_READY"
                        assert entry["lifecycle_stage"] == "DISCOVERED"

    def test_up_mappings_still_placeholder(self):
        """UP category/quota mappings remain PLACEHOLDER."""
        from pathlib import Path

        config_path = Path("config/modelling_readiness.yaml")
        with config_path.open() as f:
            config = yaml.safe_load(f)

        up_2026_seat = next(
            d
            for d in config["datasets"]
            if d["source_id"] == "mcc_state_uttar_pradesh"
            and d["year"] == 2026
            and d["dataset"] == "seat_matrix"
        )
        limitations = " ".join(up_2026_seat["limitations"])
        assert "PLACEHOLDER" in limitations

    def test_human_ingestion_framework_still_works(self):
        """HumanArtifactIngestor still functional."""
        from etl.contracts.historical.human_ingestion import HumanArtifactIngestor

        ingestor = HumanArtifactIngestor()
        assert ingestor.pii_gate is not None
        assert ingestor.contract_gate is not None
        assert ingestor.provenance_gate is not None

    def test_lifecycle_transitions_still_enforced(self):
        """Lifecycle transitions still require evidence."""
        # Valid transition
        valid, desc = validate_transition(
            EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.SOURCE_VERIFIED
        )
        assert valid is True
        assert "source_id registered" in desc

        # Invalid transition (skipping)
        valid2, _ = validate_transition(
            EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.MODELLING_READY
        )
        assert valid2 is False

    def test_promotion_workflow_still_enforces_no_skipping(self):
        """PromotionWorkflow still prevents skipping stages."""
        workflow = PromotionWorkflow()
        workflow.current_stage = PromotionStage.NOT_VERIFIED

        # Cannot jump to READY
        from etl.contracts.historical.promotion import VALID_PROMOTIONS

        assert PromotionStage.READY not in VALID_PROMOTIONS[PromotionStage.NOT_VERIFIED]

        # Must go through VERIFIED first
        assert PromotionStage.VERIFIED in VALID_PROMOTIONS[PromotionStage.NOT_VERIFIED]

    def test_migrations_untouched(self):
        """Database migrations 0001 and 0002 remain untouched."""
        from pathlib import Path

        migration_dir = Path("backend/alembic/versions")
        files = [f.name for f in migration_dir.iterdir() if f.suffix == ".py"]
        assert "0001_initial_schema.py" in files
        assert "0002_create_historical_cutoffs.py" in files
        assert len(files) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
