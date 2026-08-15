"""Verify the production SQLAlchemy ``AllotmentLoader`` emits idempotent SQL.

This runs entirely without a database: the loader's upsert statement is
compiled against the PostgreSQL dialect and captured, so we can assert the
insert is ``ON CONFLICT DO NOTHING`` against the cohort unique constraint --
the property that makes re-running a counselling year safe. A live PostgreSQL
round-trip is the integration suite's job (Sprint 3.1A: recorded as BLOCKED in
this sandbox -- the on-file dev credentials are rejected by the local server).
"""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.domain.enums import Category, Course, Gender, QuotaType
from app.infrastructure.etl.loaders.allotment_loader import AllotmentLoader
from app.infrastructure.etl.validators import AllotmentRow

_UNIQUE_CONSTRAINT = "uq_allotments_college_round_cohort"


class _CapturingSession:
    """Minimal session stand-in that only captures compiled SQL."""

    def __init__(self, captured: list[str]) -> None:
        self._captured = captured

    def execute(self, statement: Any) -> None:
        self._captured.append(str(statement.compile(dialect=postgresql.dialect())))


def test_upsert_compiles_to_on_conflict_do_nothing() -> None:
    captured: list[str] = []
    loader = AllotmentLoader(session_factory=lambda: cast(Session, _CapturingSession(captured)))
    loader._college_ids = {"200101": "11111111-1111-1111-1111-111111111111"}

    row = AllotmentRow(
        college_code="200101",
        course=Course.MBBS,
        counselling_year=2025,
        round_number=3,
        quota_type=QuotaType.AIQ,
        category=Category.GENERAL,
        gender=Gender.NEUTRAL,
        is_pwd=False,
        opening_rank=1000,
        closing_rank=1200,
        closing_marks=180.5,
    )

    written = loader._upsert_batch(cast(Session, _CapturingSession(captured)), [row])
    sql = " ".join(captured)

    assert written == 1
    assert "INSERT INTO allotments" in sql
    assert "ON CONFLICT" in sql
    assert "DO NOTHING" in sql
    assert _UNIQUE_CONSTRAINT in sql
