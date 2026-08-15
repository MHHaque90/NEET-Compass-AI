"""Row-level validation for ETL pipeline data.

Raw data from counselling releases is notoriously dirty (merged cells,
footnotes, dashes for empty ranks, inconsistent headers). This module owns
the canonical row contract and fails loudly with structured error detail so
operators can fix the source data instead of silently shipping corruption.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, Field, ValidationError

from app.domain.enums import Category, Course, Gender, QuotaType
from app.infrastructure.etl.base import RawRow


class AllotmentRow(BaseModel):
    """Canonical, validated allotment row the loader can trust."""

    model_config = {"frozen": True}

    college_code: str = Field(min_length=1, max_length=20)
    course: Course
    counselling_year: int = Field(ge=2013, le=2100)
    round_number: int = Field(ge=1, le=5)
    quota_type: QuotaType
    category: Category
    gender: Gender
    is_pwd: bool = False
    opening_rank: int = Field(ge=1)
    closing_rank: int = Field(ge=1)
    opening_marks: float | None = Field(default=None, ge=0, le=720)
    closing_marks: float | None = Field(default=None, ge=0, le=720)


class DataValidationError(ValueError):
    """Raised when rows fail the canonical contract."""

    def __init__(self, message: str, failed: int) -> None:
        super().__init__(message)
        self.failed = failed


def validate_rows(rows: Iterable[RawRow]) -> list[AllotmentRow]:
    """Validate normalized rows into ``AllotmentRow`` objects.

    Raises:
        DataValidationError: when any row is invalid (all-or-nothing policy:
            a partial load with corrupted rows is worse than no load).

    """
    validated: list[AllotmentRow] = []
    failures = 0
    for row in rows:
        try:
            validated.append(AllotmentRow.model_validate(row))
        except ValidationError:
            failures += 1

    if failures:
        raise DataValidationError(
            f"{failures} of {failures + len(validated)} rows failed validation", failures
        )
    return validated
