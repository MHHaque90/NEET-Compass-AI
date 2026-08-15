"""The core use case: produce a full admission recommendation.

Orchestration only — the service composes the injected engine and
repositories, and assembles the explainable output. All scoring knowledge is
delegated to the ``RecommendationEngine`` port so this code survives intact
whether the engine is rule-based, statistical, or a trained ML model.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence

from app.application.errors import (
    CollegeNotFoundError,
    PredictionUnavailable,
    RecommendationEngineNotConfigured,
)
from app.application.services.strategy_service import StrategyService
from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.college import College
from app.domain.entities.recommendation import Recommendation
from app.domain.enums import RecommendationStatus
from app.domain.ports.allotment_repository import AllotmentRepository
from app.domain.ports.college_repository import CollegeRepository
from app.domain.ports.recommendation_engine import RecommendationEngine
from app.domain.ports.recommendation_repository import RecommendationRepository

logger = logging.getLogger(__name__)


class RecommendationService:
    """Use case: generate a college-by-college recommendation for a candidate.

    All dependencies are constructor-injected, satisfying both the I and the D
    of SOLID and making the use case fully testable with fakes.
    """

    def __init__(
        self,
        engine: RecommendationEngine,
        colleges: CollegeRepository,
        allotments: AllotmentRepository,
        recommendations: RecommendationRepository,
        strategy: StrategyService,
    ) -> None:
        self._engine = engine
        self._colleges = colleges
        self._allotments = allotments
        self._recommendations = recommendations
        self._strategy = strategy

    def recommend(
        self,
        candidate: CandidateProfile,
        college_ids: Sequence[str],
        candidate_id: uuid.UUID | None = None,
    ) -> Sequence[Recommendation]:
        """Score a candidate against the given colleges and persist results.

        Args:
            candidate: validated candidate profile (see ``CandidateProfile``).
            college_ids: stable college codes to evaluate.
            candidate_id: optional persisted candidate id for the audit trail.

        Raises:
            RecommendationEngineNotConfigured: when the active engine cannot run.
            CollegeNotFoundError: when a requested code is unknown.

        """
        if self._engine.name == "unavailable":
            raise RecommendationEngineNotConfigured(
                f"No scoring engine is registered for backend '{type(self._engine).__name__}'."
            )

        colleges = self._resolve_colleges(college_ids)
        recommendations: list[Recommendation] = []
        for college in colleges:
            try:
                rec = self._engine.predict(candidate, college.id)  # type: ignore[arg-type]
            except PredictionUnavailable as exc:
                logger.warning("Prediction unavailable for %s: %s", college.code, exc)
                rec = self._empty_recommendation(college)

            enriched = rec.model_copy(
                update={
                    "candidate_id": candidate_id,
                    "status": RecommendationStatus.COMPLETED,
                    "strategy": self._strategy.build_strategy(candidate, college),
                }
            )
            recommendations.append(self._recommendations.save(enriched))

        return recommendations

    def _resolve_colleges(self, college_ids: Sequence[str]) -> list[College]:
        resolved: list[College] = []
        for code in college_ids:
            college = self._colleges.get_by_code(code)
            if college is None:
                raise CollegeNotFoundError(f"Unknown college code: {code}")
            resolved.append(college)
        return resolved

    def _empty_recommendation(self, college: College) -> Recommendation:
        """Auditable placeholder for colleges the engine cannot score."""
        return Recommendation(
            college_id=college.id,
            course=college.course,
            status=RecommendationStatus.DEGRADED,
            reasons=(
                {
                    "type": "data_gap",
                    "message": "No reliable allotment history exists for this college/cohort yet.",
                },
            ),
        )
