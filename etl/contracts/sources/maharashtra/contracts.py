"""Maharashtra (MAH CET Cell) source contracts.

Declares the schema an external source is *expected* to present once it has
been rendered into rows. It does NOT know how to read the source format
 PDF / CSV itself -- that is the source adapter's job nor how to persist
 (the loader's job). The contract is the durable, versioned agreement between
 "the world outside" and the canonical models in ``etl.contracts.canonical``.
"""

from __future__ import annotations

from etl.contracts.base import (
    FieldMapping,
    SourceContract,
    SourceType,
    ValidationRule,
)
from etl.contracts.version import ContractVersion

SEAT_MATRIX_COLUMNS: tuple[str, ...] = (
    "StateName",
    "Institute",
    "Course",
    "Category",
    "Quota",
    "TotalSeats",
)

ALLOTMENT_COLUMNS: tuple[str, ...] = (
    "Institute",
    "Course",
    "Category",
    "Quota",
    "Round",
    "OpeningRank",
    "ClosingRank",
    "SeatCount",
)


def _required(*fields: str) -> tuple[ValidationRule, ...]:
    return tuple(ValidationRule(field_name=f, rule_type="required") for f in fields)


def _seat_matrix_validation_rules() -> tuple[ValidationRule, ...]:
    rules: list[ValidationRule] = [
        *_required("college_id", "course_id", "quota_id", "category_id", "total_seats"),
        ValidationRule("quota_id", "enum", {"values": ["ai", "so", "mm"]}),
        ValidationRule("category_id", "enum", {"values": ["gn", "bc", "ew", "sc", "st", "gn_pwd", "bc_pwd", "ew_pwd", "sc_pwd", "st_pwd"]}),
        ValidationRule("total_seats", "type", {"type": "int"}),
        ValidationRule("total_seats", "range", {"min": 0, "max": 5000}),
        *(
            ValidationRule(field_name=key_field, rule_type="unique_key")
            for key_field in (
                "college_id", "course_id", "quota_id", "category_id", "effective_year"
            )
        ),
    ]
    return tuple(rules)


def _allotment_validation_rules() -> tuple[ValidationRule, ...]:
    rules: list[ValidationRule] = [
        *_required("college_id", "course_id", "quota_id", "category_id", "round_id", "rank"),
        ValidationRule("quota_id", "enum", {"values": ["ai", "so", "mm"]}),
        ValidationRule("category_id", "enum", {"values": ["gn", "bc", "ew", "sc", "st", "gn_pwd", "bc_pwd", "ew_pwd", "sc_pwd", "st_pwd"]}),
        ValidationRule("rank", "type", {"type": "int"}),
        ValidationRule("rank", "range", {"min": 1, "max": 900000}),
        ValidationRule("seat_count", "type", {"type": "int"}),
        ValidationRule("seat_count", "range", {"min": 1, "max": 100}),
        *(
            ValidationRule(field_name=key_field, rule_type="unique_key")
            for key_field in (
                "college_id", "course_id", "quota_id", "category_id", "round_id", "rank"
            )
        ),
    ]
    return tuple(rules)


def seat_matrix_2026_contract() -> SourceContract:
    """Contract for the Maharashtra 2026 seat-matrix data.

    External column names are the literal headers emitted by the source
    format (CSV or HTML table extraction). The adapter transforms the values
    before validation runs.
    """
    return SourceContract(
        source_id="mcc_state_maharashtra",
        source_name="MAHA CET Cell (State CET Cell)",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="seat_matrix",
        source_type=SourceType.CSV,
        contract_version=ContractVersion.parse("1.0.0"),
        effective_year=2026,
        publication_version="Round 1",
        supported_formats=("csv", "table"),
        expected_columns=SEAT_MATRIX_COLUMNS,
        required_columns=SEAT_MATRIX_COLUMNS,
        field_mapping=(
            FieldMapping("StateName", "state"),
            FieldMapping("Institute", "college_name"),
            FieldMapping("Course", "course_id"),
            FieldMapping("Category", "category_id"),
            FieldMapping("Quota", "quota_id"),
            FieldMapping("TotalSeats", "total_seats"),
        ),
        validation_rules=_seat_matrix_validation_rules(),
    )


def allotments_2026_contract() -> SourceContract:
    """Contract for the Maharashtra 2026 allotment-result data.

    Declares the non-PII columns the Maharashtra CET Cell publishes in its
    machine-readable allotment file. Candidate PII columns are deliberately
    absent: the canonical Allotment record is built from rank + score + seat_count
    only.
    """
    return SourceContract(
        source_id="mcc_state_maharashtra",
        source_name="MAHA CET Cell (State CET Cell)",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="allotments",
        source_type=SourceType.CSV,
        contract_version=ContractVersion.parse("1.0.0"),
        effective_year=2026,
        publication_version="Round 1",
        supported_formats=("csv",),
        expected_columns=ALLOTMENT_COLUMNS,
        required_columns=ALLOTMENT_COLUMNS,
        field_mapping=(
            FieldMapping("Institute", "college_id"),
            FieldMapping("Course", "course_id"),
            FieldMapping("Category", "category_id"),
            FieldMapping("Quota", "quota_id"),
            FieldMapping("Round", "round_id"),
            FieldMapping("OpeningRank", "opening_rank"),
            FieldMapping("ClosingRank", "closing_rank"),
            FieldMapping("SeatCount", "seat_count"),
        ),
        validation_rules=_allotment_validation_rules(),
    )
