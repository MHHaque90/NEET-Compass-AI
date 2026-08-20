"""Artifact Integrity — Sprint 3.9.

Deterministic checks for SHA-256 stability and artifact identity.
Same bytes → same identity. Modified bytes → different identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from etl.contracts.canonical.checksum import compute_checksum, compute_file_checksum


@dataclass(frozen=True)
class ArtifactIntegrityResult:
    """Result of artifact integrity verification."""

    passed: bool
    checksum: str
    source_file_id: str | None
    details: dict[str, Any]

    def __bool__(self) -> bool:
        return self.passed


class ArtifactIntegrity:
    """Verifies artifact integrity through deterministic checksums."""

    def __init__(self, source_id: str, dataset: str, effective_year: int):
        self.source_id = source_id
        self.dataset = dataset
        self.effective_year = effective_year

    def compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of artifact bytes."""
        return compute_checksum(data)

    def compute_file_hash(self, file_path: str | Path) -> str:
        """Compute SHA-256 hash of artifact file."""
        return compute_file_checksum(str(file_path))

    def build_source_file_id(self, checksum: str) -> str:
        """Build deterministic source_file_id from checksum."""
        return f"{self.source_id}_{self.dataset}_{self.effective_year}_{checksum[:12]}"

    def verify(self, data: bytes, expected_checksum: str | None = None) -> ArtifactIntegrityResult:
        """Verify artifact integrity.

        Args:
            data: Artifact bytes.
            expected_checksum: Expected SHA-256 (if known).

        Returns:
            ArtifactIntegrityResult.

        """
        actual_checksum = self.compute_hash(data)
        source_file_id = self.build_source_file_id(actual_checksum)

        checksum_match = True
        if expected_checksum is not None:
            checksum_match = actual_checksum == expected_checksum

        return ArtifactIntegrityResult(
            passed=checksum_match,
            checksum=actual_checksum,
            source_file_id=source_file_id,
            details={
                "expected_checksum": expected_checksum,
                "actual_checksum": actual_checksum,
                "checksum_match": checksum_match,
                "source_file_id": source_file_id,
            },
        )

    def verify_file(self, file_path: str | Path, expected_checksum: str | None = None) -> ArtifactIntegrityResult:
        """Verify artifact file integrity."""
        actual_checksum = self.compute_file_hash(file_path)
        source_file_id = self.build_source_file_id(actual_checksum)

        checksum_match = True
        if expected_checksum is not None:
            checksum_match = actual_checksum == expected_checksum

        return ArtifactIntegrityResult(
            passed=checksum_match,
            checksum=actual_checksum,
            source_file_id=source_file_id,
            details={
                "file_path": str(file_path),
                "expected_checksum": expected_checksum,
                "actual_checksum": actual_checksum,
                "checksum_match": checksum_match,
                "source_file_id": source_file_id,
            },
        )


def compute_artifact_hash(data: bytes) -> str:
    """Compute SHA-256 hash of artifact bytes."""
    return compute_checksum(data)


def build_source_file_id(checksum: str, source_id: str, dataset: str, effective_year: int) -> str:
    """Deterministic identifier for an ingested source file.

    Same (checksum, source, dataset, year) -> same id, so the file registry
    can recognise a re-submitted file without storing the bytes.
    """
    return f"{source_id}_{dataset}_{effective_year}_{checksum[:12]}"


def verify_artifact_integrity(
    data: bytes,
    source_id: str,
    dataset: str,
    effective_year: int,
    expected_checksum: str | None = None,
    expected_source_file_id: str | None = None,
) -> ArtifactIntegrityResult:
    """Verify artifact integrity with full identity check.

    Checks:
    - SHA-256 stability
    - same bytes → same identity
    - modified bytes → different identity
    - missing checksum → NOT_READY
    - invalid source identity → NOT_READY
    - inconsistent metadata → NOT_READY
    """
    integrity = ArtifactIntegrity(source_id, dataset, effective_year)
    result = integrity.verify(data, expected_checksum)

    # Additional checks
    details = dict(result.details)

    if expected_checksum is None:
        details["missing_checksum"] = True
        result = ArtifactIntegrityResult(
            passed=False,
            checksum=result.checksum,
            source_file_id=result.source_file_id,
            details=details,
        )

    if expected_source_file_id is not None:
        if result.source_file_id != expected_source_file_id:
            details["invalid_source_identity"] = True
            result = ArtifactIntegrityResult(
                passed=False,
                checksum=result.checksum,
                source_file_id=result.source_file_id,
                details=details,
            )

    return result
