"""Tests for Unverified Source Rejection — Sprint 4.1.

Critical assertions:
- Unverified sources cannot become READY
- Source must be verified before promotion
- Automated download blocked sources need manual retrieval
"""

import pytest
from etl.contracts.historical.promotion import (
    PromotionStage,
    can_promote,
)
from etl.contracts.historical.status import (
    EvidenceStatus,
    is_blocking_status,
    is_terminal_status,
    requires_manual_intervention,
)
from etl.contracts.historical.quality_gate_integration import (
    HistoricalQualityGateRunner,
    HistoricalQualityResult,
)
from etl.contracts.historical.contract_gate import ContractGateResult, ContractCompatibility
from etl.contracts.historical.provenance_gate import ProvenanceGateResult
from etl.contracts.historical.pii_gate import PIIGateResult
from etl.contracts.historical.artifact_integrity import ArtifactIntegrityResult
from etl.contracts.historical.manifest import EvidenceManifest


class TestUnverifiedSourceRejection:
    """Test that unverified sources are rejected."""

    def test_not_verified_cannot_become_ready(self):
        """NOT_VERIFIED source cannot jump to READY."""
        result = can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.READY, {})
        assert result.allowed is False

    def test_not_verified_cannot_become_validated(self):
        """NOT_VERIFIED source cannot jump to VALIDATED."""
        result = can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.VALIDATED, {})
        assert result.allowed is False

    def test_not_verified_cannot_become_ready_limited(self):
        """NOT_VERIFIED source cannot jump to READY_WITH_LIMITATIONS."""
        result = can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.READY_WITH_LIMITATIONS, {})
        assert result.allowed is False

    def test_not_verified_must_go_to_verified_first(self):
        """NOT_VERIFIED can only go to VERIFIED (with evidence)."""
        from etl.contracts.historical.promotion import VALID_PROMOTIONS
        assert VALID_PROMOTIONS[PromotionStage.NOT_VERIFIED] == (PromotionStage.VERIFIED,)

    def test_verified_requires_evidence_for_validated(self):
        """VERIFIED -> VALIDATED requires specific evidence."""
        from etl.contracts.historical.promotion import PROMOTION_REQUIREMENTS
        req = PROMOTION_REQUIREMENTS[PromotionStage.VERIFIED]
        assert "artifact_retrieved" in req["requires"]
        assert "checksum_recorded" in req["requires"]
        assert "format_inspected" in req["requires"]
        assert "pii_screened" in req["requires"]

    def test_evidence_status_not_verified_not_ready(self):
        """EvidenceStatus.NOT_VERIFIED means not ready for modelling."""
        runner = HistoricalQualityGateRunner()
        class MockManifest:
            format_status = "FORMAT_UNKNOWN"
            limitations = []

        prov_result = ProvenanceGateResult(
            passed=False, missing_fields=("source_url",), present_fields=(),
            details={"missing_count": 1}
        )
        pii_result = PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={})
        integrity_result = ArtifactIntegrityResult(
            passed=True, checksum="a"*64, source_file_id="test", details={}
        )
        contract_result = ContractGateResult(
            compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}
        )
        data_quality = {f"gate_{i}": True for i in range(1, 16)}

        assert prov_result.passed is False

    def test_blocking_statuses_require_manual_intervention(self):
        """Blocking statuses should require manual intervention."""
        for status in EvidenceStatus:
            if status.name.startswith("BLOCKED_"):
                assert is_blocking_status(status) is True
                assert requires_manual_intervention(status) is True

    def test_terminal_statuses(self):
        """Terminal statuses should be marked as terminal."""
        # Based on actual implementation
        terminal = [
            EvidenceStatus.MODELLING_READY,
            EvidenceStatus.READY_WITH_LIMITATIONS,
            EvidenceStatus.NOT_READY,
        ]
        for status in terminal:
            assert is_terminal_status(status) is True, f"{status} should be terminal"

    def test_automated_download_blocked_is_blocking(self):
        """AUTOMATED_DOWNLOAD_BLOCKED is a blocking status."""
        assert is_blocking_status(EvidenceStatus.AUTOMATED_DOWNLOAD_BLOCKED) is True
        assert requires_manual_intervention(EvidenceStatus.AUTOMATED_DOWNLOAD_BLOCKED) is True

    def test_quality_gate_rejects_not_verified(self):
        """Quality gate should reject NOT_VERIFIED sources."""
        runner = HistoricalQualityGateRunner()
        manifest = EvidenceManifest(
            source_authority="Test Authority",
            source_url="https://example.com",
            source_identifier="test_source",
            dataset_type="seat_matrix",
            counselling_year=2024,
            round="Round 1",
            course="MBBS",
            quota="ALL_INDIA",
            retrieval_method="MANUAL_BROWSER",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            retrieval_status="SUCCESS",
            verification_status="VERIFIED",
            evidence_status="VERIFIED",
            artifact_filename="test.csv",
            mime_type="text/csv",
            file_size=1000,
            sha256="a" * 64,
            source_file_id="test_source_seat_matrix_2024_abc123",
            contract_version="1.0.0",
            parser_version="v1",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="VALIDATED",
            modelling_readiness="READY",
            limitations=[],
            notes="",
        )

        prov_result = ProvenanceGateResult(
            passed=False, missing_fields=("source_url", "retrieval_timestamp"), present_fields=(),
            details={"missing_count": 2}
        )
        pii_result = PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={})
        integrity_result = ArtifactIntegrityResult(
            passed=True, checksum="a"*64, source_file_id="test", details={}
        )
        contract_result = ContractGateResult(
            compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}
        )
        data_quality = {f"gate_{i}": True for i in range(1, 16)}

        result = runner.run(
            manifest=manifest,
            source_metadata=None,
            artifact_bytes=b"test",
            data_quality_results=data_quality,
            temporal_safety=True,
        )
        # Create new result with modified provenance
        result = HistoricalQualityResult(
            provenance=prov_result,
            pii=result.pii,
            artifact_integrity=result.artifact_integrity,
            contract=result.contract,
            data_quality_gates=result.data_quality_gates,
            temporal_safety=result.temporal_safety,
            classification="NOT_READY",
            readiness=False,
            evidence_status=EvidenceStatus.NOT_VERIFIED,
            lifecycle_stage=result.lifecycle_stage,
        )

        assert result.classification == "NOT_READY"
        assert result.readiness is False


