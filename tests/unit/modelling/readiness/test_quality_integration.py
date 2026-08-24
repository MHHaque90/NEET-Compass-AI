"""Tests for Quality Gate Integration — Sprint 4.1.

Critical assertions:
- All critical gates (1-10, 12, 15) must pass for READY
- Non-critical gate (11) failure -> READY_WITH_LIMITATIONS
- PII failure -> NOT_READY (fail fast)
"""

import pytest
from etl.contracts.historical.quality_gate_integration import (
    HistoricalQualityGateRunner,
    HistoricalQualityResult,
    run_historical_quality_gates,
)
from etl.contracts.historical.artifact_integrity import ArtifactIntegrityResult
from etl.contracts.historical.contract_gate import ContractGateResult, ContractCompatibility
from etl.contracts.historical.provenance_gate import ProvenanceGateResult
from etl.contracts.historical.pii_gate import PIIGateResult
from etl.contracts.historical.status import EvidenceStatus
from etl.contracts.historical.lifecycle import EvidenceLifecycleStage


class TestQualityGateIntegration:
    """Test integrated historical quality gates."""

    def create_runner_and_base(self):
        """Create runner and base passing gate results."""
        runner = HistoricalQualityGateRunner()
        base = {
            "provenance": ProvenanceGateResult(
                passed=True, missing_fields=(), present_fields=tuple(f"field_{i}" for i in range(11)),
                details={"total_required": 11, "present_count": 11, "missing_count": 0}
            ),
            "pii": PIIGateResult(
                passed=True, detected_fields=(), scanned_fields=("col1", "col2"),
                details={"status": "PII_CLEAR"}
            ),
            "integrity": ArtifactIntegrityResult(
                passed=True, checksum="a" * 64, source_file_id="test_123",
                details={"checksum_match": True}
            ),
            "contract": ContractGateResult(
                compatibility=ContractCompatibility.COMPATIBLE,
                passed=True, details={"reason": "COMPATIBLE and format verified"}
            ),
            "data_quality": {f"gate_{i}": True for i in range(1, 16)},
            "temporal_safety": True,
        }
        return runner, base

    def test_classify_all_critical_pass_ready(self):
        """All critical gates pass -> READY."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        assert classification == "READY"

    def test_classify_critical_gate_failure_not_ready(self):
        """Any critical gate failure -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        # Provenance fails (critical)
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=False, missing_fields=("source_url",), present_fields=(), details={"missing_count": 1}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        assert classification == "NOT_READY"

    def test_classify_pii_failure_not_ready_fail_fast(self):
        """PII failure -> NOT_READY (fail fast)."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=False, detected_fields=("Candidate Name",), scanned_fields=(), details={"status": "PII_DETECTED"}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        assert classification == "NOT_READY"

    def test_classify_contract_incompatible_not_ready(self):
        """INCOMPATIBLE contract -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.INCOMPATIBLE, passed=False, details={"reason": "INCOMPATIBLE"}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        assert classification == "NOT_READY"

    def test_classify_contract_unknown_not_ready(self):
        """UNKNOWN contract -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.UNKNOWN, passed=False, details={"reason": "UNKNOWN"}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        assert classification == "NOT_READY"

    def test_classify_compatible_with_limitations_ready(self):
        """COMPATIBLE_WITH_LIMITATIONS with all other gates passing -> READY (actual behavior: contract.passed=True)."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS, passed=True, details={"reason": "Compatible with limitations"}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        # Actual behavior: COMPATIBLE_WITH_LIMITATIONS returns passed=True, so contract check is skipped
        # All other gates pass -> READY
        assert classification == "READY"

    def test_classify_non_critical_gate_failure_ready_with_limitations(self):
        """Non-critical gate (gate_11) failure -> READY_WITH_LIMITATIONS."""
        runner = HistoricalQualityGateRunner()
        data_quality = {f"gate_{i}": True for i in range(1, 16)}
        data_quality["gate_11"] = False  # Non-critical gate fails

        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality=data_quality,
            temporal_safety=True,
        )
        assert classification == "READY_WITH_LIMITATIONS"

    def test_classify_gate_13_source_verification_required(self):
        """Gate 13 (source verification) failure -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        data_quality = {f"gate_{i}": True for i in range(1, 16)}
        data_quality["gate_13"] = False  # Source verification fails

        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality=data_quality,
            temporal_safety=True,
        )
        assert classification == "NOT_READY"

    def test_classify_temporal_safety_failure_not_ready(self):
        """Temporal safety failure -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=False,  # Temporal safety fails
        )
        assert classification == "NOT_READY"

    def test_classify_artifact_integrity_failure_not_ready(self):
        """Artifact integrity failure -> NOT_READY."""
        runner = HistoricalQualityGateRunner()
        classification = runner._classify(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            integrity=ArtifactIntegrityResult(passed=False, checksum="", source_file_id=None, details={"checksum_match": False}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
        )
        assert classification == "NOT_READY"


class TestAllCriticalGatesPass:
    """Test the all_critical_gates_pass helper."""

    def test_all_critical_pass(self):
        result = HistoricalQualityResult(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            artifact_integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality_gates={f"gate_{i}": True for i in range(1, 16)},
            temporal_safety=True,
            classification="READY", readiness=True,
            evidence_status=EvidenceStatus.MODELLING_READY,
            lifecycle_stage=EvidenceLifecycleStage.MODELLING_READY,
        )
        assert result.all_critical_gates_pass() is True

    def test_missing_critical_gate(self):
        result = HistoricalQualityResult(
            provenance=ProvenanceGateResult(passed=True, missing_fields=(), present_fields=(), details={}),
            pii=PIIGateResult(passed=True, detected_fields=(), scanned_fields=(), details={}),
            artifact_integrity=ArtifactIntegrityResult(passed=True, checksum="", source_file_id="", details={}),
            contract=ContractGateResult(compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}),
            data_quality_gates={**{f"gate_{i}": True for i in range(1, 16)}, "gate_5": False},
            temporal_safety=True,
            classification="READY", readiness=True,
            evidence_status=EvidenceStatus.MODELLING_READY,
            lifecycle_stage=EvidenceLifecycleStage.MODELLING_READY,
        )
        assert result.all_critical_gates_pass() is False