"""
Temporal Split Engine - Phase 6
Deterministic temporal dataset splitter with chronological boundaries.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from modelling.config.modelling_readiness import get_modelling_ready_years
from modelling.contracts.dataset import (
    AuthorityType,
    ModellingRecord,
)


class TemporalValidationStatus(str, Enum):
    """Status of temporal validation readiness."""

    READY = "READY"
    BLOCKED_INSUFFICIENT_YEARS = "TEMPORAL_VALIDATION_BLOCKED"
    BLOCKED_NO_TARGET = "TARGET_NOT_READY"
    BLOCKED_LEAKAGE = "LEAKAGE_CHECK_FAILED"
    BLOCKED_DATA_QUALITY = "DATA_QUALITY_GATES_FAILED"


@dataclass(frozen=True)
class SplitResult:
    """Result of temporal dataset splitting."""

    train_records: list[ModellingRecord]
    validation_records: list[ModellingRecord]
    test_records: list[ModellingRecord]
    train_years: list[int]
    validation_years: list[int]
    test_years: list[int]
    status: TemporalValidationStatus
    split_timestamp: datetime
    minimum_years_required: int
    available_years: list[int]
    blocking_reason: str | None = None

    def __post_init__(self):
        if self.status == TemporalValidationStatus.READY:
            if not self.train_records or not self.validation_records or not self.test_records:
                raise ValueError("READY split must have all three sets non-empty")
        else:
            if self.train_records or self.validation_records or self.test_records:
                raise ValueError("BLOCKED split must have empty record sets")


class TemporalSplitter:
    """
    Deterministic temporal dataset splitter.
    Uses chronological boundaries: TRAIN -> VALIDATION -> TEST
    FAILS CLOSED if insufficient verified years exist.
    """

    def __init__(
        self,
        minimum_years_required: int = 3,
        test_years_count: int = 1,
        validation_years_count: int = 1,
    ):
        self.minimum_years_required = minimum_years_required
        self.test_years_count = test_years_count
        self.validation_years_count = validation_years_count

    def split(
        self,
        records: list[ModellingRecord],
        modelling_ready_years: dict[AuthorityType, list[int]],
    ) -> SplitResult:
        """
        Split records into train/validation/test using chronological boundaries.
        Returns TEMPORAL_VALIDATION_BLOCKED if insufficient years.
        """
        # Get all verified modelling-ready years across authorities
        all_ready_years = set()
        for authority, years in modelling_ready_years.items():
            all_ready_years.update(years)

        available_years = sorted(all_ready_years)

        # Check if we have enough years
        if len(available_years) < self.minimum_years_required:
            return SplitResult(
                train_records=[],
                validation_records=[],
                test_records=[],
                train_years=[],
                validation_years=[],
                test_years=[],
                status=TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS,
                split_timestamp=datetime.now(UTC),
                minimum_years_required=self.minimum_years_required,
                available_years=available_years,
                blocking_reason=f"Only {len(available_years)} verified modelling-ready year(s) available: {available_years}. Need >= {self.minimum_years_required}.",
            )

        # Determine split boundaries
        # Train: oldest years, Validation: middle, Test: newest
        test_years = available_years[-self.test_years_count :]
        validation_years = available_years[
            -(self.test_years_count + self.validation_years_count) : -self.test_years_count
        ]
        train_years = available_years[: -(self.test_years_count + self.validation_years_count)]

        # Split records by year
        train_records = [r for r in records if r.source_facts.counselling_year in train_years]
        validation_records = [
            r for r in records if r.source_facts.counselling_year in validation_years
        ]
        test_records = [r for r in records if r.source_facts.counselling_year in test_years]

        return SplitResult(
            train_records=train_records,
            validation_records=validation_records,
            test_records=test_records,
            train_years=train_years,
            validation_years=validation_years,
            test_years=test_years,
            status=TemporalValidationStatus.READY,
            split_timestamp=datetime.now(UTC),
            minimum_years_required=self.minimum_years_required,
            available_years=available_years,
        )

    def split_by_authority(
        self,
        records: list[ModellingRecord],
        modelling_ready_years: dict[AuthorityType, list[int]],
    ) -> dict[AuthorityType, SplitResult]:
        """Split records per authority."""
        results = {}
        records_by_authority = {}
        for record in records:
            auth = record.source_facts.counselling_authority
            if auth not in records_by_authority:
                records_by_authority[auth] = []
            records_by_authority[auth].append(record)

        for authority, auth_records in records_by_authority.items():
            auth_ready_years = {authority: modelling_ready_years.get(authority, [])}
            results[authority] = self.split(auth_records, auth_ready_years)

        return results

    def get_current_status(
        self, modelling_ready_years: dict[AuthorityType, list[int]]
    ) -> TemporalValidationStatus:
        """Get current temporal validation status without splitting."""
        all_ready_years = set()
        for years in modelling_ready_years.values():
            all_ready_years.update(years)

        if len(all_ready_years) < self.minimum_years_required:
            return TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS

        return TemporalValidationStatus.READY


def get_current_temporal_status() -> TemporalValidationStatus:
    """Get current temporal validation status from config."""
    ready_years = get_modelling_ready_years()
    splitter = TemporalSplitter()
    return splitter.get_current_status(ready_years)
