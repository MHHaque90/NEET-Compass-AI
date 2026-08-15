"""SQLAlchemy adapter for the ``RecommendationRepository`` port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.recommendation import Recommendation
from app.domain.enums import Course, RecommendationStatus
from app.domain.ports.recommendation_repository import RecommendationRepository
from app.infrastructure.db.models.recommendation import RecommendationModel


class SQLAlchemyRecommendationRepository(RecommendationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, recommendation: Recommendation) -> Recommendation:
        model = _to_model(recommendation)
        model.id = recommendation.id or model.id
        self._session.merge(model)
        self._session.flush()
        return recommendation.model_copy(update={"id": model.id})

    def get(self, recommendation_id: UUID) -> Recommendation | None:
        model = self._session.get(RecommendationModel, recommendation_id)
        return _to_domain(model) if model is not None else None

    def latest_for_candidate(self, candidate_id: UUID) -> Recommendation | None:
        model = self._session.scalar(
            select(RecommendationModel)
            .where(RecommendationModel.candidate_id == candidate_id)
            .order_by(RecommendationModel.created_at.desc())
            .limit(1)
        )
        return _to_domain(model) if model is not None else None


def _to_model(recommendation: Recommendation) -> RecommendationModel:
    return RecommendationModel(
        id=recommendation.id,
        candidate_id=recommendation.candidate_id,
        college_id=recommendation.college_id,
        course=recommendation.course,
        probability=recommendation.probability,
        expected_round=recommendation.expected_round,
        confidence=recommendation.confidence,
        engine_name=recommendation.engine_name,
        engine_version=recommendation.engine_version,
        status=recommendation.status,
        reasons=list(recommendation.reasons),
        strategy=recommendation.strategy,
        choice_filling_order=list(recommendation.choice_filling_order),
    )


def _to_domain(model: RecommendationModel) -> Recommendation:
    return Recommendation(
        id=model.id,
        candidate_id=model.candidate_id,
        college_id=model.college_id,
        course=Course(model.course),
        probability=_as_float(model.probability),
        expected_round=model.expected_round,
        confidence=_as_float(model.confidence),
        engine_name=model.engine_name,
        engine_version=model.engine_version,
        status=RecommendationStatus(model.status),
        reasons=tuple(model.reasons or ()),
        strategy=model.strategy or {},
        choice_filling_order=tuple(model.choice_filling_order or ()),
    )


def _as_float(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value)
