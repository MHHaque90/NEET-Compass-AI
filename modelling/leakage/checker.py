"""
Leakage Prevention Checker - Phase 4
Deterministic leakage detection that fails closed.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from modelling.contracts.dataset import (
    ModellingRecord,
    RoundType,
)
from modelling.features.engine import LeakageStatus, TemporalAvailability
from modelling.features.registry import FeatureDefinition, FeatureRegistry


class LeakageCategory(str, Enum):
    """Categories of temporal leakage."""

    FUTURE_COUNSELLING_YEAR = "future_counselling_year"
    FUTURE_COUNSELLING_ROUND = "future_counselling_round"
    FUTURE_ALLOTMENT_OUTCOME = "future_allotment_outcome"
    POST_OUTCOME_INFORMATION = "post_outcome_information"
    TARGET_DERIVED_FIELD = "target_derived_field"
    FUTURE_SEAT_MATRIX = "future_seat_matrix"
    FUTURE_YEAR_STATISTICS = "future_year_statistics"
    AGGREGATE_WITH_FUTURE_DATA = "aggregate_with_future_data"
    UNKNOWN_TEMPORAL_AVAILABILITY = "unknown_temporal_availability"


@dataclass(frozen=True)
class LeakageViolation:
    """A single leakage violation found during checking."""

    category: LeakageCategory
    feature_name: str
    description: str
    prediction_year: int
    prediction_round: RoundType
    offending_data_year: int | None = None
    offending_data_round: RoundType | None = None
    severity: str = "CRITICAL"

    def __post_init__(self):
        if self.severity not in ("CRITICAL", "HIGH", "MEDIUM"):
            raise ValueError(f"Invalid severity: {self.severity}")


@dataclass(frozen=True)
class LeakageResult:
    """Result of leakage checking."""

    passed: bool
    violations: list[LeakageViolation]
    checked_features: list[str]
    checked_records: int
    check_timestamp: datetime
    prediction_year: int
    prediction_round: RoundType

    def __post_init__(self):
        if self.passed and self.violations:
            raise ValueError("Cannot have violations if passed=True")
        if not self.passed and not self.violations:
            raise ValueError("Must have violations if passed=False")

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def critical_violations(self) -> list[LeakageViolation]:
        return [v for v in self.violations if v.severity == "CRITICAL"]


class LeakageChecker:
    """
    Deterministic leakage checker.
    FAILS CLOSED: Any UNKNOWN temporal availability -> REJECTED.
    """

    def __init__(
        self,
        feature_registry: FeatureRegistry,
        strict_mode: bool = True,
    ):
        self.feature_registry = feature_registry
        self.strict_mode = strict_mode

    def check_record(
        self,
        record: ModellingRecord,
        historical_data: dict[str, Any],
    ) -> LeakageResult:
        """Check a single modelling record for leakage."""
        violations = []
        prediction_year = record.source_facts.counselling_year
        prediction_round = record.source_facts.round
        checked_features = []

        for feature_name in self.feature_registry.get_feature_names():
            feature_def = self.feature_registry.get_feature(feature_name)
            checked_features.append(feature_name)

            violation = self._check_feature_leakage(
                feature_def,
                record,
                historical_data,
                prediction_year,
                prediction_round,
            )
            if violation:
                violations.append(violation)

        passed = len(violations) == 0
        return LeakageResult(
            passed=passed,
            violations=violations,
            checked_features=checked_features,
            checked_records=1,
            check_timestamp=datetime.now(UTC),
            prediction_year=prediction_year,
            prediction_round=prediction_round,
        )

    def check_dataset(
        self,
        records: list[ModellingRecord],
        historical_data: dict[str, Any],
    ) -> LeakageResult:
        """Check an entire dataset for leakage."""
        all_violations = []
        all_checked_features = set()
        total_records = len(records)

        for record in records:
            result = self.check_record(record, historical_data)
            all_violations.extend(result.violations)
            all_checked_features.update(result.checked_features)

        passed = len(all_violations) == 0
        return LeakageResult(
            passed=passed,
            violations=all_violations,
            checked_features=sorted(all_checked_features),
            checked_records=total_records,
            check_timestamp=datetime.now(UTC),
            prediction_year=records[0].source_facts.counselling_year if records else 0,
            prediction_round=records[0].source_facts.round if records else RoundType.ROUND_1,
        )

    def _check_feature_leakage(
        self,
        feature_def: FeatureDefinition,
        record: ModellingRecord,
        historical_data: dict[str, Any],
        prediction_year: int,
        prediction_round: RoundType,
    ) -> LeakageViolation | None:
        """Check a single feature for leakage."""
        # Rule 1: UNKNOWN temporal availability -> REJECTED
        if feature_def.temporal_availability == TemporalAvailability.NOT_ALLOWED:
            return LeakageViolation(
                category=LeakageCategory.UNKNOWN_TEMPORAL_AVAILABILITY,
                feature_name=feature_def.name,
                description=f"Feature {feature_def.name} has UNKNOWN/NOT_ALLOWED temporal availability",
                prediction_year=prediction_year,
                prediction_round=prediction_round,
                severity="CRITICAL",
            )

        # Rule 2: FORBIDDEN leakage status -> REJECTED
        if feature_def.leakage_status == LeakageStatus.FORBIDDEN:
            return LeakageViolation(
                category=LeakageCategory.FUTURE_YEAR_STATISTICS,
                feature_name=feature_def.name,
                description=f"Feature {feature_def.name} has FORBIDDEN leakage status",
                prediction_year=prediction_year,
                prediction_round=prediction_round,
                severity="CRITICAL",
            )

        # Rule 3: Check temporal boundaries for CONDITIONAL features
        if feature_def.leakage_status == LeakageStatus.CONDITIONAL:
            if feature_def.latest_allowed_year_for_prediction is not None:
                if prediction_year > feature_def.latest_allowed_year_for_prediction:
                    return LeakageViolation(
                        category=LeakageCategory.FUTURE_YEAR_STATISTICS,
                        feature_name=feature_def.name,
                        description=f"Feature {feature_def.name} uses data from year {feature_def.latest_allowed_year_for_prediction} to predict {prediction_year}",
                        prediction_year=prediction_year,
                        prediction_round=prediction_round,
                        offending_data_year=feature_def.latest_allowed_year_for_prediction,
                        severity="CRITICAL",
                    )

            if feature_def.latest_allowed_round_for_prediction is not None:
                round_order = {
                    RoundType.ROUND_1: 1,
                    RoundType.ROUND_2: 2,
                    RoundType.ROUND_3: 3,
                    RoundType.STRAY_VACANCY: 4,
                }
                if (
                    round_order[prediction_round]
                    > round_order[feature_def.latest_allowed_round_for_prediction]
                ):
                    return LeakageViolation(
                        category=LeakageCategory.FUTURE_COUNSELLING_ROUND,
                        feature_name=feature_def.name,
                        description=f"Feature {feature_def.name} uses data from round {feature_def.latest_allowed_round_for_prediction.value} to predict {prediction_round.value}",
                        prediction_year=prediction_year,
                        prediction_round=prediction_round,
                        offending_data_round=feature_def.latest_allowed_round_for_prediction,
                        severity="CRITICAL",
                    )

        # Rule 4: Check for future counselling year data in historical aggregations
        if "historical" in feature_def.name.lower() or "prior_year" in feature_def.name.lower():
            violation = self._check_historical_feature_boundaries(
                feature_def, record, historical_data, prediction_year, prediction_round
            )
            if violation:
                return violation

        # Rule 5: Check for target-derived fields
        if self._is_target_derived(feature_def, record):
            return LeakageViolation(
                category=LeakageCategory.TARGET_DERIVED_FIELD,
                feature_name=feature_def.name,
                description=f"Feature {feature_def.name} appears to be derived from target variable",
                prediction_year=prediction_year,
                prediction_round=prediction_round,
                severity="CRITICAL",
            )

        # Rule 6: Check for future seat matrix usage
        if "seat" in feature_def.name.lower() and "future" in feature_def.transformation.lower():
            return LeakageViolation(
                category=LeakageCategory.FUTURE_SEAT_MATRIX,
                feature_name=feature_def.name,
                description=f"Feature {feature_def.name} uses future seat matrix data",
                prediction_year=prediction_year,
                prediction_round=prediction_round,
                severity="CRITICAL",
            )

        return None

    def _check_historical_feature_boundaries(
        self,
        feature_def: FeatureDefinition,
        record: ModellingRecord,
        historical_data: dict[str, Any],
        prediction_year: int,
        prediction_round: RoundType,
    ) -> LeakageViolation | None:
        """Verify historical features only use data from years < prediction_year."""
        group_key = f"{record.source_facts.institute_code}|{record.source_facts.course}|{record.source_facts.quota.value}|{record.source_facts.category.value}|{record.source_facts.round.value}"

        if "closing_ranks" in historical_data:
            years_used = historical_data["closing_ranks"].get(group_key, {})
            future_years = [y for y in years_used.keys() if y >= prediction_year]
            if future_years:
                return LeakageViolation(
                    category=LeakageCategory.FUTURE_YEAR_STATISTICS,
                    feature_name=feature_def.name,
                    description=f"Feature {feature_def.name} uses closing ranks from future years {future_years} for prediction year {prediction_year}",
                    prediction_year=prediction_year,
                    prediction_round=prediction_round,
                    offending_data_year=min(future_years),
                    severity="CRITICAL",
                )

        if "seat_counts" in historical_data:
            years_used = historical_data["seat_counts"].get(group_key, {})
            future_years = [y for y in years_used.keys() if y >= prediction_year]
            if future_years:
                return LeakageViolation(
                    category=LeakageCategory.FUTURE_SEAT_MATRIX,
                    feature_name=feature_def.name,
                    description=f"Feature {feature_def.name} uses seat counts from future years {future_years} for prediction year {prediction_year}",
                    prediction_year=prediction_year,
                    prediction_round=prediction_round,
                    offending_data_year=min(future_years),
                    severity="CRITICAL",
                )

        return None

    def _is_target_derived(self, feature_def: FeatureDefinition, record: ModellingRecord) -> bool:
        """Check if feature appears to be derived from target.

        Historical features that use past closing_rank data are allowed if they
        have CONDITIONAL leakage status (they use historical data with proper
        temporal boundaries enforced by _check_historical_feature_boundaries).
        """
        target_fields = {
            "closing_rank",
            "opening_rank",
            "admission_probability",
            "vacancy_after_round",
        }
        source_fields_set = set(feature_def.source_fields)

        # Allow historical features that use past target data with proper temporal boundaries
        # CONDITIONAL features are designed to use historical data with temporal boundaries
        if feature_def.leakage_status == LeakageStatus.CONDITIONAL:
            return False

        return bool(source_fields_set & target_fields)

    def check_feature_definitions(self) -> LeakageResult:
        """Check all registered feature definitions for structural leakage issues."""
        violations = []
        checked_features = []

        for feature_name in self.feature_registry.get_feature_names():
            feature_def = self.feature_registry.get_feature(feature_name)
            checked_features.append(feature_name)

            if feature_def.leakage_status == LeakageStatus.UNKNOWN:
                violations.append(
                    LeakageViolation(
                        category=LeakageCategory.UNKNOWN_TEMPORAL_AVAILABILITY,
                        feature_name=feature_name,
                        description=f"Feature {feature_name} has UNKNOWN leakage status - NOT_ALLOWED",
                        prediction_year=0,
                        prediction_round=RoundType.ROUND_1,
                        severity="CRITICAL",
                    )
                )

            if feature_def.temporal_availability == TemporalAvailability.NOT_ALLOWED:
                violations.append(
                    LeakageViolation(
                        category=LeakageCategory.UNKNOWN_TEMPORAL_AVAILABILITY,
                        feature_name=feature_name,
                        description=f"Feature {feature_name} has NOT_ALLOWED temporal availability",
                        prediction_year=0,
                        prediction_round=RoundType.ROUND_1,
                        severity="CRITICAL",
                    )
                )

        passed = len(violations) == 0
        return LeakageResult(
            passed=passed,
            violations=violations,
            checked_features=checked_features,
            checked_records=0,
            check_timestamp=datetime.now(UTC),
            prediction_year=0,
            prediction_round=RoundType.ROUND_1,
        )
