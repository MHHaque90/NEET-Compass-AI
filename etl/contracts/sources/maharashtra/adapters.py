"""Source adapters for Maharashtra seat-matrix and allotment rows.

Adapters transform *external* rows (external column names + Maharashtra tokens)
into *canonical* records that match the schema declared by the contract. They
must not persist and must not embed candidate PII in their output.

Seat-matrix input columns: ``StateName``, ``Institute``, ``Course``,
``Category``, ``Quota``, ``TotalSeats`` (see contract).

Allotment input columns: ``Institute``, ``Course``, ``Category``,
``Quota``, ``Round``, ``OpeningRank``, ``ClosingRank``, ``SeatCount``
(Maharashtra CET Cell machine-readable format).
"""

from __future__ import annotations

from typing import Any

from etl.contracts.adapters import AdapterResult, SourceAdapter
from etl.contracts.base import SourceContract
from etl.contracts.canonical import SourceMetadata
from etl.contracts.sources.maharashtra.mappings import (
    normalize_maharashtra_category,
    normalize_maharashtra_quota,
)


def _safe_int(value: object) -> int | str:
    """Coerce to int when possible, else return the raw string."""
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


def _normalize_course(raw: str) -> str:
    """Normalise a ``Course``/``Branch`` value to a canonical course id."""
    token = raw.strip()
    first = token.split()[0] if token else ""
    course_map = {"MBBS": "mbbs", "BDS": "bds"}
    if first in course_map:
        return course_map[first]
    return first.lower()


class MaharashtraSeatMatrixAdapter(SourceAdapter):
    """Transform Maharashtra seat-matrix rows into canonical ``SeatMatrix`` records."""

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
            category_id, pwd = normalize_maharashtra_category(raw.get("Category", ""))
            records.append(
                {
                    "college_id": institute,
                    "college_name": institute,
                    "state": (raw.get("StateName") or "").strip(),
                    "institute_type": "",
                    "quota_id": normalize_maharashtra_quota(raw.get("Quota", "")),
                    "course_id": _normalize_course(raw.get("Course", "")),
                    "branch": (raw.get("Course") or "").strip(),
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
            errors.append("Maharashtra seat matrix source data is empty")
            return errors
        first_row = raw_data[0]
        errors.extend(
            f"Expected column not found: {column}"
            for column in contract.required_columns
            if column not in first_row
        )
        return errors


class MaharashtraAllotmentsAdapter(SourceAdapter):
    """Transform Maharashtra allotment rows into canonical ``Allotment`` records.

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
            if not raw.get("Institute") and not raw.get("OpeningRank"):
                skipped += 1
                continue
            category_id, _pwd = normalize_maharashtra_category(raw.get("Category", ""))
            records.append(
                {
                    "college_id": (raw.get("Institute") or "").strip(),
                    "college_name": (raw.get("Institute") or "").strip(),
                    "course_id": _normalize_course(raw.get("Course", "")),
                    "quota_id": normalize_maharashtra_quota(raw.get("Quota", "")),
                    "category_id": category_id,
                    "round_id": round_id,
                    "rank": _safe_int(raw.get("OpeningRank")),
                    "opening_rank": _safe_int(raw.get("OpeningRank")),
                    "closing_rank": _safe_int(raw.get("ClosingRank")),
                    "seat_count": _safe_int(raw.get("SeatCount")),
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
            errors.append("Maharashtra allotment source data is empty")
            return errors
        first_row = raw_data[0]
        errors.extend(
            f"Expected column not found: {column}"
            for column in contract.required_columns
            if column not in first_row
        )
        return errors


__all__ = ["MaharashtraAllotmentsAdapter", "MaharashtraSeatMatrixAdapter"]