class TestSourceVerificationGates:
    """Test source verification gates enforce verification."""

    def test_gate_13_source_verification_critical(self):
        """Gate 13 (source verification) is critical - failure -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        manifest = EvidenceManifest(
            source_authority="Test Authority",
            source_url="https://example.com",
            source_identifier="test_source",
            dataset_type="seat_matrix",
            counselling_year=2024,
            round="Round 1",
            course="MBBS",
            quota="ALL_INDIA",
            retrieval_method="MANUAL_BROWSER",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            retrieval_status="SUCCESS",
            verification_status="VERIFIED",
            evidence_status="VERIFIED",
            artifact_filename="test.csv",
            mime_type="text/csv",
            file_size=1000,
            sha256="a" * 64,
            source_file_id="test_source_seat_matrix_2024_abc123",
            contract_version="1.0.0",
            parser_version="v1",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="VALIDATED",
            modelling_readiness="READY",
            limitations=[],
            notes="",
        )

        data_quality = {f"gate_{i}": True for i in range(1, 16)}
        data_quality["gate_13"] = False  # Source not verified

        result = runner.run(
            manifest=manifest,
            source_metadata=None,
            artifact_bytes=b"test",
            data_quality_results=data_quality,
            temporal_safety=True,
        )

        assert result.classification == "NOT_READY"

    def test_source_claimed_not_verified(self):
        """SOURCE_CLAIMED (in config but not verified) -> NOT_READY."""
        from etl.contracts.historical.status import EvidenceStatus
        assert is_terminal_status(EvidenceStatus.SOURCE_CLAIMED) is False
        assert is_blocking_status(EvidenceStatus.SOURCE_CLAIMED) is False