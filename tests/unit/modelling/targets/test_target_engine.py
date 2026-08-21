"""
Tests for Target Engine - Phase 5
"""

import pytest
from modelling.targets.engine import TargetEngine, TargetReadinessStatus
from modelling.contracts.dataset import (
    SourceFacts,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
)


class TestTargetEngine:
    @pytest.fixture
    def engine(self):
        return TargetEngine()

    @pytest.fixture
    def sample_source_facts(self):
        return SourceFacts(
            counselling_year=2025,
            state="ALL_INDIA",
            counselling_authority=AuthorityType.MCC,
            round=RoundType.ROUND_1,
            course="MBBS",
            institute="AIIMS Delhi",
            institute_code="AIMS001",
            quota=QuotaType.AI,
            category=CategoryType.GN,
            total_seats=100,
            allotment_count=100,
            closing_rank=5000,
        )

    def test_no_target_ready_for_closing_rank(self, engine, sample_source_facts):
        targets = engine.generate_targets(sample_source_facts, {}, "closing_rank")
        assert targets.target_ready is False
        assert "Insufficient historical coverage" in targets.target_readiness_reason
        assert targets.closing_rank is None

    def test_no_target_ready_for_all_targets(self, engine, sample_source_facts):
        for target_name in ["closing_rank", "opening_rank", "admission_probability", "seat_allocation", "vacancy_after_round"]:
            targets = engine.generate_targets(sample_source_facts, {}, target_name)
            assert targets.target_ready is False
            # Each target has its own specific reason
            assert targets.target_readiness_reason is not None
            assert len(targets.target_readiness_reason) > 0

    def test_unknown_target_returns_not_ready(self, engine, sample_source_facts):
        targets = engine.generate_targets(sample_source_facts, {}, "unknown_target")
        assert targets.target_ready is False
        assert "UNKNOWN_TARGET" in targets.target_readiness_reason

    def test_target_readiness_details(self, engine):
        readiness = engine.get_target_readiness("closing_rank")
        assert readiness.target_name == "closing_rank"
        assert readiness.is_ready is False
        assert "Insufficient historical coverage" in readiness.reason
        assert len(readiness.missing_requirements) > 0

    def test_all_targets_not_ready(self, engine):
        all_readiness = engine.get_all_target_readiness()
        for name, readiness in all_readiness.items():
            assert readiness.is_ready is False

    def test_first_modelling_target_is_none(self, engine):
        assert engine.get_first_modelling_target() == "NO_TARGET_READY"

    def test_target_version_metadata(self, engine):
        metadata = engine.get_target_version_metadata()
        assert metadata["version"] == "targets_v1"
        assert "closing_rank" in metadata["definitions"]
        assert metadata["first_modelling_target"] == "NO_TARGET_READY"
