"""Composition root — where the object graph is wired.

This is the only place in the codebase that knows about *both* the
application layer and the infrastructure layer. It selects the concrete
implementations (SQLAlchemy repositories, the active scoring engine) that
the application services receive through their ports. Tests replace this
graph with fakes; production swaps engines by configuration — nothing else
changes. This satisfies the D (dependency inversion) and L (Liskov) of SOLID.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.application.services.recommendation_service import RecommendationService
from app.application.services.strategy_service import StrategyService
from app.core.config import Settings, get_settings
from app.domain.ports.allotment_repository import AllotmentRepository
from app.domain.ports.college_repository import CollegeRepository
from app.domain.ports.recommendation_engine import RecommendationEngine
from app.domain.ports.recommendation_repository import RecommendationRepository
from app.infrastructure.db.repositories.sqlalchemy_allotment_repository import (
    SQLAlchemyAllotmentRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_college_repository import (
    SQLAlchemyCollegeRepository,
)
from app.infrastructure.db.repositories.sqlalchemy_recommendation_repository import (
    SQLAlchemyRecommendationRepository,
)
from app.infrastructure.ml.unavailable_engine import UnavailableEngine


class Container:
    """Composition root exposing factories for the application services.

    Repositories and services are cheap, stateless objects bound to a
    caller-supplied SQLAlchemy ``Session`` (one per request / one per test).
    The scoring engine is a singleton because loading a model is expensive.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        engine_factory: Callable[[], RecommendationEngine] | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._engines: dict[str, Callable[[], RecommendationEngine]] = {
            "unavailable": lambda: UnavailableEngine(),
        }
        if engine_factory is not None:
            # Allow tests to inject the engine implementation directly.
            self.register_engine("__injected__", engine_factory)
            self._settings = self._settings.model_copy(
                update={"ml_recommendation_engine": "__injected__"}
            )
        self._engine_singleton: RecommendationEngine | None = None

    # ── Registry ───────────────────────────────────────────────────────────
    def register_engine(self, name: str, factory: Callable[[], RecommendationEngine]) -> None:
        """Register a scoring engine so it can be selected via configuration."""
        self._engines[name] = factory
        self._engine_singleton = None

    # ── Repositories (per-session) ─────────────────────────────────────────
    def college_repository(self, session: Session) -> CollegeRepository:
        return SQLAlchemyCollegeRepository(session)

    def allotment_repository(self, session: Session) -> AllotmentRepository:
        return SQLAlchemyAllotmentRepository(session)

    def recommendation_repository(self, session: Session) -> RecommendationRepository:
        return SQLAlchemyRecommendationRepository(session)

    # ── Singleton collaborators ────────────────────────────────────────────
    @property
    def strategy_service(self) -> StrategyService:
        return StrategyService()

    @property
    def recommendation_engine(self) -> RecommendationEngine:
        """The active engine selected by ``ML_RECOMMENDATION_ENGINE``."""
        if self._engine_singleton is None:
            factory = self._engines.get(self._settings.ml_recommendation_engine)
            if factory is None:
                raise ValueError(
                    f"Unknown recommendation engine "
                    f"'{self._settings.ml_recommendation_engine}'. "
                    f"Registered engines: {sorted(self._engines)}."
                )
            self._engine_singleton = factory()
        return self._engine_singleton

    # ── Services (per-session) ─────────────────────────────────────────────
    def recommendation_service(self, session: Session) -> RecommendationService:
        return RecommendationService(
            engine=self.recommendation_engine,
            colleges=self.college_repository(session),
            allotments=self.allotment_repository(session),
            recommendations=self.recommendation_repository(session),
            strategy=self.strategy_service,
        )


def build_container() -> Container:
    """Return the default container for the current process."""
    return Container()
