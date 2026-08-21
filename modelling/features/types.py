"""
Feature Types - Shared types for feature engineering to avoid circular imports.
"""

from dataclasses import dataclass
from enum import Enum


class TemporalAvailability(str, Enum):
    """When a feature becomes available for prediction."""

    ALWAYS_AVAILABLE = "always_available"
    AFTER_ROUND_1 = "after_round_1"
    AFTER_ROUND_2 = "after_round_2"
    AFTER_ROUND_3 = "after_round_3"
    AFTER_COUNSELLING_YEAR = "after_counselling_year"
    NOT_ALLOWED = "not_allowed"


class LeakageStatus(str, Enum):
    """Leakage classification for a feature."""

    SAFE = "safe"
    CONDITIONAL = "conditional"
    FORBIDDEN = "forbidden"
    UNKNOWN = "unknown"


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
    provenance: object | None  # FeatureProvenance - avoid circular import
    leakage_status: LeakageStatus
    latest_allowed_year_for_prediction: int | None = None
    latest_allowed_round_for_prediction: object | None = None  # RoundType

    def __post_init__(self):
        if not self.name:
            raise ValueError("Feature name is required")
        if self.leakage_status == LeakageStatus.UNKNOWN:
            raise ValueError(f"Feature {self.name}: UNKNOWN leakage status is NOT_ALLOWED")
