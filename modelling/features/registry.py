"""
Feature Registry - Phase 3 & 8
Central registry of all feature definitions with versioning.
"""

from dataclasses import dataclass, field

from modelling.contracts.dataset import RoundType
from modelling.features.types import FeatureDefinition, LeakageStatus, TemporalAvailability


@dataclass
class FeatureRegistry:
    """
    Registry of all feature definitions.
    Every feature must be registered with complete metadata.
    """

    features: dict[str, FeatureDefinition] = field(default_factory=dict)
    version: str = "features_v1"

    def register(self, feature: FeatureDefinition) -> None:
        """Register a feature definition."""
        if feature.name in self.features:
            raise ValueError(f"Feature already registered: {feature.name}")
        if feature.leakage_status == LeakageStatus.UNKNOWN:
            raise ValueError(f"Feature {feature.name}: UNKNOWN leakage status is NOT_ALLOWED")
        self.features[feature.name] = feature

    def get_feature(self, name: str) -> FeatureDefinition:
        """Get a feature definition by name."""
        if name not in self.features:
            raise KeyError(f"Feature not found: {name}")
        return self.features[name]

    def get_feature_names(self) -> list[str]:
        """Get all registered feature names."""
        return list(self.features.keys())

    def get_features_by_leakage_status(self, status: LeakageStatus) -> list[FeatureDefinition]:
        """Get all features with a specific leakage status."""
        return [f for f in self.features.values() if f.leakage_status == status]

    def validate_all_temporal_availability(
        self, prediction_year: int, prediction_round: RoundType
    ) -> dict[str, bool]:
        """Validate temporal availability for all features at prediction time."""
        results = {}
        for name, feature in self.features.items():
            allowed = True
            if feature.latest_allowed_year_for_prediction is not None:
                if prediction_year > feature.latest_allowed_year_for_prediction:
                    allowed = False
            if feature.latest_allowed_round_for_prediction is not None:
                round_order = {
                    RoundType.ROUND_1: 1,
                    RoundType.ROUND_2: 2,
                    RoundType.ROUND_3: 3,
                    RoundType.STRAY_VACANCY: 4,
                }
                if (
                    round_order[prediction_round]
                    > round_order[feature.latest_allowed_round_for_prediction]
                ):
                    allowed = False
            results[name] = allowed
        return results

    def create_default_registry() -> "FeatureRegistry":
        """Create the default feature registry with all defined features."""
        registry = FeatureRegistry()

        # Core categorical features (always available)
        registry.register(
            FeatureDefinition(
                name="round_number",
                definition="Ordinal round number: 1, 2, 3, 4 (stray)",
                source_fields=["round"],
                transformation="Mapping: round_1->1, round_2->2, round_3->3, stray_vacancy->4",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        registry.register(
            FeatureDefinition(
                name="is_first_round",
                definition="Boolean: true if predicting for round_1",
                source_fields=["round"],
                transformation="round == round_1",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        registry.register(
            FeatureDefinition(
                name="category_quota_combo",
                definition="Concatenation of category and quota",
                source_fields=["category", "quota"],
                transformation="category + '_' + quota",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        registry.register(
            FeatureDefinition(
                name="institute_type",
                definition="Institute type from seat matrix: govt/private/deemed/central",
                source_fields=["institute_type"],
                transformation="Direct from seat matrix",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        registry.register(
            FeatureDefinition(
                name="state_quota_indicator",
                definition="Boolean: true if quota is state-level (so, mm, du, am)",
                source_fields=["quota"],
                transformation="quota in {so, mm, du, am}",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        registry.register(
            FeatureDefinition(
                name="year_index",
                definition="Years since minimum year in dataset",
                source_fields=["counselling_year"],
                transformation="counselling_year - min_year_in_dataset",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        registry.register(
            FeatureDefinition(
                name="seat_count_log",
                definition="Log of total seats + 1",
                source_fields=["total_seats"],
                transformation="log(total_seats + 1)",
                temporal_availability=TemporalAvailability.ALWAYS_AVAILABLE,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.SAFE,
            )
        )

        # Historical features (require prior years, temporal boundary enforced)
        registry.register(
            FeatureDefinition(
                name="historical_closing_rank_median",
                definition="Median closing rank for same college/course/quota/category/round over prior years",
                source_fields=[
                    "closing_rank",
                    "counselling_year",
                    "institute_code",
                    "course",
                    "quota",
                    "category",
                    "round",
                ],
                transformation="median(closing_rank) for years < prediction_year",
                temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.CONDITIONAL,
                latest_allowed_year_for_prediction=None,  # Uses expanding window
                latest_allowed_round_for_prediction=None,
            )
        )

        registry.register(
            FeatureDefinition(
                name="historical_closing_rank_p10",
                definition="10th percentile closing rank over prior years",
                source_fields=[
                    "closing_rank",
                    "counselling_year",
                    "institute_code",
                    "course",
                    "quota",
                    "category",
                    "round",
                ],
                transformation="quantile(closing_rank, 0.1) for years < prediction_year",
                temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.CONDITIONAL,
                latest_allowed_year_for_prediction=None,
                latest_allowed_round_for_prediction=None,
            )
        )

        registry.register(
            FeatureDefinition(
                name="historical_closing_rank_p90",
                definition="90th percentile closing rank over prior years",
                source_fields=[
                    "closing_rank",
                    "counselling_year",
                    "institute_code",
                    "course",
                    "quota",
                    "category",
                    "round",
                ],
                transformation="quantile(closing_rank, 0.9) for years < prediction_year",
                temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.CONDITIONAL,
                latest_allowed_year_for_prediction=None,
                latest_allowed_round_for_prediction=None,
            )
        )

        registry.register(
            FeatureDefinition(
                name="prior_year_closing_rank",
                definition="Closing rank from immediately prior year for same group",
                source_fields=[
                    "closing_rank",
                    "counselling_year",
                    "institute_code",
                    "course",
                    "quota",
                    "category",
                    "round",
                ],
                transformation="closing_rank at year = prediction_year - 1",
                temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.CONDITIONAL,
                latest_allowed_year_for_prediction=None,
                latest_allowed_round_for_prediction=None,
            )
        )

        registry.register(
            FeatureDefinition(
                name="prior_year_seat_count",
                definition="Total seats from immediately prior year for same group",
                source_fields=[
                    "total_seats",
                    "counselling_year",
                    "institute_code",
                    "course",
                    "quota",
                    "category",
                ],
                transformation="total_seats at year = prediction_year - 1",
                temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.CONDITIONAL,
                latest_allowed_year_for_prediction=None,
                latest_allowed_round_for_prediction=None,
            )
        )

        registry.register(
            FeatureDefinition(
                name="seat_count_change_pct",
                definition="Percentage change in seat count from prior year",
                source_fields=[
                    "total_seats",
                    "counselling_year",
                    "institute_code",
                    "course",
                    "quota",
                    "category",
                ],
                transformation="(total_seats - prior_year_seats) / prior_year_seats * 100",
                temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.CONDITIONAL,
                latest_allowed_year_for_prediction=None,
                latest_allowed_round_for_prediction=None,
            )
        )

        # Seat availability - NOT available at prediction time (applicants unknown)
        registry.register(
            FeatureDefinition(
                name="seat_availability_ratio",
                definition="Total seats divided by applicant count",
                source_fields=["total_seats"],
                transformation="NOT_COMPUTABLE_AT_PREDICTION_TIME",
                temporal_availability=TemporalAvailability.NOT_ALLOWED,
                version="features_v1",
                provenance=None,
                leakage_status=LeakageStatus.FORBIDDEN,
                latest_allowed_year_for_prediction=None,
                latest_allowed_round_for_prediction=None,
            )
        )

        return registry
