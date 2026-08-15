"""Database relationship tests."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


class TestTableRelationships:
    """Tests for foreign key relationships between tables."""

    def test_allotments_college_relationship(self, db_session):
        """Allotment should reference a valid college."""
        from app.domain.enums import Category, Course, Gender, QuotaType
        from app.infrastructure.db.models.allotment import AllotmentModel
        from app.infrastructure.db.models.college import CollegeModel

        college = CollegeModel(
            code="TEST001",
            name="Test College",
            state="MAHARASHTRA",
            city="Mumbai",
            course="MBBS",
            ownership="PRIVATE",
            annual_fee_inr=100000,
            total_seats=100,
            aiq_seats=15,
        )
        db_session.add(college)
        db_session.commit()

        allotment = AllotmentModel(
            college_id=college.id,
            college_code="TEST001",
            course=Course.MBBS,
            counselling_year=2024,
            round_number=1,
            is_stray_round=False,
            quota_type=QuotaType.AIQ,
            category=Category.GENERAL,
            gender=Gender.NEUTRAL,
            is_pwd=False,
            opening_rank=80000,
            closing_rank=90000,
            seats_offered=15,
        )
        db_session.add(allotment)
        db_session.commit()
        assert allotment.college_id == college.id

    def test_prediction_user_relationship(self, db_session):
        """Prediction should reference a valid user."""
        from app.domain.enums import Category, Gender, QuotaType
        from app.infrastructure.db.models.prediction import PredictionModel
        from app.infrastructure.db.models.user import UserModel

        user = UserModel(
            email="t1@e.com",
            password_hash="h",
            full_name="T1",
            air=85000,
            marks=620,
            category=Category.OBC,
            gender=Gender.NEUTRAL,
            quota_type=QuotaType.AIQ,
            preferred_states=["MAHARASHTRA"],
        )
        db_session.add(user)
        db_session.commit()

        prediction = PredictionModel(
            user_id=user.id,
            session_id="sess_001",
            air=85000,
            marks=620,
            category=Category.OBC,
            gender=Gender.NEUTRAL,
            quota_type=QuotaType.AIQ,
            preferred_states=["MAHARASHTRA"],
            counselling_year=2024,
            engine_name="test",
            total_colleges_evaluated=0,
            total_recommendations=0,
            prediction_status="PENDING",
        )
        db_session.add(prediction)
        db_session.commit()
        assert prediction.user_id == user.id

    def test_etl_error_run_relationship(self, db_session):
        """ETL error should reference a valid ETL run."""
        from app.infrastructure.db.models.etl_error import ETLErrorModel
        from app.infrastructure.db.models.etl_run import ETLRunModel

        run = ETLRunModel(
            pipeline_name="test",
            run_type="INCREMENTAL",
            status="RUNNING",
            etl_version="1.0.0",
            config_snapshot={},
        )
        db_session.add(run)
        db_session.commit()

        error = ETLErrorModel(
            etl_run_id=run.id,
            stage="VALIDATE",
            severity="ERROR",
            error_code="INVALID_VALUE",
            error_message="Invalid value",
        )
        db_session.add(error)
        db_session.commit()
        assert error.etl_run_id == run.id

    def test_source_file_data_source_relationship(self, db_session):
        """Source file should reference a valid data source."""
        from app.infrastructure.db.models.data_source import DataSourceModel
        from app.infrastructure.db.models.source_file import SourceFileModel

        source = DataSourceModel(
            code="test_src",
            name="Test Source",
            source_type="MCC_OFFICIAL",
            status="ACTIVE",
            schema_version="1.0",
        )
        db_session.add(source)
        db_session.commit()

        sf = SourceFileModel(
            data_source_id=source.id,
            file_name="test.xlsx",
            file_version="1",
            academic_year=2024,
        )
        db_session.add(sf)
        db_session.commit()
        assert sf.data_source_id == source.id

    def test_prediction_history_prediction_relationship(self, db_session):
        """Prediction history should reference a valid prediction."""
        from app.domain.enums import Category, Gender, QuotaType
        from app.infrastructure.db.models.prediction import PredictionModel
        from app.infrastructure.db.models.prediction_history import PredictionHistoryModel
        from app.infrastructure.db.models.user import UserModel

        user = UserModel(
            email="t2@e.com",
            password_hash="h",
            full_name="T2",
            air=85000,
            marks=620,
            category=Category.OBC,
            gender=Gender.NEUTRAL,
            quota_type=QuotaType.AIQ,
            preferred_states=[],
        )
        db_session.add(user)
        db_session.commit()

        prediction = PredictionModel(
            user_id=user.id,
            session_id="sess_003",
            air=85000,
            marks=620,
            category=Category.OBC,
            gender=Gender.NEUTRAL,
            quota_type=QuotaType.AIQ,
            preferred_states=[],
            counselling_year=2024,
            engine_name="test",
            total_colleges_evaluated=0,
            total_recommendations=0,
            prediction_status="PENDING",
        )
        db_session.add(prediction)
        db_session.commit()

        history = PredictionHistoryModel(
            prediction_id=prediction.id,
            course="MBBS",
            quota_type="AIQ",
            category="OBC",
            gender="NEUTRAL",
            is_pwd=False,
        )
        db_session.add(history)
        db_session.commit()
        assert history.prediction_id == prediction.id

    def test_system_setting_feature_flag_relationship(self, db_session):
        """System setting should reference a valid feature flag."""
        from app.infrastructure.db.models.feature_flag import FeatureFlagModel
        from app.infrastructure.db.models.system_setting import SystemSettingModel

        flag = FeatureFlagModel(
            key="test.flag",
            name="Test Flag",
            flag_type="BOOLEAN",
            default_value="false",
            current_value="false",
            current_source="DEFAULT",
        )
        db_session.add(flag)
        db_session.commit()

        setting = SystemSettingModel(
            scope="GLOBAL",
            key="test.setting",
            value="123",
            value_type="INTEGER",
            feature_flag_id=flag.id,
        )
        db_session.add(setting)
        db_session.commit()
        assert setting.feature_flag_id == flag.id
