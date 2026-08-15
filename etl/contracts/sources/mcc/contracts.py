"""MCC (Medical Counselling Committee) source contracts.

A contract declares the schema an external source is *expected* to present
once it has been rendered into rows (PDF tables -> rows, or a CSV file). It
does NOT know how to read the PDF / CSV itself -- that is the source adapter's
job -- nor how to persist (the loader's job). The contract is the durable,
versioned agreement between "the world outside" and the canonical models in
``etl.contracts.canonical``.

Two contracts are declared for the 2025 cycle:

* ``seat_matrix`` -- the sanctioned-seat PDFs (AIQ seat matrix + the
  AIIMS/JIPMER/BHU seat matrix). PII-free.
* ``allotments``  -- the per-round allotment result CSV. The canonical
  ``Allotment`` record carries only rank/score/seat_count -- candidate PII
  (name, percentile, caste certificate number, guardian, contact) is
  intentionally NOT part of these contracts.
"""

from __future__ import annotations

from etl.contracts.base import (
    FieldMapping,
    SourceContract,
    SourceType,
    ValidationRule,
)
from etl.contracts.sources.mcc.mappings import (
    ALLOTMENT_QUOTA_ABBREVIATIONS,
    SEAT_MATRIX_CATEGORY_BASE,
    SEAT_MATRIX_QUOTA_MAP,
)
from etl.contracts.version import ContractVersion

SEAT_MATRIX_COLUMNS: tuple[str, ...] = (
    "StateName",
    "InstituteType",
    "Institute",
    "Quota",
    "Branch",
    "Category",
    "TotalSeats",
)

ALLOTMENT_COLUMNS: tuple[str, ...] = (
    "Institute Code",
    "Institute Name",
    "Course",
    "Quota",
    "Category",
    "Round",
    "Rank",
    "Score",
    "Seats",
)

# PII fields the MCC human-readable allotment *report* carries but the
# machine-readable allotment CSV never should. The contract + adapter assert
# against this set so a stray PII column can never be ingested as canonical
# data.
ALLOTMENT_PRIVACY_BLOCKLIST: frozenset[str] = frozenset(
    {
        "Candidate Name", "Father Name", "Mother Name", "Guardian Name",
        "Candidate Category", "Community", "Religion", "Aadhaar", "Contact No",
        "Email", "Percentile", "NEET Score", "Application ID", "Password",
        "Mother's Name", "Father's Name",
    }
)

_CATEGORIES: tuple[str, ...] = tuple(
    [*SEAT_MATRIX_CATEGORY_BASE.values()]
    + [f"{v}_pwd" for v in SEAT_MATRIX_CATEGORY_BASE.values()]
)
_QUOTAS: tuple[str, ...] = tuple(
    sorted({v.lower() for v in [*SEAT_MATRIX_QUOTA_MAP.values(), *ALLOTMENT_QUOTA_ABBREVIATIONS]})
)


def _required(*fields: str) -> tuple[ValidationRule, ...]:
    return tuple(ValidationRule(field_name=f, rule_type="required") for f in fields)


def _seat_matrix_validation_rules() -> tuple[ValidationRule, ...]:
    """Build the validation rule tuple for the seat-matrix contract."""
    rules: list[ValidationRule] = [
        *_required("college_id", "course_id", "quota_id", "category_id", "total_seats"),
        ValidationRule("quota_id", "enum", {"values": list(_QUOTAS)}),
        ValidationRule("category_id", "enum", {"values": list(_CATEGORIES)}),
        ValidationRule("total_seats", "type", {"type": "int"}),
        ValidationRule("total_seats", "range", {"min": 0, "max": 2000}),
        *(
            ValidationRule(field_name=key_field, rule_type="unique_key")
            for key_field in (
                "college_id", "course_id", "quota_id", "category_id", "effective_year"
            )
        ),
    ]
    return tuple(rules)


def _allotment_validation_rules() -> tuple[ValidationRule, ...]:
    """Build the validation rule tuple for the allotment contract."""
    rules: list[ValidationRule] = [
        *_required("college_id", "course_id", "quota_id", "category_id", "round_id", "rank"),
        ValidationRule("quota_id", "enum", {"values": list(_QUOTAS)}),
        ValidationRule("category_id", "enum", {"values": list(_CATEGORIES)}),
        ValidationRule("rank", "type", {"type": "int"}),
        ValidationRule("rank", "range", {"min": 1, "max": 900000}),
        ValidationRule("score", "type", {"type": "float"}),
        ValidationRule("seat_count", "type", {"type": "int"}),
        ValidationRule("seat_count", "range", {"min": 1, "max": 3}),
        *(
            ValidationRule(field_name=key_field, rule_type="unique_key")
            for key_field in (
                "college_id", "course_id", "quota_id", "category_id", "round_id", "rank"
            )
        ),
    ]
    return tuple(rules)


def seat_matrix_2025_contract() -> SourceContract:
    """Contract for the MCC 2025 round-1 seat-matrix PDF tables.

    External column names are the literal headers emitted by the PDF table
    extraction. The adapter transforms the values (e.g. ``OP`` -> ``gn``)
    before validation runs.
    """
    return SourceContract(
        source_id="mcc",
        source_name="Medical Counselling Committee",
        authority="MCC / DGHS",
        dataset="seat_matrix",
        source_type=SourceType.CSV,
        contract_version=ContractVersion.parse("1.1.0"),
        effective_year=2025,
        publication_version="Round 1",
        supported_formats=("csv", "table"),
        expected_columns=SEAT_MATRIX_COLUMNS,
        required_columns=SEAT_MATRIX_COLUMNS,
        field_mapping=(
            FieldMapping("StateName", "state"),
            FieldMapping("InstituteType", "institute_type"),
            FieldMapping("Institute", "college_name"),
            FieldMapping("Quota", "quota_id"),
            FieldMapping("Branch", "course_id"),
            FieldMapping("Category", "category_id"),
            FieldMapping("TotalSeats", "total_seats"),
        ),
        validation_rules=_seat_matrix_validation_rules(),
    )


def allotments_2025_contract() -> SourceContract:
    """Contract for the MCC 2025 allotment-result CSV (per round).

    Only the non-PII columns the MCC publishes in its machine-readable
    allotment file are declared as expected. Candidate PII columns
    (``Candidate Name``, ``Percentile``, certificate number,
    ``Father/Mother Name``, ``Contact No``, ``Email``, ``Aadhaar``, ...)
    are deliberately absent: the canonical ``Allotment`` record is built from
    rank + score + seat_count only.
    """
    return SourceContract(
        source_id="mcc",
        source_name="Medical Counselling Committee",
        authority="MCC / DGHS",
        dataset="allotments",
        source_type=SourceType.CSV,
        contract_version=ContractVersion.parse("1.1.0"),
        effective_year=2025,
        publication_version="Round 3",
        supported_formats=("csv",),
        expected_columns=ALLOTMENT_COLUMNS,
        required_columns=ALLOTMENT_COLUMNS,
        field_mapping=(
            FieldMapping("Institute Code", "college_id"),
            FieldMapping("Institute Name", "college_name"),
            FieldMapping("Course", "course_id"),
            FieldMapping("Quota", "quota_id"),
            FieldMapping("Category", "category_id"),
            FieldMapping("Round", "round_id"),
            FieldMapping("Rank", "rank"),
            FieldMapping("Score", "score"),
            FieldMapping("Seats", "seat_count"),
        ),
        validation_rules=_allotment_validation_rules(),
    )
