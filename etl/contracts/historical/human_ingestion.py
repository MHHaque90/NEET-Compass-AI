"""Human Artifact Ingestion — Sprint 4.1.

Thin orchestrator for submitting a legitimately obtained historical artifact.
Accepts: local artifact path, source URL, authority, year, dataset type, round,
retrieval timestamp, SHA-256 (optional — will be computed if not provided).

Runs the existing verification pipeline:
1. SHA-256 computation/verification
2. PII screening on column headers
3. Contract compatibility check
4. Provenance completeness
5. Artifact integrity

Returns a classification result — NEVER promotes without evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from etl.contracts.canonical import SourceMetadata
from etl.contracts.historical.artifact_integrity import (
    ArtifactIntegrity,
    ArtifactIntegrityResult,
)
from etl.contracts.historical.contract_gate import (
    ContractCompatibility,
    ContractGate,
    ContractGateResult,
)
from etl.contracts.historical.lifecycle import EvidenceLifecycleStage
from etl.contracts.historical.manifest import EvidenceManifest, create_manifest
from etl.contracts.historical.pii_gate import PIIGate, PIIGateResult
from etl.contracts.historical.provenance_gate import (
    ProvenanceGate,
    ProvenanceGateResult,
)
from etl.contracts.historical.status import EvidenceStatus


@dataclass(frozen=True)
class IngestionInput:
    """Input for human artifact ingestion.

    All fields are required except provided_sha256 (computed if missing).
    """

    artifact_path: str  # Local path to the artifact file
    source_url: str  # Exact download URL
    authority: str  # e.g., "Medical Counselling Committee"
    year: int  # Counselling year (e.g., 2024)
    dataset_type: str  # "seat_matrix" or "allotments"
    round: str  # e.g., "Round 1", "Round 3"
    retrieval_timestamp: str  # UTC ISO 8601
    provided_sha256: str | None = None  # Optional: verify against computed
    course: str = "MBBS+BDS+NURSING"
    quota: str = "ALL_INDIA"
    parser_version: str = ""
    contract_version: str = ""
    limitations: list[str] | None = None
    notes: str = ""


@dataclass(frozen=True)
class IngestionResult:
    """Result of human artifact ingestion verification.

    Does NOT modify any registry. Returns classification for maintainer review.
    """

    # Core identification
    source_authority: str
    counselling_year: int
    dataset_type: str
    round: str

    # Verification results
    artifact_integrity: ArtifactIntegrityResult
    pii_result: PIIGateResult
    contract_result: ContractGateResult
    provenance_result: ProvenanceGateResult

    # Derived
    evidence_manifest: EvidenceManifest
    format_status: str  # FORMAT_VERIFIED, FORMAT_UNKNOWN, FORMAT_MISMATCH
    evidence_status: EvidenceStatus
    lifecycle_stage: EvidenceLifecycleStage
    modelling_readiness: str  # READY, READY_WITH_LIMITATIONS, NOT_READY

    # Summary
    all_gates_passed: bool
    blocking_reasons: tuple[str, ...]
    warnings: tuple[str, ...]

    # Metadata
    ingestion_timestamp: str


class HumanArtifactIngestor:
    """Processes a human-supplied historical artifact through the verification pipeline."""

    def __init__(
        self,
        pii_gate: PIIGate | None = None,
        contract_gate: ContractGate | None = None,
        provenance_gate: ProvenanceGate | None = None,
        artifact_integrity: ArtifactIntegrity | None = None,
    ):
        self.pii_gate = pii_gate or PIIGate()
        self.contract_gate = contract_gate or ContractGate()
        self.provenance_gate = provenance_gate or ProvenanceGate()
        self.artifact_integrity = artifact_integrity

    def _read_artifact_headers(self, artifact_path: str) -> tuple[str, list[str], int]:
        """Read artifact file, return (mime_type, column_headers, file_size).

        Supports CSV and XLSX. PDF requires pdfplumber (not included here).
        """
        path = Path(artifact_path)
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")

        file_size = path.stat().st_size
        suffix = path.suffix.lower()

        if suffix == ".csv":
            import csv

            with path.open(newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
            mime_type = "text/csv"
        elif suffix in (".xlsx", ".xls"):
            try:
                import openpyxl  # type: ignore[import-untyped]

                wb = openpyxl.load_workbook(path, read_only=True)
                ws = wb.active
                headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                wb.close()
            except ImportError as err:
                raise RuntimeError("openpyxl required for XLSX files") from err
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif suffix == ".pdf":
            # PDF requires pdfplumber; caller should convert to CSV first or provide headers
            raise NotImplementedError(
                "PDF parsing not implemented. Convert to CSV first or provide headers manually."
            )
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

        return mime_type, [str(h).strip() for h in headers if h is not None], file_size

    def ingest(self, input_: IngestionInput) -> IngestionResult:
        """Run the complete verification pipeline on a human-supplied artifact.

        This does NOT write to any registry or modify any config.
        It returns a complete IngestionResult for maintainer review.
        """
        # 1. Read artifact and compute/verify SHA-256
        path = Path(input_.artifact_path)
        artifact_bytes = path.read_bytes()

        # Build ArtifactIntegrity with source_id inferred from authority
        source_id = input_.authority.lower().replace(" ", "_").replace(",", "")
        if "mcc" in source_id:
            source_id = "mcc_ug_archive"
        elif "maharashtra" in source_id or "cetcell" in source_id:
            source_id = "mcc_state_maharashtra"
        elif "karnataka" in source_id or "kea" in source_id:
            source_id = "mcc_state_karnataka"
        elif "uttar" in source_id or "upmu" in source_id:
            source_id = "mcc_state_uttar_pradesh"
        else:
            source_id = f"{source_id}_archive"

        if self.artifact_integrity is None:
            self.artifact_integrity = ArtifactIntegrity(
                source_id=source_id,
                dataset=input_.dataset_type,
                effective_year=input_.year,
            )

        integrity_result = self.artifact_integrity.verify(
            artifact_bytes,
            expected_checksum=input_.provided_sha256,
        )

        # 2. Read column headers for PII screening
        mime_type, headers, file_size = self._read_artifact_headers(input_.artifact_path)

        # 3. Run PII gate on column headers
        pii_result = self.pii_gate.validate(headers)

        # 4. Build SourceMetadata for provenance gate
        source_metadata = SourceMetadata(
            source_id=source_id,
            authority=input_.authority,
            dataset=input_.dataset_type,
            effective_year=input_.year,
            publication_version=input_.round,
            contract_version=input_.contract_version,
            retrieval_timestamp=input_.retrieval_timestamp,
            source_file_id=integrity_result.source_file_id or "",
            file_checksum=integrity_result.checksum,
            parser_version=input_.parser_version or f"{source_id}_parser_v1",
            source_url=input_.source_url,
        )

        provenance_result = self.provenance_gate.validate(source_metadata)

        # 5. Determine contract compatibility
        # If contract_version is provided and matches known contract, assume COMPATIBLE
        # Otherwise UNKNOWN (requires manual format inspection)
        if input_.contract_version:
            format_verified = True
            compat = ContractCompatibility.COMPATIBLE
        else:
            format_verified = False
            compat = ContractCompatibility.UNKNOWN

        contract_result = self.contract_gate.validate(
            compat,
            format_verified=format_verified,
            limitations=input_.limitations or [],
        )

        # 6. Determine format status
        format_status = "FORMAT_VERIFIED" if input_.contract_version else "FORMAT_UNKNOWN"

        # 7. Determine PII status
        pii_status = "PII_CLEAR" if pii_result.passed else "PII_DETECTED"

        # 8. Build EvidenceManifest
        manifest = create_manifest(
            source_metadata=source_metadata,
            artifact_filename=path.name,
            mime_type=mime_type,
            file_size=file_size,
            sha256=integrity_result.checksum,
            retrieval_method="MANUAL_BROWSER",
            format_status=format_status,
            pii_status=pii_status,
            validation_status="NOT_VALIDATED",  # Quality gates not run here
            modelling_readiness="NOT_READY",  # Will be updated below
            limitations=input_.limitations or [],
            notes=input_.notes,
        )

        # 9. Determine evidence status and lifecycle stage
        blocking_reasons = []
        warnings = []

        if not integrity_result.passed:
            blocking_reasons.append("ARTIFACT_INTEGRITY_FAILED")
        if not pii_result.passed:
            blocking_reasons.append("PII_DETECTED")
        if not provenance_result.passed:
            blocking_reasons.append("PROVENANCE_INCOMPLETE")
            missing = ", ".join(provenance_result.missing_fields)
            warnings.append(f"Missing provenance fields: {missing}")
        if not contract_result.passed:
            if contract_result.compatibility == ContractCompatibility.UNKNOWN:
                blocking_reasons.append("CONTRACT_COMPATIBILITY_UNKNOWN")
            elif contract_result.compatibility == ContractCompatibility.INCOMPATIBLE:
                blocking_reasons.append("CONTRACT_INCOMPATIBLE")
            else:
                blocking_reasons.append("CONTRACT_NOT_VERIFIED")

        # 10. Determine modelling readiness
        if blocking_reasons:
            modelling_readiness = "NOT_READY"
        elif contract_result.compatibility == ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS:
            modelling_readiness = "READY_WITH_LIMITATIONS"
        else:
            modelling_readiness = "NOT_READY"  # Cannot be READY without quality gates + temporal

        # Map to evidence status
        if modelling_readiness == "READY":
            evidence_status = EvidenceStatus.MODELLING_READY
            lifecycle_stage = EvidenceLifecycleStage.MODELLING_READY
        elif modelling_readiness == "READY_WITH_LIMITATIONS":
            evidence_status = EvidenceStatus.READY_WITH_LIMITATIONS
            lifecycle_stage = EvidenceLifecycleStage.QUALITY_GATES_PASSED
        elif "PII_DETECTED" in blocking_reasons:
            evidence_status = EvidenceStatus.PII_DETECTED
            lifecycle_stage = EvidenceLifecycleStage.PII_SCREENED
        elif "CONTRACT_COMPATIBILITY_UNKNOWN" in blocking_reasons:
            evidence_status = EvidenceStatus.CONTRACT_UNKNOWN
            lifecycle_stage = EvidenceLifecycleStage.CONTRACT_CHECKED
        elif "CONTRACT_INCOMPATIBLE" in blocking_reasons:
            evidence_status = EvidenceStatus.CONTRACT_INCOMPATIBLE
            lifecycle_stage = EvidenceLifecycleStage.BLOCKED_CONTRACT_INCOMPATIBLE
        elif "PROVENANCE_INCOMPLETE" in blocking_reasons:
            evidence_status = EvidenceStatus.NOT_VERIFIED
            lifecycle_stage = EvidenceLifecycleStage.PROVENANCE_COMPLETE
        else:
            evidence_status = EvidenceStatus.NOT_VERIFIED
            lifecycle_stage = EvidenceLifecycleStage.FORMAT_INSPECTED

        # Update manifest with final classification
        manifest = EvidenceManifest(
            **{
                **manifest.to_dict(),
                "modelling_readiness": modelling_readiness,
                "evidence_status": evidence_status.value,
                "lifecycle_stage": lifecycle_stage,
                "validation_status": "NOT_VALIDATED",
            }
        )

        return IngestionResult(
            source_authority=input_.authority,
            counselling_year=input_.year,
            dataset_type=input_.dataset_type,
            round=input_.round,
            artifact_integrity=integrity_result,
            pii_result=pii_result,
            contract_result=contract_result,
            provenance_result=provenance_result,
            evidence_manifest=manifest,
            format_status=format_status,
            evidence_status=evidence_status,
            lifecycle_stage=lifecycle_stage,
            modelling_readiness=modelling_readiness,
            all_gates_passed=len(blocking_reasons) == 0,
            blocking_reasons=tuple(blocking_reasons),
            warnings=tuple(warnings),
            ingestion_timestamp=datetime.now(UTC).isoformat(),
        )


def ingest_historical_artifact(
    artifact_path: str,
    source_url: str,
    authority: str,
    year: int,
    dataset_type: str,
    round_: str,
    retrieval_timestamp: str,
    provided_sha256: str | None = None,
    course: str = "MBBS+BDS+NURSING",
    quota: str = "ALL_INDIA",
    parser_version: str = "",
    contract_version: str = "",
    limitations: list[str] | None = None,
    notes: str = "",
) -> IngestionResult:
    """Convenience function for human artifact ingestion.

    Args:
        artifact_path: Local path to the artifact file (CSV, XLSX).
        source_url: Exact URL from which the artifact was downloaded.
        authority: Official authority name (e.g., "Medical Counselling Committee").
        year: NEET UG counselling year (e.g., 2024).
        dataset_type: "seat_matrix" or "allotments".
        round_: Counselling round (e.g., "Round 1", "Round 3").
        retrieval_timestamp: UTC ISO 8601 timestamp of download.
        provided_sha256: Optional SHA-256 to verify against computed hash.
        course: Course coverage string.
        quota: "ALL_INDIA" or "STATE_QUOTA".
        parser_version: Parser version identifier.
        contract_version: Contract version if known (e.g., "1.1.0").
        limitations: Known limitations of this artifact.
        notes: Additional notes.

    Returns:
        IngestionResult with complete verification details.

    """
    input_ = IngestionInput(
        artifact_path=artifact_path,
        source_url=source_url,
        authority=authority,
        year=year,
        dataset_type=dataset_type,
        round=round_,
        retrieval_timestamp=retrieval_timestamp,
        provided_sha256=provided_sha256,
        course=course,
        quota=quota,
        parser_version=parser_version,
        contract_version=contract_version,
        limitations=limitations or [],
        notes=notes,
    )

    ingestor = HumanArtifactIngestor()
    return ingestor.ingest(input_)


__all__ = [
    "HumanArtifactIngestor",
    "IngestionInput",
    "IngestionResult",
    "ingest_historical_artifact",
]
