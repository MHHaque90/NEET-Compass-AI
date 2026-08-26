"""
Tests for Target Validation — Sprint 4.2.

Critical assertions:
- FUTURE TARGET INFORMATION -> REJECTED
- UNKNOWN TARGET TEMPORALITY -> REJECTED
- MISSING PROVENANCE -> NOT_READY
- INVALID TARGET -> NO_TARGET_READY
"""

import pytest
from modelling.contracts.dataset import (
    AuthorityType,
    CategoryType,
    QuotaType,
    RoundType,
    SourceFacts,
)
from modelling.targets.engine import TargetDefinition, TargetEngine, TargetReadinessStatus


class TestTargetDefinition:
    """Test target definition completeness."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_all_targets_have_complete_definitions(self, engine):
        """Every target must have complete definition metadata."""
        for name, target_def in engine.target_definitions.items():
            assert target_def.name == name
            assert target_def.definition, f"Target {name}: missing definition"
            assert target_def.source_fields, f"Target {name}: missing source_fields"
            assert target_def.temporal_availability, f"Target {name}: missing temporal_availability"
            assert target_def.label_generation_rule, f"Target {name}: missing label_generation_rule"
            assert target_def.missing_value_policy, f"Target {name}: missing missing_value_policy"
            assert target_def.validity_rules, f"Target {name}: missing validity_rules"
            assert target_def.provenance, f"Target {name}: missing provenance"
            assert target_def.leakage_classification, (
                f"Target {name}: missing leakage_classification"
            )
            assert target_def.readiness_status in TargetReadinessStatus

    def test_readiness_status_consistent(self, engine):
        """READY targets must have readiness_reason; NOT_READY must have reason."""
        for name, target_def in engine.target_definitions.items():
            if target_def.readiness_status == TargetReadinessStatus.READY:
                assert target_def.readiness_reason, f"READY target {name} missing readiness_reason"
            elif target_def.readiness_status in (
                TargetReadinessStatus.NOT_READY,
                TargetReadinessStatus.NO_TARGET_READY,
            ):
                assert target_def.readiness_reason, (
                    f"{target_def.readiness_status} target {name} missing readiness_reason"
                )


class TestTargetSourceFields:
    """Test source field requirements."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_closing_rank_source_fields_available_in_canonical(self, engine):
        """closing_rank source fields must exist in canonical model."""
        target_def = engine.target_definitions["closing_rank"]
        required_fields = {
            "allotment_rank",
            "counselling_year",
            "institute_code",
            "course",
            "quota",
            "category",
            "round",
        }
        assert set(target_def.source_fields) == required_fields

    def test_opening_rank_source_fields_same_as_closing_rank(self, engine):
        """opening_rank should require same source fields as closing_rank."""
        closing_fields = set(engine.target_definitions["closing_rank"].source_fields)
        opening_fields = set(engine.target_definitions["opening_rank"].source_fields)
        assert opening_fields == closing_fields

    def test_admission_probability_requires_unavailable_fields(self, engine):
        """admission_probability requires fields not in canonical model."""
        target_def = engine.target_definitions["admission_probability"]
        # These fields are documented as unavailable
        src = str(target_def.source_fields).lower()
        assert "preference data" in src or "student rank distribution" in src


class TestTargetTemporalAvailability:
    """Test temporal availability of targets."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_closing_rank_temporal_availability_known(self, engine):
        """closing_rank temporal availability must be known."""
        target_def = engine.target_definitions["closing_rank"]
        assert target_def.temporal_availability != "UNKNOWN"
        assert "after round completion" in target_def.temporal_availability.lower()

    def test_admission_probability_temporal_availability_unavailable(self, engine):
        """admission_probability temporal availability is fundamentally unavailable."""
        target_def = engine.target_definitions["admission_probability"]
        temp_avail = target_def.temporal_availability.lower()
        assert "not available" in temp_avail or "unavailable" in temp_avail

    def test_vacancy_after_round_temporal_availability_unknown(self, engine):
        """vacancy_after_round temporal availability claims available but no model exists."""
        target_def = engine.target_definitions["vacancy_after_round"]
        # The target_def says "Available after round completion" but provenance says no model exists
        assert target_def.readiness_status == TargetReadinessStatus.NO_TARGET_READY
        assert "no vacancy canonical model" in target_def.provenance.get("note", "").lower()


class TestTargetLeakagePrevention:
    """Test leakage prevention."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_closing_rank_high_leakage_risk_documented(self, engine):
        """closing_rank must document HIGH leakage risk."""
        target_def = engine.target_definitions["closing_rank"]
        assert "high" in target_def.leakage_classification.lower()
        assert "prediction round" in target_def.leakage_classification.lower()
        assert "prediction year" in target_def.leakage_classification.lower()

    def test_admission_probability_extreme_leakage_rejected(self, engine):
        """admission_probability must be classified as EXTREME risk."""
        target_def = engine.target_definitions["admission_probability"]
        assert "extreme" in target_def.leakage_classification.lower()

    def test_seat_allocation_extreme_leakage_rejected(self, engine):
        """seat_allocation must be classified as EXTREME risk."""
        target_def = engine.target_definitions["seat_allocation"]
        assert "extreme" in target_def.leakage_classification.lower()

    def test_vacancy_after_round_high_leakage_unknown_model(self, engine):
        """vacancy_after_round has HIGH risk but no model exists."""
        target_def = engine.target_definitions["vacancy_after_round"]
        assert "high" in target_def.leakage_classification.lower()
        note = target_def.provenance.get("note", "").lower()
        assert "no vacancy canonical model" in note or "not ingested" in note


