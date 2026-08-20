"""Historical Quality Gate Integration — Sprint 3.9.

Integrates the evidence lifecycle with the existing 15 Sprint 3.6 quality gates.
Does not duplicate their logic. The final readiness decision must be deterministic.

Conceptually:
source evidence
+ artifact integrity
+ format compatibility
+ PII safety
+ provenance
+ contract compatibility
+ data quality
+ temporal safety
= modelling readiness

No individual gate may silently override another.
"""

from __future__ import annotations

from dataclasses import dataclass

from etl.contracts.canonical import SourceMetadata
from etl.contracts.historical.artifact_integrity import ArtifactIntegrity, ArtifactIntegrityResult
from etl.contracts.historical.contract_gate import (
    ContractCompatibility,
    ContractGate,
    ContractGateResult,
)
from etl.contracts.historical.lifecycle import EvidenceLifecycleStage
from etl.contracts.historical.manifest import EvidenceManifest
from etl.contracts.historical.pii_gate import PIIGate, PIIGateResult
from etl.contracts.historical.provenance_gate import ProvenanceGate, ProvenanceGateResult
from etl.contracts.historical.status import EvidenceStatus


@dataclass(frozen=True)
class HistoricalQualityResult:
    """Aggregated result of all historical quality gates."""

    # Individual gate results
    provenance: ProvenanceGateResult
    pii: PIIGateResult
    artifact_integrity: ArtifactIntegrityResult
    contract: ContractGateResult
    data_quality_gates: dict[str, bool]  # The 15 Sprint 3.6 gates
    temporal_safety: bool

    # Final classification
    classification: str  # READY, READY_WITH_LIMITATIONS, NOT_READY
    readiness: bool

    # Evidence
    evidence_status: EvidenceStatus
    lifecycle_stage: EvidenceLifecycleStage

    def __bool__(self) -> bool:
        return self.readiness

    def all_critical_gates_pass(self) -> bool:
        """Check if all critical gates pass (gates 1-10, 12-15 from Sprint 3.6)."""
        critical_gates = {
            "gate_1", "gate_2", "gate_3", "gate_4", "gate_5", "gate_6",
            "gate_7", "gate_8", "gate_9", "gate_10", "gate_12", "gate_13",
            "gate_14", "gate_15",
        }
        return all(self.data_quality_gates.get(g, False) for g in critical_gates)


