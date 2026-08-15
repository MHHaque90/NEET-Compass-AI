"""Port for persisting/loading generated recommendations (audit trail)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.recommendation import Recommendation


class RecommendationRepository(ABC):
    """Write-side contract for recommendation snapshots."""

    @abstractmethod
    def save(self, recommendation: Recommendation) -> Recommendation:
        """Persist (or update) a recommendation and return it with its id."""

    @abstractmethod
    def get(self, recommendation_id: uuid.UUID) -> Recommendation | None:
        """Fetch a recommendation by id, or None when it does not exist."""

    @abstractmethod
    def latest_for_candidate(self, candidate_id: uuid.UUID) -> Recommendation | None:
        """Return the most recently generated recommendation for a candidate."""
