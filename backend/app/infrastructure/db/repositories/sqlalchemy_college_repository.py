"""SQLAlchemy adapter for the ``CollegeRepository`` port."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.college import College
from app.domain.enums import Course, IndiaState
from app.domain.ports.college_repository import CollegeRepository
from app.infrastructure.db.models.college import CollegeModel


class SQLAlchemyCollegeRepository(CollegeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_code(self, code: str) -> College | None:
        model = self._session.scalar(select(CollegeModel).where(CollegeModel.code == code))
        return _to_domain(model) if model is not None else None

    def find(
        self,
        *,
        course: Course | None = None,
        states: Sequence[IndiaState] | None = None,
        max_annual_fee: int | None = None,
    ) -> Sequence[College]:
        stmt = select(CollegeModel)
        if course is not None:
            stmt = stmt.where(CollegeModel.course == course)
        if states:
            stmt = stmt.where(CollegeModel.state.in_([s.value for s in states]))
        if max_annual_fee is not None:
            stmt = stmt.where(CollegeModel.annual_fee_inr <= max_annual_fee)
        stmt = stmt.order_by(CollegeModel.code)

        return [_to_domain(model) for model in self._session.scalars(stmt).all()]


def _to_domain(model: CollegeModel) -> College:
    return College(
        id=model.id,
        code=model.code,
        name=model.name,
        state=IndiaState(model.state),
        city=model.city,
        course=Course(model.course),
        ownership=model.ownership,
        annual_fee_inr=int(model.annual_fee_inr),
        total_seats=model.total_seats,
        aiq_seats=model.aiq_seats,
    )