class HistoricalQualityGateRunner:
    """Runs all historical quality gates and produces deterministic classification.

    This integrates the evidence lifecycle gates with the existing
    15 Sprint 3.6 data quality gates.
    """

    def __init__(
        self,
        provenance_gate: ProvenanceGate | None = None,
        pii_gate: PIIGate | None = None,
        contract_gate: ContractGate | None = None,
        artifact_integrity: ArtifactIntegrity | None = None,
    ):
        self.provenance_gate = provenance_gate or ProvenanceGate()
        self.pii_gate = pii_gate or PIIGate()
        self.contract_gate = contract_gate or ContractGate()
        self.artifact_integrity = artifact_integrity

    def run(
        self,
        manifest: EvidenceManifest,
        source_metadata: SourceMetadata,
        artifact_bytes: bytes,
        data_quality_results: dict[str, bool],
        temporal_safety: bool,
    ) -> HistoricalQualityResult:
        """Run all quality gates for a historical artifact.

        Args:
            manifest: Evidence manifest.
            source_metadata: Provenance metadata.
            artifact_bytes: Raw artifact bytes for integrity check.
            data_quality_results: Results of 15 Sprint 3.6 quality gates.
            temporal_safety: Whether temporal leakage boundaries are preserved.

        Returns:
            HistoricalQualityResult with final classification.

        """
        # Run provenance gate
        provenance_result = self.provenance_gate.validate(source_metadata)

        # Run PII gate on manifest fields
        manifest_fields = list(manifest.to_dict().keys())
        pii_result = self.pii_gate.validate(manifest_fields)

        # Run artifact integrity
        if self.artifact_integrity:
            integrity_result = self.artifact_integrity.verify(
                artifact_bytes,
                expected_checksum=manifest.sha256,
            )
        else:
            integrity_result = ArtifactIntegrityResult(
                passed=False,
                checksum="",
                source_file_id=None,
                details={"error": "ArtifactIntegrity not configured"},
            )

        # Run contract gate
        contract_compat = ContractCompatibility(manifest.format_status) if manifest.format_status in ContractCompatibility._value2member_map_ else ContractCompatibility.UNKNOWN
        contract_result = self.contract_gate.validate(
            contract_compat,
            format_verified=(manifest.format_status == "FORMAT_VERIFIED"),
            limitations=manifest.limitations,
        )

        # Determine classification
        classification = self._classify(
            provenance_result,
            pii_result,
            integrity_result,
            contract_result,
            data_quality_results,
            temporal_safety,
        )

        readiness = classification == "READY"

        # Determine evidence status
        evidence_status = self._determine_evidence_status(
            provenance_result,
            pii_result,
            integrity_result,
            contract_result,
            classification,
        )

        # Determine lifecycle stage
        lifecycle_stage = self._determine_lifecycle_stage(
            classification,
            provenance_result,
            pii_result,
            contract_result,
        )

        return HistoricalQualityResult(
            provenance=provenance_result,
            pii=pii_result,
            artifact_integrity=integrity_result,
            contract=contract_result,
            data_quality_gates=data_quality_results,
            temporal_safety=temporal_safety,
            classification=classification,
            readiness=readiness,
            evidence_status=evidence_status,
            lifecycle_stage=lifecycle_stage,
        )

    def _classify(
        self,
        provenance: ProvenanceGateResult,
        pii: PIIGateResult,
        integrity: ArtifactIntegrityResult,
        contract: ContractGateResult,
        data_quality: dict[str, bool],
        temporal_safety: bool,
    ) -> str:
        """Determine final classification from all gate results.

        Classification logic (mirrors Sprint 3.6):
        - READY: All critical gates pass
        - READY_WITH_LIMITATIONS: Critical gates 1-10 pass, non-critical documented
        - NOT_READY: Any critical gate fails
        """
        # Gate 13: Source verification (from data quality)
        if not data_quality.get("gate_13", False):
            return "NOT_READY"

        # Gate 14: PII exclusion (fail fast)
        if not pii.passed:
            return "NOT_READY"

        # Provenance completeness
        if not provenance.passed:
            return "NOT_READY"

        # Artifact integrity
        if not integrity.passed:
            return "NOT_READY"

        # Contract compatibility
        if not contract.passed:
            if contract.compatibility == ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS:
                return "READY_WITH_LIMITATIONS"
            return "NOT_READY"

        # Data quality critical gates (1-10, 12, 15)
        critical_gates = {
            "gate_1", "gate_2", "gate_3", "gate_4", "gate_5", "gate_6",
            "gate_7", "gate_8", "gate_9", "gate_10", "gate_12", "gate_15",
        }
        critical_pass = all(data_quality.get(g, False) for g in critical_gates)
        if not critical_pass:
            return "NOT_READY"

        # Temporal safety
        if not temporal_safety:
            return "NOT_READY"

        # Non-critical gates (11, 13 already checked)
        non_critical = {"gate_11"}
        non_critical_pass = all(data_quality.get(g, False) for g in non_critical)

        if non_critical_pass:
            return "READY"
        else:
            return "READY_WITH_LIMITATIONS"

    def _determine_evidence_status(
        self,
        provenance: ProvenanceGateResult,
        pii: PIIGateResult,
        integrity: ArtifactIntegrityResult,
        contract: ContractGateResult,
        classification: str,
    ) -> EvidenceStatus:
        """Determine evidence status from gate results."""
        if classification == "READY":
            return EvidenceStatus.MODELLING_READY
        if classification == "READY_WITH_LIMITATIONS":
            return EvidenceStatus.READY_WITH_LIMITATIONS

        # Not ready - determine specific blocking reason
        if not provenance.passed:
            return EvidenceStatus.NOT_VERIFIED
        if not pii.passed:
            return EvidenceStatus.PII_DETECTED
        if not integrity.passed:
            return EvidenceStatus.NOT_VERIFIED
        if not contract.passed:
            if contract.compatibility == ContractCompatibility.INCOMPATIBLE:
                return EvidenceStatus.CONTRACT_INCOMPATIBLE
            if contract.compatibility == ContractCompatibility.UNKNOWN:
                return EvidenceStatus.NOT_VERIFIED
            return EvidenceStatus.NOT_READY

        return EvidenceStatus.NOT_READY

    def _determine_lifecycle_stage(
        self,
        classification: str,
        provenance: ProvenanceGateResult,
        pii: PIIGateResult,
        contract: ContractGateResult,
    ) -> EvidenceLifecycleStage:
        """Determine lifecycle stage from results."""
        if classification == "READY":
            return EvidenceLifecycleStage.MODELLING_READY
        if classification == "READY_WITH_LIMITATIONS":
            return EvidenceLifecycleStage.QUALITY_GATES_PASSED

        # Find the blocking stage
        if not provenance.passed:
            return EvidenceLifecycleStage.PROVENANCE_COMPLETE  # Blocked before provenance complete
        if not pii.passed:
            return EvidenceLifecycleStage.PII_SCREENED
        if not contract.passed:
            if contract.compatibility == ContractCompatibility.INCOMPATIBLE:
                return EvidenceLifecycleStage.BLOCKED_CONTRACT_INCOMPATIBLE
            if contract.compatibility == ContractCompatibility.UNKNOWN:
                return EvidenceLifecycleStage.CONTRACT_CHECKED
            return EvidenceLifecycleStage.CONTRACT_CHECKED

        return EvidenceLifecycleStage.VALIDATED


def run_historical_quality_gates(
    manifest: EvidenceManifest,
    source_metadata: SourceMetadata,
    artifact_bytes: bytes,
    data_quality_results: dict[str, bool],
    temporal_safety: bool,
) -> HistoricalQualityResult:
    """Convenience function to run all historical quality gates."""
    runner = HistoricalQualityGateRunner()
    return runner.run(manifest, source_metadata, artifact_bytes, data_quality_results, temporal_safety)
