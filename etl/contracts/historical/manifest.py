"""Evidence Manifest for Historical Artifacts — Sprint 3.9.

Machine-readable manifest capturing all evidence for a historical source artifact.
Reuses existing provenance infrastructure where possible.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from etl.contracts.canonical import SourceMetadata
from etl.contracts.historical.lifecycle import EvidenceLifecycleStage


class ManifestField(str, Enum):
    """Standard fields in the evidence manifest."""

    # Source identification
    SOURCE_AUTHORITY = "source_authority"
    SOURCE_URL = "source_url"
    SOURCE_IDENTIFIER = "source_identifier"
    DATASET_TYPE = "dataset_type"
    COUNSELLING_YEAR = "counselling_year"
    ROUND = "round"
    COURSE = "course"
    QUOTA = "quota"

    # Retrieval
    RETRIEVAL_METHOD = "retrieval_method"
    RETRIEVAL_TIMESTAMP = "retrieval_timestamp"
    RETRIEVAL_STATUS = "retrieval_status"

    # Verification
    VERIFICATION_STATUS = "verification_status"
    EVIDENCE_STATUS = "evidence_status"

    # Artifact
    ARTIFACT_FILENAME = "artifact_filename"
    MIME_TYPE = "mime_type"
    FILE_SIZE = "file_size"
    SHA256 = "sha256"
    SOURCE_FILE_ID = "source_file_id"

    # Contract & Parser
    CONTRACT_VERSION = "contract_version"
    PARSER_VERSION = "parser_version"
    FORMAT_STATUS = "format_status"

    # PII & Validation
    PII_STATUS = "pii_status"
    VALIDATION_STATUS = "validation_status"
    MODELLING_READINESS = "modelling_readiness"

    # Limitations & Notes
    LIMITATIONS = "limitations"
    NOTES = "notes"


@dataclass(frozen=True)
class EvidenceManifest:
    """Complete evidence manifest for a historical source artifact.

    This manifest captures all evidence needed to determine whether
    a historical artifact can be promoted to modelling readiness.
    """

    # Source identification (required)
    source_authority: str
    source_url: str
    source_identifier: str
    dataset_type: str
    counselling_year: int
    round: str
    course: str
    quota: str

    # Retrieval (required)
    retrieval_method: str
    retrieval_timestamp: str
    retrieval_status: str

    # Verification (required)
    verification_status: str
    evidence_status: str

    # Artifact (required)
    artifact_filename: str
    mime_type: str
    file_size: int
    sha256: str
    source_file_id: str

    # Contract & Parser (required)
    contract_version: str
    parser_version: str
    format_status: str

    # PII & Validation (required)
    pii_status: str
    validation_status: str
    modelling_readiness: str

    # Optional
    limitations: list[str] = field(default_factory=list)
    notes: str = ""

    # Internal tracking
    lifecycle_stage: EvidenceLifecycleStage | str = EvidenceLifecycleStage.DISCOVERED
    manifest_version: str = "1.0"
    created_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary for serialization."""
        lifecycle = self.lifecycle_stage
        if isinstance(lifecycle, EvidenceLifecycleStage):
            lifecycle = lifecycle.value

        return {
            "source_authority": self.source_authority,
            "source_url": self.source_url,
            "source_identifier": self.source_identifier,
            "dataset_type": self.dataset_type,
            "counselling_year": self.counselling_year,
            "round": self.round,
            "course": self.course,
            "quota": self.quota,
            "retrieval_method": self.retrieval_method,
            "retrieval_timestamp": self.retrieval_timestamp,
            "retrieval_status": self.retrieval_status,
            "verification_status": self.verification_status,
            "evidence_status": self.evidence_status,
            "artifact_filename": self.artifact_filename,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "sha256": self.sha256,
            "source_file_id": self.source_file_id,
            "contract_version": self.contract_version,
            "parser_version": self.parser_version,
            "format_status": self.format_status,
            "pii_status": self.pii_status,
            "validation_status": self.validation_status,
            "modelling_readiness": self.modelling_readiness,
            "limitations": self.limitations,
            "notes": self.notes,
            "lifecycle_stage": lifecycle,
            "manifest_version": self.manifest_version,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceManifest:
        """Create manifest from dictionary."""
        data = data.copy()
        if "lifecycle_stage" in data and isinstance(data["lifecycle_stage"], str):
            with suppress(ValueError, TypeError):
                data["lifecycle_stage"] = EvidenceLifecycleStage(data["lifecycle_stage"])
        return cls(**data)


REQUIRED_MANIFEST_FIELDS: set[str] = {
    "source_authority",
    "source_url",
    "source_identifier",
    "dataset_type",
    "counselling_year",
    "round",
    "course",
    "quota",
    "retrieval_method",
    "retrieval_timestamp",
    "retrieval_status",
    "verification_status",
    "evidence_status",
    "artifact_filename",
    "mime_type",
    "file_size",
    "sha256",
    "source_file_id",
    "contract_version",
    "parser_version",
    "format_status",
    "pii_status",
    "validation_status",
    "modelling_readiness",
}


def create_manifest(
    source_metadata: SourceMetadata | None,
    artifact_filename: str,
    mime_type: str,
    file_size: int,
    sha256: str,
    retrieval_method: str,
    format_status: str,
    pii_status: str,
    validation_status: str,
    modelling_readiness: str,
    limitations: list[str] | None = None,
    notes: str = "",
) -> EvidenceManifest:
    """Create an evidence manifest from existing provenance and artifact info.

    Args:
        source_metadata: Existing SourceMetadata from provenance system.
            If None, default values are used.
        artifact_filename: Name of the source artifact file.
        mime_type: MIME type of the artifact.
        file_size: File size in bytes.
        sha256: SHA-256 checksum of the artifact.
        retrieval_method: How the artifact was obtained (manual/automated/blocked).
        format_status: Result of format inspection.
        pii_status: Result of PII screening.
        validation_status: Result of data quality validation.
        modelling_readiness: Final readiness classification.
        limitations: Known limitations.
        notes: Additional notes.

    Returns:
        Complete EvidenceManifest.

    """
    if source_metadata is None:
        source_metadata = SourceMetadata(
            source_id="",
            authority="",
            dataset="",
            effective_year=0,
            publication_version="",
            contract_version="",
            retrieval_timestamp="",
            source_file_id="",
            file_checksum="",
            parser_version="",
            source_url="",
        )

    return EvidenceManifest(
        source_authority=source_metadata.authority,
        source_url=source_metadata.source_url or "",
        source_identifier=source_metadata.source_id,
        dataset_type=source_metadata.dataset,
        counselling_year=source_metadata.effective_year,
        round=source_metadata.publication_version,
        course="MBBS+BDS+NURSING" if source_metadata.authority == "MCC / DGHS" else "MBBS+BDS",
        quota="ALL_INDIA" if source_metadata.authority == "MCC / DGHS" else "STATE_QUOTA",
        retrieval_method=retrieval_method,
        retrieval_timestamp=source_metadata.retrieval_timestamp,
        retrieval_status="SUCCESS" if source_metadata.retrieval_timestamp else "BLOCKED",
        verification_status=source_metadata.authority.replace(" ", "_").upper() if source_metadata.authority else "",
        evidence_status="VERIFIED" if source_metadata.file_checksum else "NOT_VERIFIED",
        artifact_filename=artifact_filename,
        mime_type=mime_type,
        file_size=file_size,
        sha256=sha256,
        source_file_id=source_metadata.source_file_id or "",
        contract_version=source_metadata.contract_version,
        parser_version=source_metadata.parser_version or "",
        format_status=format_status,
        pii_status=pii_status,
        validation_status=validation_status,
        modelling_readiness=modelling_readiness,
        limitations=limitations or [],
        notes=notes,
    )


def validate_manifest(manifest: EvidenceManifest) -> tuple[bool, list[str]]:
    """Validate that an evidence manifest has all required fields.

    Args:
        manifest: The manifest to validate.

    Returns:
        Tuple of (is_valid, list_of_missing_fields).

    """
    data = manifest.to_dict()
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if not data.get(field)]
    return len(missing) == 0, missing