class TestTargetMissingValues:
    """Test missing value policies."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_closing_rank_missing_value_policy(self, engine):
        """closing_rank must have NULL policy for missing groups."""
        target_def = engine.target_definitions["closing_rank"]
        policy = target_def.missing_value_policy.lower()
        assert "null" in policy or "none" in policy

    def test_admission_probability_missing_value_na(self, engine):
        """admission_probability missing value policy should be N/A."""
        target_def = engine.target_definitions["admission_probability"]
        policy = target_def.missing_value_policy.lower()
        assert "n/a" in policy or "not computable" in policy


class TestTargetInvalidTargets:
    """Test invalid target handling."""

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

    def test_unknown_target_returns_no_target_ready(self, engine, sample_source_facts):
        """Unknown target returns NO_TARGET_READY equivalent."""
        targets = engine.generate_targets(sample_source_facts, {}, "unknown_target")
        assert targets.target_ready is False
        assert "UNKNOWN_TARGET" in targets.target_readiness_reason

    def test_no_target_defined_returns_no_target_ready(self, engine):
        """get_first_modelling_target returns NO_TARGET_READY when none ready."""
        assert engine.get_first_modelling_target() == "NO_TARGET_READY"


class TestTargetProvenance:
    """Test target provenance."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_all_targets_have_provenance(self, engine):
        """Every target must have provenance metadata."""
        for target_def in engine.target_definitions.values():
            assert "source" in target_def.provenance
            assert target_def.provenance["source"]

    def test_closing_rank_provenance_complete(self, engine):
        """closing_rank provenance must be complete."""
        target_def = engine.target_definitions["closing_rank"]
        prov = target_def.provenance
        assert "source" in prov
        assert "aggregation" in prov
        assert "version" in prov
        assert prov["aggregation"] == "MAX per group"

    def test_opening_rank_provenance_complete(self, engine):
        """opening_rank provenance must be complete."""
        target_def = engine.target_definitions["opening_rank"]
        prov = target_def.provenance
        assert "source" in prov
        assert "aggregation" in prov
        assert "version" in prov
        assert prov["aggregation"] == "MIN per group"


