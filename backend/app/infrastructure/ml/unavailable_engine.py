"""The safe default engine: refuses to fabricate predictions.

A NEET recommendation is high-stakes advice. Until a real scoring engine is
implemented and validated, the platform must *never* return invented
probabilities. This engine fails loud, and the application layer downgrades
the recommendation to an auditable `DEGRADED` record.

To ship a real engine:
    1. Implement ``RecommendationEngine`` (see `domain.ports`).
    2. Register it in ``app.application.container.Container.register_engine``.
    3. Set ``ML_RECOMMENDATION_ENGINE`` to its registration name.
"""

from __future__ import annotations

import uuid

from app.application.errors import PredictionUnavailable
from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.recommendation import Recommendation
from app.domain.ports.recommendation_engine import RecommendationEngine


class UnavailableEngine(RecommendationEngine):
    """Scoring engine placeholder that always declines to predict."""

    name = "unavailable"
    version = "0.0.0"

    def predict(
        self,
        candidate: CandidateProfile,
        college_id: uuid.UUID,
    ) -> Recommendation:
        raise PredictionUnavailable(
            "No scoring engine is configured. Set ML_RECOMMENDATION_ENGINE to "
            "a registered engine to enable predictions."
        )
