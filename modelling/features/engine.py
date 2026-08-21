"""
Feature Engineering Architecture - Phase 3
Deterministic feature-engineering layer with full provenance and versioning.
"""

import hashlib
from dataclasses import dataclass
from typing import Any

from modelling.contracts.dataset import (
    DerivedFeatures,
    QuotaType,
    RoundType,
    SourceFacts,
)
from modelling.contracts.versioning import FeatureVersion
from modelling.features.provenance import FeatureProvenance
from modelling.features.registry import FeatureRegistry
from modelling.features.types import FeatureDefinition, LeakageStatus, TemporalAvailability


@dataclass(frozen=True)
class FeatureDefinition:
    """
    Complete feature definition with all metadata required for reproducibility.
    """

    name: str
    definition: str
    source_fields: list[str]
    transformation: str
    temporal_availability: TemporalAvailability
    version: str
    provenance: FeatureProvenance
    leakage_status: LeakageStatus
    latest_allowed_year_for_prediction: int | None = None
    latest_allowed_round_for_prediction: RoundType | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Feature name is required")
        if self.leakage_status == LeakageStatus.UNKNOWN:
            raise ValueError(f"Feature {self.name}: UNKNOWN leakage status is NOT_ALLOWED")


@dataclass
class FeatureEngine:
    """
    Deterministic feature-engineering layer.
    Features derived ONLY from information legally available at prediction time.
    """

    registry: FeatureRegistry
    feature_version: str = "features_v1"
    transformation_version: str = "modelling_dataset_v1"

    def __post_init__(self):
        if not self.registry:
            raise ValueError("FeatureRegistry is required")

    def compute_features(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
        prediction_round: RoundType,
    ) -> DerivedFeatures:
        """
        Compute all features for a modelling record.
        Enforces temporal boundaries - only uses data from years < prediction_year
        and rounds < prediction_round within prediction_year.
        """
        feature_values = {}

        for feature_name in self.registry.get_feature_names():
            feature_def = self.registry.get_feature(feature_name)

            if not self._is_temporally_allowed(feature_def, prediction_year, prediction_round):
                feature_values[feature_name] = None
                continue

            try:
                value = self._compute_feature(
                    feature_def, source_facts, historical_data, prediction_year, prediction_round
                )
                feature_values[feature_name] = value
            except Exception:
                feature_values[feature_name] = None

        return DerivedFeatures(
            round_number=self._round_to_number(source_facts.round),
            is_first_round=source_facts.round == RoundType.ROUND_1,
            category_quota_combo=f"{source_facts.category.value}_{source_facts.quota.value}",
            institute_type=source_facts.institute_type
            if hasattr(source_facts, "institute_type")
            else "unknown",
            state_quota_indicator=source_facts.quota
            in [
                QuotaType.STATE_QUOTA,
                QuotaType.MANAGEMENT,
                QuotaType.DEEMED_UNIVERSITY,
                QuotaType.ALL_INDIA_MINORITY,
            ],
            year_index=prediction_year - min(historical_data.get("years", [prediction_year])),
            seat_count_log=self._safe_log(source_facts.total_seats + 1),
            historical_closing_rank_median=feature_values.get("historical_closing_rank_median"),
            historical_closing_rank_p10=feature_values.get("historical_closing_rank_p10"),
            historical_closing_rank_p90=feature_values.get("historical_closing_rank_p90"),
            seat_availability_ratio=feature_values.get("seat_availability_ratio"),
            prior_year_closing_rank=feature_values.get("prior_year_closing_rank"),
            prior_year_seat_count=feature_values.get("prior_year_seat_count"),
            seat_count_change_pct=feature_values.get("seat_count_change_pct"),
            feature_version=self.feature_version,
        )

    def _is_temporally_allowed(
        self,
        feature_def: FeatureDefinition,
        prediction_year: int,
        prediction_round: RoundType,
    ) -> bool:
        """Check if feature is allowed at prediction time."""
        if feature_def.leakage_status == LeakageStatus.FORBIDDEN:
            return False
        if feature_def.leakage_status == LeakageStatus.UNKNOWN:
            return False

        if feature_def.latest_allowed_year_for_prediction is not None:
            if prediction_year > feature_def.latest_allowed_year_for_prediction:
                return False

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
                return False

        return True

    def _compute_feature(
        self,
        feature_def: FeatureDefinition,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
        prediction_round: RoundType,
    ) -> Any:
        """Compute a single feature value."""
        if feature_def.name == "historical_closing_rank_median":
            return self._compute_historical_median(source_facts, historical_data, prediction_year)
        elif feature_def.name == "historical_closing_rank_p10":
            return self._compute_historical_quantile(
                source_facts, historical_data, prediction_year, 0.1
            )
        elif feature_def.name == "historical_closing_rank_p90":
            return self._compute_historical_quantile(
                source_facts, historical_data, prediction_year, 0.9
            )
        elif feature_def.name == "seat_availability_ratio":
            return self._compute_seat_availability_ratio(
                source_facts, historical_data, prediction_year
            )
        elif feature_def.name == "prior_year_closing_rank":
            return self._compute_prior_year_closing_rank(
                source_facts, historical_data, prediction_year
            )
        elif feature_def.name == "prior_year_seat_count":
            return self._compute_prior_year_seat_count(
                source_facts, historical_data, prediction_year
            )
        elif feature_def.name == "seat_count_change_pct":
            return self._compute_seat_count_change_pct(
                source_facts, historical_data, prediction_year
            )
        return None

    def _compute_historical_median(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
    ) -> float | None:
        """Compute median closing rank from prior years only."""
        key = self._get_group_key(source_facts)
        prior_years = [
            y for y in historical_data.get("closing_ranks", {}).get(key, {}) if y < prediction_year
        ]
        if len(prior_years) < 2:
            return None
        values = [historical_data["closing_ranks"][key][y] for y in prior_years]
        return float(sorted(values)[len(values) // 2])

    def _compute_historical_quantile(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
        quantile: float,
    ) -> float | None:
        """Compute quantile of closing rank from prior years only."""
        key = self._get_group_key(source_facts)
        prior_years = [
            y for y in historical_data.get("closing_ranks", {}).get(key, {}) if y < prediction_year
        ]
        if len(prior_years) < 2:
            return None
        values = sorted([historical_data["closing_ranks"][key][y] for y in prior_years])
        idx = int(quantile * (len(values) - 1))
        return float(values[idx])

    def _compute_seat_availability_ratio(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
    ) -> float | None:
        """Compute seat availability ratio (seats/applicants) - applicants unknown at prediction time."""
        return None

    def _compute_prior_year_closing_rank(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
    ) -> int | None:
        """Get prior year closing rank for same group."""
        key = self._get_group_key(source_facts)
        prior_year = prediction_year - 1
        return historical_data.get("closing_ranks", {}).get(key, {}).get(prior_year)

    def _compute_prior_year_seat_count(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
    ) -> int | None:
        """Get prior year seat count for same group."""
        key = self._get_group_key(source_facts)
        prior_year = prediction_year - 1
        return historical_data.get("seat_counts", {}).get(key, {}).get(prior_year)

    def _compute_seat_count_change_pct(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        prediction_year: int,
    ) -> float | None:
        """Compute seat count change percentage from prior year."""
        prior_seats = self._compute_prior_year_seat_count(
            source_facts, historical_data, prediction_year
        )
        if prior_seats is None or prior_seats == 0:
            return None
        return ((source_facts.total_seats - prior_seats) / prior_seats) * 100

    def _get_group_key(self, source_facts: SourceFacts) -> str:
        return f"{source_facts.institute_code}|{source_facts.course}|{source_facts.quota.value}|{source_facts.category.value}|{source_facts.round.value}"

    def _round_to_number(self, round_type: RoundType) -> int:
        return {"round_1": 1, "round_2": 2, "round_3": 3, "stray_vacancy": 4}[round_type.value]

    def _safe_log(self, x: float) -> float:
        import math

        return math.log(max(x, 1.0))

    def get_feature_version_metadata(self) -> FeatureVersion:
        """Get feature version metadata for reproducibility."""
        feature_defs = {}
        for name in self.registry.get_feature_names():
            fdef = self.registry.get_feature(name)
            feature_defs[name] = {
                "definition": fdef.definition,
                "source_fields": fdef.source_fields,
                "transformation": fdef.transformation,
                "temporal_availability": fdef.temporal_availability.value,
                "leakage_status": fdef.leakage_status.value,
                "latest_allowed_year": fdef.latest_allowed_year_for_prediction,
                "latest_allowed_round": fdef.latest_allowed_round_for_prediction.value
                if fdef.latest_allowed_round_for_prediction
                else None,
            }

        code_hash = hashlib.sha256(str(feature_defs).encode()).hexdigest()[:16]
        return FeatureVersion.create(
            version=self.feature_version,
            feature_definitions=feature_defs,
            feature_computation_code_hash=code_hash,
        )
