"""SQLAlchemy adapter for the ``AllotmentRepository`` port."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.allotment import AllotmentRecord
from app.domain.enums import Category, Course, Gender, PwdStatus, QuotaType
from app.domain.ports.allotment_repository import AllotmentRepository
from app.infrastructure.db.models.allotment import AllotmentModel


class SQLAlchemyAllotmentRepository(AllotmentRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def history_for(
        self,
        college_id: UUID,
        *,
        quota_type: QuotaType,
        category: Category,
        gender: Gender,
        pw_d: PwdStatus,
        course: Course,
        years: Sequence[int] | None = None,
    ) -> Sequence[AllotmentRecord]:
        stmt = select(AllotmentModel).where(
            AllotmentModel.college_id == college_id,
            AllotmentModel.quota_type == quota_type,
            AllotmentModel.category == category,
            AllotmentModel.gender == gender,
            AllotmentModel.is_pwd == (pw_d == PwdStatus.PWD),
            AllotmentModel.course == course,
        )
        if years:
            stmt = stmt.where(AllotmentModel.counselling_year.in_(years))
        stmt = stmt.order_by(AllotmentModel.counselling_year.desc(), AllotmentModel.round_number)

        return [_to_domain(model) for model in self._session.scalars(stmt).all()]

    def closing_rank_for(
        self,
        college_id: UUID,
        *,
        quota_type: QuotaType,
        category: Category,
        gender: Gender,
        pw_d: PwdStatus,
        year: int,
        round_number: int,
    ) -> int | None:
        model = self._session.scalar(
            select(AllotmentModel).where(
                AllotmentModel.college_id == college_id,
                AllotmentModel.quota_type == quota_type,
                AllotmentModel.category == category,
                AllotmentModel.gender == gender,
                AllotmentModel.is_pwd == (pw_d == PwdStatus.PWD),
                AllotmentModel.counselling_year == year,
                AllotmentModel.round_number == round_number,
            )
        )
        return model.closing_rank if model is not None else None


def _to_domain(model: AllotmentModel) -> AllotmentRecord:
    return AllotmentRecord(
        id=model.id,
        college_id=model.college_id,
        college_code=model.college_code,
        course=Course(model.course),
        counselling_year=model.counselling_year,
        counselling_date=_as_date(model.counselling_date),
        round_number=model.round_number,
        is_stray_round=model.is_stray_round,
        quota_type=QuotaType(model.quota_type),
        category=Category(model.category),
        gender=Gender(model.gender),
        pw_d=PwdStatus.PWD if model.is_pwd else PwdStatus.NONE,
        opening_rank=model.opening_rank,
        closing_rank=model.closing_rank,
        opening_marks=_as_float(model.opening_marks),
        closing_marks=_as_float(model.closing_marks),
        seats_offered=model.seats_offered,
    )


def _as_date(value: object) -> date | None:
    return value if isinstance(value, date) else None


def _as_float(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value)
