"""Port for the recommendation engine (the future ML seam).

This is *the* plug-in point for machine learning. The application layer
calls ``predict`` through this interface and never knows whether the answer
came from a gradient-boosted model, a neural net, or the safe default
rule-based engine. A new engine is added by implementing this interface and
registering it in the composition root — nothing else changes.

Deliberately symmetric (candidate in, candidate out) so that model versioning,
A/B testing and shadow deployments slot in behind the same seam.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.recommendation import Recommendation


class RecommendationEngine(ABC):
    """Contract every scoring engine must satisfy."""

    name: str
    version: str

    @abstractmethod
    def predict(
        self,
        candidate: CandidateProfile,
        college_id: uuid.UUID,
    ) -> Recommendation:
        """Score one candidate against one college and return a recommendation.

        Implementations raise ``PredictionUnavailable`` when they cannot
        produce a score (e.g. insufficient historical data) — never return
        fabricated probabilities.
        """
