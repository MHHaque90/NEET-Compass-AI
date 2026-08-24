"""Tests for Target Readiness — Sprint 4.1.

Critical assertions:
- NO TARGET -> TRAINING_BLOCKED
- Target readiness requires evidence
"""

import pytest
from modelling.targets.engine import (
    TargetEngine,
    TargetReadinessStatus,
    TargetReadiness,
    TargetDefinition,
)
from modelling.contracts.dataset import SourceFacts


class TestTargetReadiness:
    """Test target readiness enforcement."""

    def test_no_target_ready_constant(self):
        """NO_TARGET_READY should be a valid status."""
        assert TargetReadinessStatus.NO_TARGET_READY == "NO_TARGET_READY"

    def test_engine_returns_no_target_ready(self):
        """TargetEngine should return NO_TARGET_READY for all targets."""
        engine = TargetEngine()
        assert engine.get_first_modelling_target() == "NO_TARGET_READY"

    def test_all_targets_no_target_ready(self):
        """All registered targets should have NO_TARGET_READY status."""
        engine = TargetEngine()
        for name, target in engine.target_definitions.items():
            assert target.readiness_status == TargetReadinessStatus.NO_TARGET_READY

    def test_generate_targets_returns_not_ready(self):
        """generate_targets should return target_ready=False for all targets."""
        engine = TargetEngine()

        source_facts = SourceFacts(
            counselling_year=2025, state="ALL_INDIA", counselling_authority="MCC / DGHS",
            round="round_1", course="MBBS", institute="Test College", institute_code="TEST001",
            quota="ai", category="gn", total_seats=100, allotment_count=1,
            closing_rank=50000, score=600.0,
        )

        for target_name in ["closing_rank", "opening_rank", "admission_probability",
                            "seat_allocation", "vacancy_after_round"]:
            targets = engine.generate_targets(source_facts, {}, target_name)
            assert targets.target_ready is False
            # The reason should indicate NOT_READY or NO_TARGET_READY
            assert targets.target_readiness_reason != "READY"

    def test_get_target_readiness_returns_not_ready(self):
        """get_target_readiness should return is_ready=False for all targets."""
        engine = TargetEngine()
        for target_name in ["closing_rank", "opening_rank", "admission_probability",
                            "seat_allocation", "vacancy_after_round"]:
            readiness = engine.get_target_readiness(target_name)
            assert isinstance(readiness, TargetReadiness)
            assert readiness.is_ready is False
            assert len(readiness.missing_requirements) > 0

    def test_closing_rank_missing_requirements(self):
        """closing_rank should list specific missing requirements."""
        engine = TargetEngine()
        readiness = engine.get_target_readiness("closing_rank")
        missing = readiness.missing_requirements
        assert any("MCC 2021-2024" in m for m in missing)
        assert any("state" in m.lower() for m in missing)
        assert any("4 years" in m or "temporal" in m.lower() for m in missing)

    def test_admission_probability_fundamentally_unavailable(self):
        """admission_probability should be fundamentally unavailable."""
        engine = TargetEngine()
        readiness = engine.get_target_readiness("admission_probability")
        assert readiness.is_ready is False
        missing = readiness.missing_requirements
        assert any("applicant pool" in m.lower() for m in missing)
        assert any("preference" in m.lower() for m in missing)

    def test_unknown_target_returns_not_ready(self):
        """Unknown target should return NOT_READY."""
        engine = TargetEngine()
        readiness = engine.get_target_readiness("unknown_target_xyz")
        assert readiness.is_ready is False
        assert "UNKNOWN_TARGET" in readiness.reason

    def test_get_all_target_readiness(self):
        """get_all_target_readiness should return dict for all targets."""
        engine = TargetEngine()
        all_readiness = engine.get_all_target_readiness()
        assert isinstance(all_readiness, dict)
        assert len(all_readiness) == 5
        for name, readiness in all_readiness.items():
            assert isinstance(readiness, TargetReadiness)
            assert readiness.is_ready is False

    def test_target_definition_structure(self):
        """TargetDefinition should have all required fields."""
        engine = TargetEngine()
        for name, target in engine.target_definitions.items():
            assert target.name == name
            assert target.definition
            assert isinstance(target.source_fields, list)
            assert target.temporal_availability
            assert target.label_generation_rule
            assert target.missing_value_policy
            assert isinstance(target.validity_rules, list)
            assert isinstance(target.provenance, dict)
            assert target.leakage_classification
            assert target.readiness_status in TargetReadinessStatus

    def test_target_version_metadata(self):
        """Target version metadata should be available."""
        engine = TargetEngine()
        metadata = engine.get_target_version_metadata()
        assert "version" in metadata
        assert "definitions" in metadata
        assert "first_modelling_target" in metadata
        assert metadata["first_modelling_target"] == "NO_TARGET_READY"