"""Evidence Status Taxonomy — Sprint 3.9.

Audits existing Sprint 3.7/3.8 evidence taxonomy and defines the
minimal documented extension for the historical evidence lifecycle.

Existing statuses from historical-artifact-handling.md:
- VERIFIED
- SOURCE_URL_VERIFIED
- CHECKSUM_VERIFIED
- FORMAT_VERIFIED
- AUTOMATED_DOWNLOAD_BLOCKED
- ARCHIVE_INACCESSIBLE
- MAPPING_NOT_VERIFIED

Additional statuses needed for the lifecycle:
- SOURCE_CLAIMED
- SOURCE_VERIFIED
- ARTIFACT_UNAVAILABLE
- MANUALLY_RETRIEVED
- FORMAT_UNKNOWN
- FORMAT_MISMATCH
- PII_DETECTED
- PII_CLEAR
- CONTRACT_COMPATIBLE
- CONTRACT_INCOMPATIBLE
- VALIDATED
- MODELLING_READY
"""

from __future__ import annotations

from enum import Enum


class EvidenceStatus(str, Enum):
    """Comprehensive evidence status taxonomy.

    Combines existing Sprint 3.7/3.8 statuses with minimal
    documented extensions for the lifecycle.
    """

    # Source discovery
    SOURCE_CLAIMED = "SOURCE_CLAIMED"  # Claimed in config, no verification
    SOURCE_VERIFIED = "SOURCE_VERIFIED"  # Official URL accessible (HTTP 200)

    # Retrieval
    ARTIFACT_UNAVAILABLE = "ARTIFACT_UNAVAILABLE"  # Document not found on portal
    AUTOMATED_DOWNLOAD_BLOCKED = "AUTOMATED_DOWNLOAD_BLOCKED"  # HTTP 403/429 on automated
    MANUALLY_RETRIEVED = "MANUALLY_RETRIEVED"  # Human downloaded via browser
    RETRIEVED = "RETRIEVED"  # Successfully retrieved (any method)

    # Format
    FORMAT_VERIFIED = "FORMAT_VERIFIED"  # Schema matches contract expectations
    FORMAT_UNKNOWN = "FORMAT_UNKNOWN"  # No source document examined
    FORMAT_MISMATCH = "FORMAT_MISMATCH"  # Structure differs from contract

    # PII
    PII_DETECTED = "PII_DETECTED"  # Candidate identifiers found
    PII_CLEAR = "PII_CLEAR"  # No PII columns in canonical path
    PII_EXCLUDED = "PII_EXCLUDED"  # Entire document excluded (e.g., joined lists)

    # Contract
    CONTRACT_COMPATIBLE = "CONTRACT_COMPATIBLE"  # Reuses existing contract
    CONTRACT_COMPATIBLE_WITH_LIMITATIONS = "CONTRACT_COMPATIBLE_WITH_LIMITATIONS"  # Minor differences
    CONTRACT_INCOMPATIBLE = "CONTRACT_INCOMPATIBLE"  # Requires new contract version
    CONTRACT_UNKNOWN = "CONTRACT_UNKNOWN"  # No contract exists for this year

    # Validation
    VALIDATED = "VALIDATED"  # Passed data quality gates
    VALIDATED_WITH_LIMITATIONS = "VALIDATED_WITH_LIMITATIONS"  # Non-critical gates documented
    NOT_VALIDATED = "NOT_VALIDATED"  # Gates not run or failed

    # Modelling Readiness
    MODELLING_READY = "MODELLING_READY"  # All gates pass, temporal ready
    READY_WITH_LIMITATIONS = "READY_WITH_LIMITATIONS"  # Critical gates pass, non-critical documented
    NOT_READY = "NOT_READY"  # Any critical gate fails

    # Legacy statuses from Sprint 3.7/3.8 (preserved for compatibility)
    VERIFIED = "VERIFIED"  # Full provenance + fixture (if legal)
    SOURCE_URL_VERIFIED = "SOURCE_URL_VERIFIED"  # URL confirmed, not downloaded
    CHECKSUM_VERIFIED = "CHECKSUM_VERIFIED"  # Checksum known, not in repo
    ARCHIVE_INACCESSIBLE = "ARCHIVE_INACCESSIBLE"  # Archive page not found
    MAPPING_NOT_VERIFIED = "MAPPING_NOT_VERIFIED"  # Placeholder mappings (UP)
    NOT_VERIFIED = "NOT_VERIFIED"  # Config claims but zero repo evidence
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"  # Some evidence exists


# Mapping from legacy status to new taxonomy
LEGACY_STATUS_MAP: dict[str, EvidenceStatus] = {
    "VERIFIED": EvidenceStatus.VERIFIED,
    "SOURCE_URL_VERIFIED": EvidenceStatus.SOURCE_URL_VERIFIED,
    "CHECKSUM_VERIFIED": EvidenceStatus.CHECKSUM_VERIFIED,
    "FORMAT_VERIFIED": EvidenceStatus.FORMAT_VERIFIED,
    "AUTOMATED_DOWNLOAD_BLOCKED": EvidenceStatus.AUTOMATED_DOWNLOAD_BLOCKED,
    "ARCHIVE_INACCESSIBLE": EvidenceStatus.ARCHIVE_INACCESSIBLE,
    "MAPPING_NOT_VERIFIED": EvidenceStatus.MAPPING_NOT_VERIFIED,
    "NOT_VERIFIED": EvidenceStatus.NOT_VERIFIED,
    "PARTIALLY_VERIFIED": EvidenceStatus.PARTIALLY_VERIFIED,
}


def is_terminal_status(status: EvidenceStatus) -> bool:
    """Check if a status is terminal (no further progression expected)."""
    terminal_statuses = {
        EvidenceStatus.MODELLING_READY,
        EvidenceStatus.READY_WITH_LIMITATIONS,
        EvidenceStatus.NOT_READY,
        EvidenceStatus.ARCHIVE_INACCESSIBLE,
    }
    return status in terminal_statuses


def is_blocking_status(status: EvidenceStatus) -> bool:
    """Check if a status blocks further progression without manual intervention."""
    blocking_statuses = {
        EvidenceStatus.AUTOMATED_DOWNLOAD_BLOCKED,
        EvidenceStatus.ARCHIVE_INACCESSIBLE,
        EvidenceStatus.FORMAT_MISMATCH,
        EvidenceStatus.PII_DETECTED,
        EvidenceStatus.CONTRACT_INCOMPATIBLE,
        EvidenceStatus.MAPPING_NOT_VERIFIED,
        EvidenceStatus.NOT_VERIFIED,
    }
    return status in blocking_statuses


def requires_manual_intervention(status: EvidenceStatus) -> bool:
    """Check if a status requires human action to proceed."""
    manual_statuses = {
        EvidenceStatus.AUTOMATED_DOWNLOAD_BLOCKED,
        EvidenceStatus.ARCHIVE_INACCESSIBLE,
        EvidenceStatus.FORMAT_MISMATCH,
        EvidenceStatus.PII_DETECTED,
        EvidenceStatus.CONTRACT_INCOMPATIBLE,
        EvidenceStatus.MAPPING_NOT_VERIFIED,
    }
    return status in manual_statuses


def can_proceed_to_modelling(status: EvidenceStatus) -> bool:
    """Check if a status allows progression to modelling readiness."""
    allowed = {
        EvidenceStatus.VALIDATED,
        EvidenceStatus.VERIFIED,
        EvidenceStatus.FORMAT_VERIFIED,
        EvidenceStatus.PII_CLEAR,
        EvidenceStatus.CONTRACT_COMPATIBLE,
    }
    return status in allowed
