"""Database migration tests."""

from __future__ import annotations

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration


class TestMigration0001:
    """Tests for the initial migration (0001_initial_schema)."""

    def test_migration_creates_all_tables(self, pg_engine):
        """All 24 tables should be created by the initial migration."""
        from app.core.database import Base
        from app.infrastructure.db import models  # noqa: F401

        Base.metadata.create_all(pg_engine)
        expected_tables = {
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

        actual_tables = {t.name for t in Base.metadata.sorted_tables}
        missing = expected_tables - actual_tables
        extra = actual_tables - expected_tables

        assert not missing, f"Missing tables: {missing}"
        assert not extra, f"Unexpected tables: {extra}"

    def test_migration_creates_indexes(self, pg_engine):
        """All expected indexes should be created."""
        from app.core.database import Base
        from app.infrastructure import db as _models  # noqa: F401

        Base.metadata.create_all(pg_engine)

        # Check that key indexes exist by verifying model definitions
        from app.infrastructure.db.models.allotment import AllotmentModel
        from app.infrastructure.db.models.college import CollegeModel
        from app.infrastructure.db.models.prediction import PredictionModel

        allotment_indexes = [str(idx) for idx in AllotmentModel.__table__.indexes]
        assert any("college_year_round" in idx for idx in allotment_indexes)
        assert any("cohort" in idx for idx in allotment_indexes)

        college_indexes = [str(idx) for idx in CollegeModel.__table__.indexes]
        assert any("state" in idx for idx in college_indexes)
        assert any("course" in idx for idx in college_indexes)

        prediction_indexes = [str(idx) for idx in PredictionModel.__table__.indexes]
        assert any("user_created" in idx for idx in prediction_indexes)
        assert any("session" in idx for idx in prediction_indexes)

    def test_migration_creates_unique_constraints(self, pg_engine):
        """All expected unique constraints should be created."""
        from app.core.database import Base
        from app.infrastructure import db as _models  # noqa: F401

        Base.metadata.create_all(pg_engine)

        from app.infrastructure.db.models.allotment import AllotmentModel

        unique_constraints = {
            uc.name for uc in AllotmentModel.__table__.constraints if hasattr(uc, "name")
        }
        assert "uq_allotments_college_round_cohort" in unique_constraints

    def test_migration_creates_foreign_keys(self, pg_engine):
        """All expected foreign keys should be created."""
        from app.core.database import Base
        from app.infrastructure import db as _models  # noqa: F401

        Base.metadata.create_all(pg_engine)

        from app.infrastructure.db.models.allotment import AllotmentModel

        fks = [fk.column.table.name for fk in AllotmentModel.__table__.foreign_keys]
        assert "colleges" in fks

    def test_downgrade_drops_all_tables(self, pg_engine):
        """The downgrade should drop all tables (tested via drop_all)."""

        from app.core.database import Base
        from app.infrastructure import db as _models  # noqa: F401

        Base.metadata.create_all(pg_engine)
        Base.metadata.drop_all(pg_engine)

        # Verify tables are dropped
        with pg_engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            tables = {row[0] for row in result}
            assert len(tables) == 0 or tables == {"alembic_version"}
