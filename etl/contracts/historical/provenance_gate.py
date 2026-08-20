"""Provenance Gate — Sprint 3.9.

Deterministic validation for required provenance fields.
A historical dataset must not become modelling-ready unless the
required provenance fields exist.

Reuses the project's existing 10-field provenance taxonomy from
etl.contracts.canonical.SourceMetadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from etl.contracts.canonical import SourceMetadata

# The 10 required provenance fields from the existing architecture
REQUIRED_PROVENANCE_FIELDS: tuple[str, ...] = (
    "source_id",
    "authority",
    "dataset",
    "effective_year",
    "publication_version",
    "contract_version",
    "retrieval_timestamp",
    "source_file_id",
    "file_checksum",
    "parser_version",
    "source_url",
)


@dataclass(frozen=True)
class ProvenanceGateResult:
    """Result of provenance gate validation."""

    passed: bool
    missing_fields: tuple[str, ...]
    present_fields: tuple[str, ...]
    details: dict[str, Any]

    def __bool__(self) -> bool:
        return self.passed


class ProvenanceGate:
    """Validates provenance completeness for historical artifacts.

    A dataset must have all 10 provenance fields to pass.
    """

    def __init__(self, required_fields: tuple[str, ...] = REQUIRED_PROVENANCE_FIELDS):
        self.required_fields = required_fields

    def validate(self, metadata: SourceMetadata) -> ProvenanceGateResult:
        """Validate that all required provenance fields are present and non-empty.

        Args:
            metadata: SourceMetadata to validate.

        Returns:
            ProvenanceGateResult with pass/fail and details.

        """
        present = []
        missing = []

        for field in self.required_fields:
            value = getattr(metadata, field, None)
            if value is not None and value != "":
                present.append(field)
            else:
                missing.append(field)

        passed = len(missing) == 0

        return ProvenanceGateResult(
            passed=passed,
            missing_fields=tuple(missing),
            present_fields=tuple(present),
            details={
                "total_required": len(self.required_fields),
                "present_count": len(present),
                "missing_count": len(missing),
            },
        )

    def validate_dict(self, data: dict[str, Any]) -> ProvenanceGateResult:
        """Validate provenance from a dictionary (e.g., manifest or record)."""
        present = []
        missing = []

        for field in self.required_fields:
            value = data.get(field)
            if value is not None and value != "":
                present.append(field)
            else:
                missing.append(field)

        passed = len(missing) == 0

        return ProvenanceGateResult(
            passed=passed,
            missing_fields=tuple(missing),
            present_fields=tuple(present),
            details={
                "total_required": len(self.required_fields),
                "present_count": len(present),
                "missing_count": len(missing),
            },
        )


def validate_provenance(metadata: SourceMetadata) -> ProvenanceGateResult:
    """Convenience function to validate provenance."""
    gate = ProvenanceGate()
    return gate.validate(metadata)
