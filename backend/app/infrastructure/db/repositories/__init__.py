"""SQLAlchemy implementations of the domain ports.

Repositories are thin adapters: they translate domain objects <-> ORM rows
and own every SQL query. They receive a caller-supplied ``Session`` so the
unit of work (transaction boundary) stays with the caller, not the adapter.
"""

from app.infrastructure.db.repositories.sqlalchemy_allotment_repository import (
    SQLAlchemyAllotmentRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_college_repository import (
    SQLAlchemyCollegeRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_recommendation_repository import (
    SQLAlchemyRecommendationRepository,
)

__all__ = [
    "SQLAlchemyAllotmentRepository",
    "SQLAlchemyCollegeRepository",
    "SQLAlchemyRecommendationRepository",
]
