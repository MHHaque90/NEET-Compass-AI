"""Composition root: engine selection, registration, wiring."""

from __future__ import annotations

import uuid

import pytest

from app.application.container import Container
from app.core.config import Settings
from app.domain.entities.recommendation import Recommendation
from app.domain.ports.recommendation_engine import RecommendationEngine
from app.infrastructure.ml.unavailable_engine import UnavailableEngine


class _ProbeEngine(RecommendationEngine):
    name = "probe"
    version = "0.0.0"

    def predict(self, candidate, college_id: uuid.UUID) -> Recommendation:
        raise NotImplementedError


def test_default_engine_is_unavailable() -> None:
    container = Container(settings=Settings(_env_file=None))
    engine = container.recommendation_engine
    assert isinstance(engine, UnavailableEngine)
    # Singleton: same instance across accesses.
    assert container.recommendation_engine is engine


def test_engine_selected_by_configuration() -> None:
    container = Container(settings=Settings(_env_file=None))
    container.register_engine("probe", _ProbeEngine)
    settings = Settings(_env_file=None, ml_recommendation_engine="probe")
    selected = Container(settings=settings)
    selected.register_engine("probe", _ProbeEngine)
    assert isinstance(selected.recommendation_engine, _ProbeEngine)


def test_unknown_engine_raises() -> None:
    container = Container(settings=Settings(_env_file=None, ml_recommendation_engine="nope"))
    with pytest.raises(ValueError, match="Unknown recommendation engine"):
        _ = container.recommendation_engine


def test_recommendation_service_is_wired(sample_candidate) -> None:
    container = Container(settings=Settings(_env_file=None))
    service = container.recommendation_service(None)  # session unused until methods run
    assert service is not None
