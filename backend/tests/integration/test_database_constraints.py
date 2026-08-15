"""Database constraint and uniqueness tests."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.integration


class TestUniqueConstraints:
    """Tests for unique constraints preventing duplicates."""

    def test_colleges_unique_code(self, db_session):
        from app.infrastructure.db.models.college import CollegeModel

        c1 = CollegeModel(
            code="UNIQ001",
            name="A",
            state="MH",
            city="Mumbai",
            course="MBBS",
            ownership="PRIVATE",
            annual_fee_inr=100000,
            total_seats=100,
            aiq_seats=15,
        )
        db_session.add(c1)
        db_session.commit()

        c2 = CollegeModel(
            code="UNIQ001",
            name="B",
            state="DL",
            city="Delhi",
            course="BDS",
            ownership="DEEMED",
            annual_fee_inr=200000,
            total_seats=50,
            aiq_seats=10,
        )
        db_session.add(c2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_users_unique_email(self, db_session):
        from app.infrastructure.db.models.user import UserModel

        u1 = UserModel(
            email="dup@e.com",
            password_hash="h1",
            full_name="U1",
            preferred_states=[],
        )
        db_session.add(u1)
        db_session.commit()

        u2 = UserModel(
            email="dup@e.com",
            password_hash="h2",
            full_name="U2",
            preferred_states=[],
        )
        db_session.add(u2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_feature_flags_unique_key(self, db_session):
        from app.infrastructure.db.models.feature_flag import FeatureFlagModel

        f1 = FeatureFlagModel(
            key="dup.key",
            name="F1",
            flag_type="BOOLEAN",
            default_value="true",
            current_value="true",
            current_source="DEFAULT",
        )
        db_session.add(f1)
        db_session.commit()

        f2 = FeatureFlagModel(
            key="dup.key",
            name="F2",
            flag_type="BOOLEAN",
            default_value="false",
            current_value="false",
            current_source="DEFAULT",
        )
        db_session.add(f2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_model_versions_unique_name_version(self, db_session):
        from app.infrastructure.db.models.model_version import ModelVersionModel

        v1 = ModelVersionModel(
            model_name="test_model",
            version="1.0.0",
            model_type="RULE_BASED",
            status="PRODUCTION",
        )
        db_session.add(v1)
        db_session.commit()

        v2 = ModelVersionModel(
            model_name="test_model",
            version="1.0.0",
            model_type="RULE_BASED",
            status="STAGING",
        )
        db_session.add(v2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_allotments_unique_composite(self, db_session):
        """Duplicate (college, year, round, quota, category, gender, pwd) rejected."""
        from app.domain.enums import Category, Course, Gender, QuotaType
        from app.infrastructure.db.models.allotment import AllotmentModel
        from app.infrastructure.db.models.college import CollegeModel

        college = CollegeModel(
            code="ALLT001",
            name="Test College",
            state="MH",
            city="Mumbai",
            course="MBBS",
            ownership="PRIVATE",
            annual_fee_inr=100000,
            total_seats=100,
            aiq_seats=15,
        )
        db_session.add(college)
        db_session.commit()

        a1 = AllotmentModel(
            college_id=college.id,
            college_code="ALLT001",
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
        db_session.add(a1)
        db_session.commit()

        a2 = AllotmentModel(
            college_id=college.id,
            college_code="ALLT001",
            course=Course.MBBS,
            counselling_year=2024,
            round_number=1,
            is_stray_round=False,
            quota_type=QuotaType.AIQ,
            category=Category.GENERAL,
            gender=Gender.NEUTRAL,
            is_pwd=False,
            opening_rank=81000,
            closing_rank=91000,
            seats_offered=15,
        )
        db_session.add(a2)
        with pytest.raises(IntegrityError):
            db_session.commit()
