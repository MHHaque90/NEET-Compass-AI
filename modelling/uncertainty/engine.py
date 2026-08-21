"""
Uncertainty and Abstention Framework - Phase 11
Architecture for future uncertainty handling and abstention.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from modelling.contracts.dataset import (
    SourceFacts,
)
from modelling.splits.engine import TemporalValidationStatus


class ConfidenceLevel(str, Enum):
    """Confidence levels for predictions."""

    HIGH = "HIGH_CONFIDENCE"
    MEDIUM = "MEDIUM_CONFIDENCE"
    LOW = "LOW_CONFIDENCE"
    NONE = "INSUFFICIENT_EVIDENCE"


class AbstentionReason(str, Enum):
    """Reasons for abstention."""

    INSUFFICIENT_HISTORICAL_DATA = "insufficient_historical_data"
    NEW_COLLEGE = "new_college"
    NEW_CATEGORY_QUOTA_COMBO = "new_category_quota_combo"
    EXTRAPOLATION = "extrapolation"
    CALIBRATION_FAILURE = "calibration_failure"
    SEAT_MATRIX_CHANGE = "seat_matrix_change"
    POLICY_CHANGE = "policy_change"
    DATA_QUALITY_GATE_FAILURE = "data_quality_gate_failure"
    TEMPORAL_VALIDATION_BLOCKED = "temporal_validation_blocked"
    TARGET_NOT_READY = "target_not_ready"


@dataclass(frozen=True)
class UncertaintyEstimate:
    """Uncertainty estimate for a prediction."""

    prediction: float
    lower_bound: float | None = None
    upper_bound: float | None = None
    confidence_level: ConfidenceLevel = ConfidenceLevel.NONE
    abstention_reasons: list[AbstentionReason] = field(default_factory=list)
    evidence_score: float = 0.0
    stability_score: float = 0.0
    calibration_score: float = 0.0
    composite_score: float = 0.0

    def __post_init__(self):
        if self.lower_bound is not None and self.upper_bound is not None:
            if self.lower_bound > self.upper_bound:
                raise ValueError("lower_bound cannot be > upper_bound")
        if not 0.0 <= self.evidence_score <= 1.0:
            raise ValueError("evidence_score must be in [0,1]")
        if not 0.0 <= self.stability_score <= 1.0:
            raise ValueError("stability_score must be in [0,1]")
        if not 0.0 <= self.calibration_score <= 1.0:
            raise ValueError("calibration_score must be in [0,1]")
        if not 0.0 <= self.composite_score <= 1.0:
            raise ValueError("composite_score must be in [0,1]")


class UncertaintyEngine:
    """
    Uncertainty quantification and abstention engine.
    CRITICAL RULE: WHEN UNCERTAINTY IS TOO HIGH -> ABSTAIN.
    """

    def __init__(self, temporal_status: TemporalValidationStatus):
        self.temporal_status = temporal_status

    def estimate_uncertainty(
        self,
        prediction: float,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        calibration_error: float | None = None,
        validation_metrics: dict[str, Any] | None = None,
    ) -> UncertaintyEstimate:
        """
        Estimate uncertainty for a prediction.
        Returns INSUFFICIENT_EVIDENCE if temporal validation blocked.
        """
        # Hard abstention gate: temporal validation blocked
        if self.temporal_status != TemporalValidationStatus.READY:
            return UncertaintyEstimate(
                prediction=prediction,
                confidence_level=ConfidenceLevel.NONE,
                abstention_reasons=[AbstentionReason.TEMPORAL_VALIDATION_BLOCKED],
            )

        # Hard abstention gate: target not ready
        if validation_metrics and validation_metrics.get("target_readiness") != "READY":
            return UncertaintyEstimate(
                prediction=prediction,
                confidence_level=ConfidenceLevel.NONE,
                abstention_reasons=[AbstentionReason.TARGET_NOT_READY],
            )

        # Check abstention triggers
        abstention_reasons = self._check_abstention_triggers(
            source_facts, historical_data, calibration_error, prediction
        )

        if abstention_reasons:
            return UncertaintyEstimate(
                prediction=prediction,
                confidence_level=ConfidenceLevel.NONE,
                abstention_reasons=abstention_reasons,
            )

        # Compute evidence strength
        n_historical = self._count_prior_years(source_facts, historical_data)
        seat_stability = self._compute_seat_stability(source_facts, historical_data)
        calibration = calibration_error or 1.0

        evidence_score = min(n_historical / 5.0, 1.0)
        stability_score = 1.0 - min(seat_stability / 0.5, 1.0)
        calibration_score = 1.0 - min(calibration / 0.1, 1.0)

        composite = 0.4 * evidence_score + 0.3 * stability_score + 0.3 * calibration_score

        if composite >= 0.8:
            confidence = ConfidenceLevel.HIGH
        elif composite >= 0.5:
            confidence = ConfidenceLevel.MEDIUM
        elif composite >= 0.3:
            confidence = ConfidenceLevel.LOW
        else:
            confidence = ConfidenceLevel.NONE
            abstention_reasons.append(AbstentionReason.INSUFFICIENT_HISTORICAL_DATA)

        # Compute prediction interval if we have historical data
        lower, upper = self._compute_prediction_interval(source_facts, historical_data)

        return UncertaintyEstimate(
            prediction=prediction,
            lower_bound=lower,
            upper_bound=upper,
            confidence_level=confidence,
            abstention_reasons=abstention_reasons,
            evidence_score=evidence_score,
            stability_score=stability_score,
            calibration_score=calibration_score,
            composite_score=composite,
        )

    def _check_abstention_triggers(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
        calibration_error: float | None,
        prediction: float,
    ) -> list[AbstentionReason]:
        """Check all abstention triggers from uncertainty-abstention.md."""
        reasons = []

        # Trigger 1: Insufficient historical data (< 2 prior years)
        n_prior = self._count_prior_years(source_facts, historical_data)
        if n_prior < 2:
            reasons.append(AbstentionReason.INSUFFICIENT_HISTORICAL_DATA)

        # Trigger 2: New college (no historical records)
        key = self._get_group_key(source_facts)
        if key not in historical_data.get("closing_ranks", {}):
            reasons.append(AbstentionReason.NEW_COLLEGE)

        # Trigger 3: New category/quota combo (< 5 historical records)
        pool_key = (
            f"{source_facts.category.value}|{source_facts.quota.value}|{source_facts.round.value}"
        )
        pool_count = len(historical_data.get("pool_closing_ranks", {}).get(pool_key, {}))
        if pool_count < 5:
            reasons.append(AbstentionReason.NEW_CATEGORY_QUOTA_COMBO)

        # Trigger 4: Extrapolation (rank outside historical range)
        historical_ranks = historical_data.get("closing_ranks", {}).get(key, {}).values()
        if historical_ranks:
            min_rank = min(historical_ranks)
            max_rank = max(historical_ranks)
            # We'd need the student's rank to check this - using prediction as proxy
            if prediction < min_rank * 0.5 or prediction > max_rank * 2.0:
                reasons.append(AbstentionReason.EXTRAPOLATION)

        # Trigger 5: Calibration failure (ECE > 0.1)
        if calibration_error is not None and calibration_error > 0.1:
            reasons.append(AbstentionReason.CALIBRATION_FAILURE)

        # Trigger 6: Seat matrix change (> 20% change)
        if seat_stability := self._compute_seat_stability(source_facts, historical_data):
            if seat_stability > 0.2:
                reasons.append(AbstentionReason.SEAT_MATRIX_CHANGE)

        # Trigger 7: Policy change (known counselling rule change)
        # This would come from external knowledge base
        # For now, we don't have this data

        # Trigger 8: Data quality gate failure
        # Would be checked from quality gate results

        return reasons

    def _count_prior_years(self, source_facts: SourceFacts, historical_data: dict[str, Any]) -> int:
        """Count prior years with data for this group."""
        key = self._get_group_key(source_facts)
        prior_years = [
            y
            for y in historical_data.get("closing_ranks", {}).get(key, {})
            if y < source_facts.counselling_year
        ]
        return len(prior_years)

    def _compute_seat_stability(
        self, source_facts: SourceFacts, historical_data: dict[str, Any]
    ) -> float:
        """Compute seat count change percentage from prior year."""
        key = self._get_group_key(source_facts)
        prior_year = source_facts.counselling_year - 1
        prior_seats = historical_data.get("seat_counts", {}).get(key, {}).get(prior_year)
        if prior_seats and prior_seats > 0:
            return abs(source_facts.total_seats - prior_seats) / prior_seats
        return 1.0  # Unknown = assume maximum instability

    def _compute_prediction_interval(
        self,
        source_facts: SourceFacts,
        historical_data: dict[str, Any],
    ) -> tuple[float | None, float | None]:
        """Compute 90% prediction interval from historical data."""
        key = self._get_group_key(source_facts)
        prior_years = [
            y
            for y in historical_data.get("closing_ranks", {}).get(key, {})
            if y < source_facts.counselling_year
        ]

        if len(prior_years) >= 3:
            values = sorted([historical_data["closing_ranks"][key][y] for y in prior_years])
            n = len(values)
            lower_idx = int(0.05 * (n - 1))
            upper_idx = int(0.95 * (n - 1))
            return float(values[lower_idx]), float(values[upper_idx])

        return None, None

    def _get_group_key(self, source_facts: SourceFacts) -> str:
        return f"{source_facts.institute_code}|{source_facts.course}|{source_facts.quota.value}|{source_facts.category.value}|{source_facts.round.value}"

    def format_user_display(self, estimate: UncertaintyEstimate) -> dict[str, Any]:
        """Format uncertainty estimate for user display."""
        if estimate.confidence_level == ConfidenceLevel.HIGH:
            badge = "✅ Green badge"
            text = f"Predicted closing rank: {int(estimate.prediction):,}"
            if estimate.lower_bound and estimate.upper_bound:
                text += f" (90% PI: {int(estimate.lower_bound):,}–{int(estimate.upper_bound):,})"
        elif estimate.confidence_level == ConfidenceLevel.MEDIUM:
            badge = "⚠️ Yellow badge"
            text = f"Predicted closing rank: {int(estimate.prediction):,}"
            if estimate.lower_bound and estimate.upper_bound:
                text += f" (90% PI: {int(estimate.lower_bound):,}–{int(estimate.upper_bound):,}) — Moderate confidence"
        elif estimate.confidence_level == ConfidenceLevel.LOW:
            badge = "🟠 Orange badge"
            text = f"Predicted closing rank: {int(estimate.prediction):,}"
            if estimate.lower_bound and estimate.upper_bound:
                text += f" (90% PI: {int(estimate.lower_bound):,}–{int(estimate.upper_bound):,}) — Low confidence, interpret cautiously"
        else:
            badge = "❌ Red badge"
            text = (
                "Insufficient historical data for reliable prediction. Showing general trends only."
            )

        return {
            "badge": badge,
            "text": text,
            "confidence": estimate.confidence_level.value,
            "abstention_reasons": [r.value for r in estimate.abstention_reasons],
            "composite_score": estimate.composite_score,
        }
