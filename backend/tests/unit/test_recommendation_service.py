"""RecommendationService orchestration with fakes (no DB, no ML)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import pytest

from app.application.errors import CollegeNotFoundError, RecommendationEngineNotConfigured
from app.application.services.recommendation_service import RecommendationService
from app.application.services.strategy_service import StrategyService
from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.college import College
from app.domain.entities.recommendation import Recommendation
from app.domain.enums import Course
from app.domain.ports.allotment_repository import AllotmentRepository
from app.domain.ports.college_repository import CollegeRepository
from app.domain.ports.recommendation_engine import RecommendationEngine
from app.domain.ports.recommendation_repository import RecommendationRepository


class FakeCollegeRepository(CollegeRepository):
    def __init__(self, colleges: Sequence[College]) -> None:
        self._by_code = {c.code: c for c in colleges}

    def get_by_code(self, code: str) -> College | None:
        return self._by_code.get(code)

    def find(self, **kwargs) -> Sequence[College]:
        return list(self._by_code.values())


class FakeAllotmentRepository(AllotmentRepository):
    def history_for(self, *args, **kwargs) -> Sequence:
        return []

    def closing_rank_for(self, *args, **kwargs) -> int | None:
        return None


class FakeRecommendationRepository(RecommendationRepository):
    def __init__(self) -> None:
        self._store: dict[str, Recommendation] = {}

    def save(self, recommendation: Recommendation) -> Recommendation:
        saved = recommendation.model_copy(update={"id": recommendation.id})
        self._store[str(recommendation.id)] = saved
        return saved

    def get(self, recommendation_id):
        return self._store.get(str(recommendation_id))

    def latest_for_candidate(self, candidate_id):
        for rec in self._store.values():
            if rec.candidate_id == candidate_id:
                return rec
        return None


class ScoringEngine(RecommendationEngine):
    name = "fake"
    version = "1.0-test"

    def predict(self, candidate: CandidateProfile, college_id: uuid.UUID) -> Recommendation:
        return Recommendation(
            college_id=college_id,
            course=Course.MBBS,
            probability=0.8,
            expected_round=2,
            confidence=0.7,
            engine_name=self.name,
            engine_version=self.version,
            reasons=({"type": "fake", "message": "test"},),
        )


def _build_service(colleges: Sequence[College]) -> RecommendationService:
    return RecommendationService(
        engine=ScoringEngine(),
        colleges=FakeCollegeRepository(colleges),
        allotments=FakeAllotmentRepository(),
        recommendations=FakeRecommendationRepository(),
        strategy=StrategyService(),
    )


def test_recommend_scores_each_college_and_persists(
    sample_candidate: CandidateProfile,
    sample_college: College,
) -> None:
    service = _build_service([sample_college])
    results = service.recommend(sample_candidate, [sample_college.code])

    assert len(results) == 1
    assert results[0].probability == 0.8
    assert results[0].expected_round == 2
    assert results[0].engine_name == "fake"


def test_recommend_unknown_college_raises(sample_candidate: CandidateProfile) -> None:
    service = _build_service([])
    with pytest.raises(CollegeNotFoundError):
        service.recommend(sample_candidate, ["NOPE-001"])


def test_unavailable_engine_fails_loud(sample_candidate: CandidateProfile) -> None:
    from app.infrastructure.ml.unavailable_engine import UnavailableEngine

    service = RecommendationService(
        engine=UnavailableEngine(),
        colleges=FakeCollegeRepository([]),
        allotments=FakeAllotmentRepository(),
        recommendations=FakeRecommendationRepository(),
        strategy=StrategyService(),
    )
    with pytest.raises(RecommendationEngineNotConfigured):
        service.recommend(sample_candidate, ["X"], candidate_id=None)
