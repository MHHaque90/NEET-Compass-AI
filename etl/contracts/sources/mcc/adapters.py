"""Source adapters for MCC seat-matrix and allotment rows.

Adapters transform *external* rows (external column names + MCC tokens) into
*canonical* records that match the schema declared by the contract. They must
not persist and must not embed candidate PII in their output.

Seat-matrix input columns: ``StateName``, ``InstituteType``, ``Institute``,
``Quota``, ``Branch``, ``Category``, ``TotalSeats`` (see PDF tables).

Allotment input columns: ``Institute Code``, ``Institute Name``, ``Course``,
``Quota``, ``Category``, ``Round``, ``Rank``, ``Score``, ``Seats`` (MCC
machine-readable allotment CSV).
"""

from __future__ import annotations

from typing import Any

from etl.contracts.adapters import AdapterResult, SourceAdapter
from etl.contracts.base import SourceContract
from etl.contracts.canonical import SourceMetadata
from etl.contracts.sources.mcc.contracts import ALLOTMENT_PRIVACY_BLOCKLIST
from etl.contracts.sources.mcc.mappings import (
    extract_college_id,
    extract_college_name,
    normalize_allotment_category,
    normalize_allotment_quota,
    normalize_course,
    normalize_seat_matrix_category,
    normalize_seat_matrix_quota,
)


def _safe_int(value: object) -> int | str:
    """Coerce to int when possible, else return the raw string.

    Returning the raw string on failure lets the contract validator report a
    typed ``INVALID_TYPE`` error instead of the adapter crashing the run.
    """
    if value is None or value == "":
        return ""
    text = str(value).strip().replace(",", "")
    try:
        return int(text)
    except ValueError:
        return str(value).strip()


def _safe_float(value: object) -> float | str:
    """Coerce to float when possible, else return the raw string."""
    if value is None or value == "":
        return ""
    text = str(value).strip().replace(",", "")
    try:
        return float(text)
    except ValueError:
        return str(value).strip()


class MCCSeatMatrixAdapter(SourceAdapter):
    """Transform MCC seat-matrix PDF-table rows into canonical records."""

    def transform(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
        metadata: SourceMetadata,
    ) -> AdapterResult:
        """Map each seat-matrix row to a canonical ``SeatMatrix`` record."""
        records: list[dict[str, Any]] = []
        skipped = 0
        year = contract.effective_year
        for raw in raw_data:
            institute = (raw.get("Institute") or "").strip()
            if not institute:
                skipped += 1
                continue
            category_id, pwd = normalize_seat_matrix_category(raw.get("Category", ""))
            records.append(
                {
                    "college_id": extract_college_id(institute),
                    "college_name": extract_college_name(institute),
                    "state": (raw.get("StateName") or "").strip(),
                    "institute_type": (raw.get("InstituteType") or "").strip(),
                    "quota_id": normalize_seat_matrix_quota(raw.get("Quota", "")),
                    "course_id": normalize_course(raw.get("Branch", "")),
                    "branch": (raw.get("Branch") or "").strip(),
                    "category_id": category_id,
                    "pwd": pwd,
                    "total_seats": _safe_int(raw.get("TotalSeats")),
                    "effective_year": year,
                    "source_file_id": metadata.source_file_id,
                }
            )
        return AdapterResult(
            records=records,
            metadata=metadata,
            records_transformed=len(records),
            records_skipped=skipped,
        )

    def validate_source(
        self, raw_data: list[dict[str, Any]], contract: SourceContract
    ) -> list[str]:
        """Validate that required seat-matrix columns are present."""
        errors: list[str] = []
        if not raw_data:
            errors.append("Seat matrix source data is empty")
            return errors
        first_row = raw_data[0]
        errors.extend(
            f"Expected column not found: {column}"
            for column in contract.required_columns
            if column not in first_row
        )
        return errors


class MCCAllotmentsAdapter(SourceAdapter):
    """Transform an MCC allotment CSV into canonical ``Allotment`` records.

    The adapter emits only rank/score/seat_count + cohort identifiers. Any
    candidate-level PII column present in the source is silently dropped —
    it is never copied into a canonical record.
    """

    def transform(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
        metadata: SourceMetadata,
    ) -> AdapterResult:
        """Map each allotment row to a canonical ``Allotment`` record."""
        records: list[dict[str, Any]] = []
        skipped = 0
        year = contract.effective_year
        round_id = contract.publication_version.lower().replace(" ", "_")
        for raw in raw_data:
            if not raw.get("Institute Code") and not raw.get("Rank"):
                skipped += 1
                continue
            category_id, _pwd = normalize_allotment_category(raw.get("Category", ""))
            records.append(
                {
                    "college_id": (raw.get("Institute Code") or "").strip(),
                    "college_name": (raw.get("Institute Name") or "").strip(),
                    "course_id": normalize_course(raw.get("Course", "")),
                    "quota_id": normalize_allotment_quota(raw.get("Quota", "")),
                    "category_id": category_id,
                    "round_id": round_id,
                    "rank": _safe_int(raw.get("Rank")),
                    "score": _safe_float(raw.get("Score")),
                    "seat_count": _safe_int(raw.get("Seats")),
                    "effective_year": year,
                    "source_file_id": metadata.source_file_id,
                }
            )
        return AdapterResult(
            records=records,
            metadata=metadata,
            records_transformed=len(records),
            records_skipped=skipped,
        )

    def validate_source(
        self, raw_data: list[dict[str, Any]], contract: SourceContract
    ) -> list[str]:
        """Validate required allotment columns and reject PII leakage."""
        errors: list[str] = []
        if not raw_data:
            errors.append("Allotment source data is empty")
            return errors
        first_row = raw_data[0]
        leaked = [k for k in first_row if k in ALLOTMENT_PRIVACY_BLOCKLIST]
        if leaked:
            errors.append(f"Refusing to ingest PII columns: {', '.join(sorted(leaked))}")
        errors.extend(
            f"Expected column not found: {column}"
            for column in contract.required_columns
            if column not in first_row
        )
        return errors


__all__ = ["MCCAllotmentsAdapter", "MCCSeatMatrixAdapter"]
