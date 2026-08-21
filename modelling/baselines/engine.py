"""
Baseline Framework - Phase 9
Non-ML baselines that any future ML model MUST beat.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from modelling.contracts.dataset import (
    SourceFacts,
)
from modelling.splits.engine import TemporalValidationStatus


class BaselineStatus(str, Enum):
    """Status of baseline evaluation."""

    COMPUTED = "COMPUTED"
    BLOCKED_INSUFFICIENT_DATA = "BASELINE_EVALUATION_BLOCKED"
    ABSTAINED = "ABSTAINED"


@dataclass(frozen=True)
class BaselineResult:
    """Result of a baseline prediction."""

    baseline_name: str
    predictions: dict[str, float]  # record_id -> predicted value
    mae: float | None = None
    rmse: float | None = None
    median_ae: float | None = None
    coverage: float | None = None
    status: BaselineStatus = BaselineStatus.COMPUTED
    abstention_reason: str | None = None
    records_evaluated: int = 0
    records_abstained: int = 0


class BaselineEngine:
    """
    Baseline evaluation engine.
    Implements the non-ML baselines from baseline-strategy.md.
    Returns BASELINE_EVALUATION_BLOCKED when temporal requirements not satisfied.
    """

    def __init__(self, temporal_status: TemporalValidationStatus):
        self.temporal_status = temporal_status

    def evaluate_all_baselines(
        self,
        train_records: list[SourceFacts],
        test_records: list[SourceFacts],
        historical_data: dict[str, Any],
    ) -> dict[str, BaselineResult]:
        """
        Evaluate all baselines against test data.
        Returns BASELINE_EVALUATION_BLOCKED if temporal validation is blocked.
        """
        if self.temporal_status != TemporalValidationStatus.READY:
            return {
                "previous_year": BaselineResult(
                    baseline_name="previous_year",
                    predictions={},
                    status=BaselineStatus.BLOCKED_INSUFFICIENT_DATA,
                    abstention_reason="Temporal validation blocked: insufficient verified years",
                ),
                "multiyear_median": BaselineResult(
                    baseline_name="multiyear_median",
                    predictions={},
                    status=BaselineStatus.BLOCKED_INSUFFICIENT_DATA,
                    abstention_reason="Temporal validation blocked: insufficient verified years",
                ),
                "seat_ratio": BaselineResult(
                    baseline_name="seat_ratio",
                    predictions={},
                    status=BaselineStatus.BLOCKED_INSUFFICIENT_DATA,
                    abstention_reason="Temporal validation blocked: insufficient verified years",
                ),
                "pool_level": BaselineResult(
                    baseline_name="pool_level",
                    predictions={},
                    status=BaselineStatus.BLOCKED_INSUFFICIENT_DATA,
                    abstention_reason="Temporal validation blocked: insufficient verified years",
                ),
            }

        return {
            "previous_year": self._baseline_previous_year(
                train_records, test_records, historical_data
            ),
            "multiyear_median": self._baseline_multiyear_median(
                train_records, test_records, historical_data
            ),
            "seat_ratio": self._baseline_seat_ratio(train_records, test_records, historical_data),
            "pool_level": self._baseline_pool_level(train_records, test_records, historical_data),
        }

    def _baseline_previous_year(
        self,
        train_records: list[SourceFacts],
        test_records: list[SourceFacts],
        historical_data: dict[str, Any],
    ) -> BaselineResult:
        """
        Baseline 1: Previous Comparable Historical Outcome
        Use actual outcome from year Y-1 for same group.
        """
        predictions = {}
        errors = []
        abstained = 0

        for record in test_records:
            key = self._get_group_key(record)
            prior_year = record.counselling_year - 1

            if prior_year in historical_data.get("closing_ranks", {}).get(key, {}):
                pred = historical_data["closing_ranks"][key][prior_year]
                predictions[key] = pred
                if record.closing_rank is not None:
                    errors.append(abs(pred - record.closing_rank))
            else:
                predictions[key] = None
                abstained += 1

        return BaselineResult(
            baseline_name="previous_year",
            predictions=predictions,
            mae=sum(errors) / len(errors) if errors else None,
            rmse=(sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else None,
            median_ae=sorted(errors)[len(errors) // 2] if errors else None,
            status=BaselineStatus.COMPUTED if errors else BaselineStatus.ABSTAINED,
            records_evaluated=len(errors),
            records_abstained=abstained,
        )

    def _baseline_multiyear_median(
        self,
        train_records: list[SourceFacts],
        test_records: list[SourceFacts],
        historical_data: dict[str, Any],
    ) -> BaselineResult:
        """
        Baseline 2: Multi-Year Median / Quantile
        Use median of available prior years for same group.
        """
        predictions = {}
        errors = []
        abstained = 0

        for record in test_records:
            key = self._get_group_key(record)
            prior_years = [
                y
                for y in historical_data.get("closing_ranks", {}).get(key, {})
                if y < record.counselling_year
            ]

            if len(prior_years) >= 2:
                values = [historical_data["closing_ranks"][key][y] for y in prior_years]
                pred = sorted(values)[len(values) // 2]
                predictions[key] = pred
                if record.closing_rank is not None:
                    errors.append(abs(pred - record.closing_rank))
            else:
                predictions[key] = None
                abstained += 1

        return BaselineResult(
            baseline_name="multiyear_median",
            predictions=predictions,
            mae=sum(errors) / len(errors) if errors else None,
            rmse=(sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else None,
            median_ae=sorted(errors)[len(errors) // 2] if errors else None,
            status=BaselineStatus.COMPUTED if errors else BaselineStatus.ABSTAINED,
            records_evaluated=len(errors),
            records_abstained=abstained,
        )

    def _baseline_seat_ratio(
        self,
        train_records: list[SourceFacts],
        test_records: list[SourceFacts],
        historical_data: dict[str, Any],
    ) -> BaselineResult:
        """
        Baseline 3: Simple Statistical / Seat Ratio Approach
        Use seat matrix + rank-to-seat ratio heuristics.
        """
        predictions = {}
        errors = []
        abstained = 0

        for record in test_records:
            key = self._get_group_key(record)
            seats = record.total_seats

            prior_closings = historical_data.get("closing_ranks", {}).get(key, {})
            prior_years = [y for y in prior_closings if y < record.counselling_year]

            if prior_years and seats > 0:
                ratios = []
                for y in prior_years:
                    prior_seats = historical_data.get("seat_counts", {}).get(key, {}).get(y)
                    prior_rank = prior_closings[y]
                    if prior_seats and prior_seats > 0 and prior_rank:
                        ratios.append(prior_rank / prior_seats)

                if ratios:
                    median_ratio = sorted(ratios)[len(ratios) // 2]
                    pred = int(median_ratio * seats)
                    predictions[key] = pred
                    if record.closing_rank is not None:
                        errors.append(abs(pred - record.closing_rank))
                else:
                    predictions[key] = None
                    abstained += 1
            else:
                predictions[key] = None
                abstained += 1

        return BaselineResult(
            baseline_name="seat_ratio",
            predictions=predictions,
            mae=sum(errors) / len(errors) if errors else None,
            rmse=(sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else None,
            median_ae=sorted(errors)[len(errors) // 2] if errors else None,
            status=BaselineStatus.COMPUTED if errors else BaselineStatus.ABSTAINED,
            records_evaluated=len(errors),
            records_abstained=abstained,
        )

    def _baseline_pool_level(
        self,
        train_records: list[SourceFacts],
        test_records: list[SourceFacts],
        historical_data: dict[str, Any],
    ) -> BaselineResult:
        """
        Baseline 4: Category/Quota Pool Aggregation (Fallback)
        Aggregate to category/quota/round level when college-level history insufficient.
        """
        predictions = {}
        errors = []
        abstained = 0

        for record in test_records:
            pool_key = f"{record.category.value}|{record.quota.value}|{record.round.value}"
            prior_years = [
                y
                for y in historical_data.get("pool_closing_ranks", {}).get(pool_key, {})
                if y < record.counselling_year
            ]

            if len(prior_years) >= 5:
                values = [historical_data["pool_closing_ranks"][pool_key][y] for y in prior_years]
                pred = sorted(values)[len(values) // 2]
                predictions[pool_key] = pred
                if record.closing_rank is not None:
                    errors.append(abs(pred - record.closing_rank))
            else:
                predictions[pool_key] = None
                abstained += 1

        return BaselineResult(
            baseline_name="pool_level",
            predictions=predictions,
            mae=sum(errors) / len(errors) if errors else None,
            rmse=(sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else None,
            median_ae=sorted(errors)[len(errors) // 2] if errors else None,
            status=BaselineStatus.COMPUTED if errors else BaselineStatus.ABSTAINED,
            records_evaluated=len(errors),
            records_abstained=abstained,
        )

    def _get_group_key(self, record: SourceFacts) -> str:
        return f"{record.institute_code}|{record.course}|{record.quota.value}|{record.category.value}|{record.round.value}"
