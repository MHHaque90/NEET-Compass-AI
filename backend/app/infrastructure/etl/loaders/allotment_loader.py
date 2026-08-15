"""Allotment loader: idempotent batch upsert into PostgreSQL.

Resolves college codes to ids once per run (cached) and inserts with
``ON CONFLICT DO NOTHING`` against the cohort unique constraint, making the
pipeline safe to re-run for the same year without duplicating rows.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.infrastructure.db.models.allotment import AllotmentModel
from app.infrastructure.db.models.college import CollegeModel
from app.infrastructure.etl.base import Loader, RawRow
from app.infrastructure.etl.validators import AllotmentRow, DataValidationError, validate_rows


class AllotmentLoader(Loader):
    """Loads validated ``AllotmentRow`` records with unknown-code protection."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
        batch_size: int = 1000,
    ) -> None:
        self._session_factory = session_factory
        self._batch_size = batch_size
        self._college_ids: dict[str, str] = {}

    def load(self, rows: Iterable[RawRow]) -> int:
        validated = validate_rows(rows)
        if not validated:
            return 0

        total = 0
        with self._session_factory() as session:
            self._refresh_college_lookup(session, {r.college_code for r in validated})
            unknown = sorted(
                {r.college_code for r in validated if r.college_code not in self._college_ids}
            )
            if unknown:
                raise DataValidationError(
                    f"Allotment rows reference unknown college codes: {unknown}", len(unknown)
                )

            for offset in range(0, len(validated), self._batch_size):
                batch = validated[offset : offset + self._batch_size]
                total += self._upsert_batch(session, batch)
            session.commit()
        return total

    def _refresh_college_lookup(self, session: Session, codes: set[str]) -> None:
        missing = [code for code in codes if code not in self._college_ids]
        if not missing:
            return
        rows = session.execute(
            select(CollegeModel.id, CollegeModel.code).where(CollegeModel.code.in_(missing))
        ).all()
        self._college_ids.update({code: str(college_id) for college_id, code in rows})

    def _upsert_batch(self, session: Session, batch: list[AllotmentRow]) -> int:
        stmt = insert(AllotmentModel).values(
            [
                {
                    "college_id": self._college_ids[row.college_code],
                    "college_code": row.college_code,
                    "course": row.course.value,
                    "counselling_year": row.counselling_year,
                    "round_number": row.round_number,
                    "quota_type": row.quota_type.value,
                    "category": row.category.value,
                    "gender": row.gender.value,
                    "is_pwd": row.is_pwd,
                    "opening_rank": row.opening_rank,
                    "closing_rank": row.closing_rank,
                    "opening_marks": row.opening_marks,
                    "closing_marks": row.closing_marks,
                }
                for row in batch
            ]
        )
        stmt = stmt.on_conflict_do_nothing(
            constraint="uq_allotments_college_round_cohort",
        )
        session.execute(stmt)
        return len(batch)
