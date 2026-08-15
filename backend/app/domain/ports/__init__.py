"""Ports (interfaces) between the application and the outside world.

Ports are the dependency-inversion seams required by the D of SOLID: the
application layer depends only on these abstract interfaces, and the
infrastructure layer provides concrete implementations. Swapping a
PostgreSQL repository for an in-memory fake (tests) or an ML engine for a
rule-based one never touches application code.
"""

from app.domain.ports.allotment_repository import AllotmentRepository
from app.domain.ports.college_repository import CollegeRepository
from app.domain.ports.recommendation_engine import RecommendationEngine
from app.domain.ports.recommendation_repository import RecommendationRepository

__all__ = [
    "AllotmentRepository",
    "CollegeRepository",
    "RecommendationEngine",
    "RecommendationRepository",
]