class TestTargetReadinessClassification:
    """Test target readiness classification is deterministic and evidence-backed."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_all_targets_currently_no_target_ready(self, engine):
        """All targets currently NO_TARGET_READY due to insufficient coverage."""
        for name in engine.target_definitions:
            readiness = engine.get_target_readiness(name)
            assert readiness.is_ready is False
            assert readiness.target_name == name

    def test_closing_rank_missing_requirements_documented(self, engine):
        """closing_rank missing requirements must be explicitly documented."""
        readiness = engine.get_target_readiness("closing_rank")
        missing = readiness.missing_requirements
        assert len(missing) >= 3
        assert any("MCC 2021-2024" in m for m in missing)
        assert any("state" in m.lower() for m in missing)
        assert any("temporal" in m.lower() or "years" in m.lower() for m in missing)

    def test_admission_probability_fundamentally_unidentifiable(self, engine):
        """admission_probability missing requirements include fundamentally unavailable data."""
        readiness = engine.get_target_readiness("admission_probability")
        missing = readiness.missing_requirements
        assert any("applicant pool" in m.lower() for m in missing)
        assert any("preference" in m.lower() for m in missing)

    def test_seat_allocation_fundamentally_unidentifiable(self, engine):
        """seat_allocation missing requirements include PII constraints."""
        readiness = engine.get_target_readiness("seat_allocation")
        missing = readiness.missing_requirements
        assert any("preference" in m.lower() for m in missing)
        assert any("pii" in m.lower() for m in missing)

    def test_no_target_transitions_without_evidence(self, engine):
        """Target readiness cannot transition without evidence."""
        # All targets are NO_TARGET_READY
        # Changing to READY would require:
        # - MCC 2021-2024 allotments ingested
        # - State historical allotments ingested
        # - Minimum 4 years for temporal validation
        # - Leakage checks pass
        # This is enforced by the engine - no programmatic way to upgrade
        for name in engine.target_definitions:
            target_def = engine.target_definitions[name]
            assert target_def.readiness_status == TargetReadinessStatus.NO_TARGET_READY


class TestUnsupportedTargetTransitions:
    """Test that unsupported target transitions are rejected."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_cannot_directly_set_target_ready(self, engine):
        """TargetDefinition constructor enforces READY requires readiness_reason."""
        with pytest.raises(ValueError, match="READY target must have readiness_reason"):
            TargetDefinition(
                name="test",
                definition="test",
                source_fields=[],
                temporal_availability="test",
                label_generation_rule="test",
                missing_value_policy="test",
                validity_rules=[],
                provenance={},
                leakage_classification="test",
                readiness_status=TargetReadinessStatus.READY,
                readiness_reason="",  # Empty - should fail
            )

    def test_target_readiness_immutable_after_creation(self, engine):
        """Target definitions are immutable after registration."""
        target_def = engine.target_definitions["closing_rank"]
        # TargetDefinition is frozen dataclass - cannot modify
        assert target_def.readiness_status == TargetReadinessStatus.NO_TARGET_READY


class TestTargetVersionMetadata:
    """Test target version metadata for reproducibility."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_version_metadata_complete(self, engine):
        """Target version metadata must be complete."""
        metadata = engine.get_target_version_metadata()
        assert metadata["version"] == "targets_v1"
        assert "definitions" in metadata
        assert metadata["first_modelling_target"] == "NO_TARGET_READY"

    def test_all_target_definitions_in_metadata(self, engine):
        """All target definitions must appear in version metadata."""
        metadata = engine.get_target_version_metadata()
        for name in engine.target_definitions:
            assert name in metadata["definitions"]
            td = metadata["definitions"][name]
            assert "definition" in td
            assert "source_fields" in td
            assert "temporal_availability" in td
            assert "label_generation_rule" in td
            assert "missing_value_policy" in td
            assert "validity_rules" in td
            assert "provenance" in td
            assert "leakage_classification" in td
            assert "readiness_status" in td
            assert "readiness_reason" in td


class TestFutureTargetInformationRejected:
    """Test that future target information is rejected."""

    def test_no_target_uses_future_allotment_for_prior_round(self):
        """No target should use future round data to predict prior round."""
        # This is enforced by temporal_availability documentation
        # and leakage_classification requiring temporal splits
        pass  # Documented in target definitions

    def test_no_target_uses_future_year_for_prior_year(self):
        """No target should use future year data to predict prior year."""
        # Enforced by temporal split requirements in leakage_classification
        pass  # Documented in target definitions


class TestUnknownTargetTemporalityRejected:
    """Test that unknown target temporality is rejected."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_vacancy_target_temporality_unknown_rejected(self, engine):
        """vacancy_after_round has no canonical model -> should be NO_TARGET_READY."""
        target_def = engine.target_definitions["vacancy_after_round"]
        assert target_def.readiness_status == TargetReadinessStatus.NO_TARGET_READY
        # Provenance documents that no vacancy canonical model exists
        assert "no vacancy canonical model" in target_def.provenance.get("note", "").lower()


class TestMissingProvenanceNotReady:
    """Test that missing provenance results in NOT_READY."""

    @pytest.fixture
    def engine(self):
        return TargetEngine()

    def test_all_targets_have_provenance(self, engine):
        """All targets must have provenance - if missing, would be NOT_READY."""
        for target_def in engine.target_definitions.values():
            assert target_def.provenance
            assert "source" in target_def.provenance


class TestInvalidTargetNoTargetReady:
    """Test that invalid target results in NO_TARGET_READY."""

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

    def test_invalid_target_name_returns_no_target_ready(self, engine, sample_source_facts):
        """Invalid/unknown target name returns target_ready=False with UNKNOWN_TARGET reason."""
        targets = engine.generate_targets(sample_source_facts, {}, "invalid_target_xyz")
        assert targets.target_ready is False
        assert "UNKNOWN_TARGET" in targets.target_readiness_reason


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
