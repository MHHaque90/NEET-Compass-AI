"""
Target Engine - Phase 5
Target generation with readiness enforcement.

Per target-definition-phase4.md: NO TARGET READY FOR MODELLING.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from modelling.contracts.dataset import (
    SourceFacts,
    Targets,
)


class TargetReadinessStatus(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    NO_TARGET_READY = "NO_TARGET_READY"


@dataclass(frozen=True)
class TargetReadiness:
    """Target readiness result."""

    target_name: str
    is_ready: bool
    reason: str
    missing_requirements: list[str]


@dataclass(frozen=True)
class TargetDefinition:
    """
    Complete target definition with all metadata.
    """

    name: str
    definition: str
    source_fields: list[str]
    temporal_availability: str
    label_generation_rule: str
    missing_value_policy: str
    validity_rules: list[str]
    provenance: dict[str, Any]
    leakage_classification: str
    readiness_status: TargetReadinessStatus = TargetReadinessStatus.NOT_READY
    readiness_reason: str = ""

    def __post_init__(self):
        if not self.name:
            raise ValueError("Target name is required")
        if self.readiness_status == TargetReadinessStatus.READY and not self.readiness_reason:
            raise ValueError("READY target must have readiness_reason")


@dataclass
class TargetEngine:
    """
    Target generation engine.
    Enforces target readiness - returns NO_TARGET_READY if insufficient evidence.
    """

    target_definitions: dict[str, TargetDefinition] = field(default_factory=dict)
    target_version: str = "targets_v1"

    def __post_init__(self):
        self._register_default_targets()

    def _register_default_targets(self) -> None:
        """Register default target definitions per target-definition-phase4.md."""
        # Closing Rank Forecasting
        self.target_definitions["closing_rank"] = TargetDefinition(
            name="closing_rank",
            definition="Last rank admitted for college/course/quota/category/round/year",
            source_fields=[
                "allotment_rank",
                "counselling_year",
                "institute_code",
                "course",
                "quota",
                "category",
                "round",
            ],
            temporal_availability="Available after round completion",
            label_generation_rule="MAX(allotment_rank) per college/course/quota/category/round/year",
            missing_value_policy="NULL if no allotments for group",
            validity_rules=[
                "Must have at least 1 allotment record",
                "Rank must be >= 1",
                "Rank must be <= max NEET rank for year",
            ],
            provenance={
                "source": "Allotment canonical records",
                "aggregation": "MAX per group",
                "version": "v1",
            },
            leakage_classification="HIGH_RISK - Must only use rounds < prediction round, years < prediction year",
            readiness_status=TargetReadinessStatus.NO_TARGET_READY,
            readiness_reason="Insufficient historical coverage: Only MCC 2025 available. Need >=3 years for temporal validation.",
        )

        # Opening Rank Forecasting
        self.target_definitions["opening_rank"] = TargetDefinition(
            name="opening_rank",
            definition="First rank admitted for college/course/quota/category/round/year",
            source_fields=[
                "allotment_rank",
                "counselling_year",
                "institute_code",
                "course",
                "quota",
                "category",
                "round",
            ],
            temporal_availability="Available after round completion",
            label_generation_rule="MIN(allotment_rank) per college/course/quota/category/round/year",
            missing_value_policy="NULL if no allotments for group",
            validity_rules=[
                "Must have at least 1 allotment record",
                "Rank must be >= 1",
                "Rank must be <= max NEET rank for year",
            ],
            provenance={
                "source": "Allotment canonical records",
                "aggregation": "MIN per group",
                "version": "v1",
            },
            leakage_classification="HIGH_RISK - Must only use rounds < prediction round, years < prediction year",
            readiness_status=TargetReadinessStatus.NO_TARGET_READY,
            readiness_reason="Insufficient historical coverage: Only MCC 2025 available. Opening rank not in canonical model.",
        )

        # Admission Probability
        self.target_definitions["admission_probability"] = TargetDefinition(
            name="admission_probability",
            definition="P(admitted | student_rank, college, course, quota, category, round)",
            source_fields=["allotment records", "student rank distribution", "preference data"],
            temporal_availability="NOT AVAILABLE - No applicant pool data",
            label_generation_rule="Cannot be computed without applicant pool and preferences",
            missing_value_policy="N/A - Target not computable",
            validity_rules=[
                "Requires student preference data (PII - not available)",
                "Requires applicant pool counts (never published)",
            ],
            provenance={
                "source": "Not available",
                "note": "Fundamentally unidentifiable without applicant pool data",
            },
            leakage_classification="EXTREME_RISK - Requires applicant pool and preferences",
            readiness_status=TargetReadinessStatus.NO_TARGET_READY,
            readiness_reason="NO applicant pool data ever. No student preference data (PII protected).",
        )

        # Seat Allocation (multi-class)
        self.target_definitions["seat_allocation"] = TargetDefinition(
            name="seat_allocation",
            definition="Which college/course/quota/category a student gets",
            source_fields=["allotment records", "student preferences"],
            temporal_availability="NOT AVAILABLE - No preference data",
            label_generation_rule="Cannot be computed without student preferences",
            missing_value_policy="N/A - Target not computable",
            validity_rules=[
                "Requires student preference lists (PII)",
                "Requires full allotment chain per student",
            ],
            provenance={
                "source": "Not available",
                "note": "PII constraints prevent collecting preference data",
            },
            leakage_classification="EXTREME_RISK - Uses final allotment",
            readiness_status=TargetReadinessStatus.NO_TARGET_READY,
            readiness_reason="No student preference data available (PII protected). No historical preference data.",
        )

        # Vacancy After Round
        self.target_definitions["vacancy_after_round"] = TargetDefinition(
            name="vacancy_after_round",
            definition="Seats remaining after each round",
            source_fields=["vacancy reports", "seat matrix", "allotments"],
            temporal_availability="Available after round completion",
            label_generation_rule="Vacancy report data per college/course/quota/category/round",
            missing_value_policy="NULL if no vacancy report",
            validity_rules=[
                "Requires vacancy canonical model (not implemented)",
                "Vacancy >= 0 and <= total_seats",
            ],
            provenance={
                "source": "Vacancy reports (not ingested)",
                "note": "No vacancy canonical model exists",
            },
            leakage_classification="HIGH_RISK - Uses vacancy data from same round",
            readiness_status=TargetReadinessStatus.NO_TARGET_READY,
            readiness_reason="No vacancy canonical model. No vacancy data ingested.",
        )

    def generate_targets(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        target_name: str,
    ) -> Targets:
        """
        Generate target for a modelling record.
        Returns NO_TARGET_READY if target is not ready.
        """
        if target_name not in self.target_definitions:
            return Targets(
                target_version=self.target_version,
                target_ready=False,
                target_readiness_reason=f"UNKNOWN_TARGET: {target_name}",
            )

        target_def = self.target_definitions[target_name]

        if target_def.readiness_status == TargetReadinessStatus.NO_TARGET_READY:
            return Targets(
                target_version=self.target_version,
                target_ready=False,
                target_readiness_reason=target_def.readiness_reason,
            )

        if target_def.readiness_status == TargetReadinessStatus.NOT_READY:
            return Targets(
                target_version=self.target_version,
                target_ready=False,
                target_readiness_reason=f"TARGET_NOT_READY: {target_def.readiness_reason}",
            )

        # Target is READY - compute it
        value = self._compute_target(target_def, source_facts, historical_data)
        return Targets(
            **{target_name: value},
            target_version=self.target_version,
            target_ready=True,
            target_readiness_reason="READY",
        )

    def _compute_target(
        self,
        target_def: TargetDefinition,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
    ) -> Any:
        """Compute target value from source facts."""
        if target_def.name == "closing_rank":
            return source_facts.closing_rank
        elif target_def.name == "opening_rank":
            return source_facts.opening_rank
        return None

    def get_target_readiness(self, target_name: str) -> TargetReadiness:
        """Get readiness status for a target."""
        if target_name not in self.target_definitions:
            return TargetReadiness(
                target_name=target_name,
                is_ready=False,
                reason=f"UNKNOWN_TARGET: {target_name}",
                missing_requirements=["Target definition not found"],
            )

        target_def = self.target_definitions[target_name]

        if target_def.readiness_status == TargetReadinessStatus.READY:
            return TargetReadiness(
                target_name=target_name,
                is_ready=True,
                reason=target_def.readiness_reason,
                missing_requirements=[],
            )
        else:
            missing = []
            if target_name == "closing_rank":
                missing = [
                    "MCC 2021-2024 allotments ingested and validated",
                    "At least one state's historical allotments ingested",
                    "Minimum 4 years of data for temporal validation",
                ]
            elif target_name == "opening_rank":
                missing = [
                    "Opening rank aggregation in canonical model",
                    "MCC 2021-2024 allotments",
                    "Minimum 4 years of data",
                ]
            elif target_name == "admission_probability":
                missing = [
                    "Applicant pool data (never published)",
                    "Student preference data (PII protected)",
                ]
            elif target_name == "seat_allocation":
                missing = [
                    "Student preference data (PII)",
                    "Historical preference data",
                ]
            elif target_name == "vacancy_after_round":
                missing = [
                    "Vacancy canonical model implementation",
                    "Vacancy data ingestion",
                ]

            return TargetReadiness(
                target_name=target_name,
                is_ready=False,
                reason=target_def.readiness_reason,
                missing_requirements=missing,
            )

    def get_all_target_readiness(self) -> dict[str, TargetReadiness]:
        """Get readiness for all targets."""
        return {name: self.get_target_readiness(name) for name in self.target_definitions}

    def get_first_modelling_target(self) -> str:
        """Get the first target that would be ready for modelling."""
        # Per target-definition-phase4.md: NO TARGET READY
        return "NO_TARGET_READY"

    def get_target_version_metadata(self) -> dict[str, Any]:
        """Get target version metadata for reproducibility."""
        return {
            "version": self.target_version,
            "definitions": {
                name: {
                    "definition": td.definition,
                    "source_fields": td.source_fields,
                    "temporal_availability": td.temporal_availability,
                    "label_generation_rule": td.label_generation_rule,
                    "missing_value_policy": td.missing_value_policy,
                    "validity_rules": td.validity_rules,
                    "provenance": td.provenance,
                    "leakage_classification": td.leakage_classification,
                    "readiness_status": td.readiness_status.value,
                    "readiness_reason": td.readiness_reason,
                }
                for name, td in self.target_definitions.items()
            },
            "first_modelling_target": self.get_first_modelling_target(),
        }
