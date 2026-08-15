"""Database model unit tests.

Tests all ORM models without requiring a database connection.
Models are tested in isolation using in-memory SQLite.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.infrastructure import db as _  # noqa: F401 - registers models


@pytest.fixture
def in_memory_session():
    """Provide an in-memory SQLite session for model testing."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def engine():
    """Provide an in-memory SQLite engine."""
    return create_engine("sqlite+pysqlite:///:memory:")


class TestModelImports:
    """All 24 models should be importable and registered on Base."""

    def test_all_models_importable(self):
        from app.infrastructure.db import models

        expected = [
            "AllotmentModel",
            "CandidateModel",
            "CategoryModel",
            "CollegeModel",
            "CourseModel",
            "DataSourceModel",
            "DistrictModel",
            "ETLErrorModel",
            "ETLRunModel",
            "FeeModel",
            "FeatureFlagModel",
            "LogModel",
            "ModelVersionModel",
            "PredictionModel",
            "PredictionHistoryModel",
            "QuotaModel",
            "RecommendationModel",
            "RoundModel",
            "SeatMatrixModel",
            "SourceFileModel",
            "StateModel",
            "SystemSettingModel",
            "UploadModel",
            "UserModel",
        ]
        for name in expected:
            assert hasattr(models, name), f"{name} not in models package"

    def test_all_models_registered_on_base(self):
        from app.infrastructure.db import models  # noqa: F401

        table_names = {t.name for t in Base.metadata.tables.values()}
        expected = {
            "states",
            "districts",
            "categories",
            "quotas",
            "rounds",
            "courses",
            "colleges",
            "fees",
            "seat_matrix",
            "allotments",
            "candidates",
            "recommendations",
            "users",
            "uploads",
            "predictions",
            "prediction_history",
            "data_sources",
            "source_files",
            "etl_runs",
            "etl_errors",
            "model_versions",
            "feature_flags",
            "system_settings",
            "logs",
        }
        assert table_names == expected


class TestTimestampMixin:
    """All tables with timestamps should have created_at and updated_at."""

    def test_timestamp_mixin_columns(self):
        from app.infrastructure.db.models._base import TimestampMixin

        assert hasattr(TimestampMixin, "created_at")
        assert hasattr(TimestampMixin, "updated_at")

    def test_models_use_timestamp_mixin(self):
        from app.infrastructure.db.models.college import CollegeModel
        from app.infrastructure.db.models.state import StateModel
        from app.infrastructure.db.models.user import UserModel

        for model in [CollegeModel, UserModel, StateModel]:
            assert hasattr(model.__table__.columns, "created_at")
            assert hasattr(model.__table__.columns, "updated_at")


class TestSoftDelete:
    """Tables with soft delete should have deleted_at column."""

    def test_colleges_have_soft_delete(self):
        from app.infrastructure.db.models.college import CollegeModel

        assert "deleted_at" in CollegeModel.__table__.columns

    def test_users_have_soft_delete(self):
        from app.infrastructure.db.models.user import UserModel

        assert "deleted_at" in UserModel.__table__.columns

    def test_lookup_tables_have_soft_delete(self):
        from app.infrastructure.db.models.category import CategoryModel
        from app.infrastructure.db.models.course import CourseModel
        from app.infrastructure.db.models.district import DistrictModel
        from app.infrastructure.db.models.quota import QuotaModel
        from app.infrastructure.db.models.round import RoundModel
        from app.infrastructure.db.models.state import StateModel

        models_to_check = [
            StateModel,
            DistrictModel,
            CategoryModel,
            QuotaModel,
            RoundModel,
            CourseModel,
        ]
        for model in models_to_check:
            assert "deleted_at" in model.__table__.columns


class TestModelDefaults:
    """Test that all models have correct default values."""

    def test_seat_matrix_default_seats_filled(self):
        from app.infrastructure.db.models.seat_matrix import SeatMatrixModel

        col = SeatMatrixModel.__table__.columns["seats_filled"]
        assert col.default is not None

    def test_allotments_default_seats_offered(self):
        from app.infrastructure.db.models.allotment import AllotmentModel

        col = AllotmentModel.__table__.columns["seats_offered"]
        assert col.default is not None

    def test_users_default_is_active(self):
        from app.infrastructure.db.models.user import UserModel

        col = UserModel.__table__.columns["is_active"]
        assert col.default is not None
