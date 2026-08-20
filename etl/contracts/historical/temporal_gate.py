"""Temporal Readiness Gate — Sprint 3.9.

Creates a final deterministic temporal readiness calculation.

Answers:
- How many verified modelling-ready years exist?
- Which years exist?
- Are there gaps?
- Are years chronologically ordered?
- Can a train/validation/test temporal split exist?
- Is the minimum required historical coverage satisfied?

Current expected result: 1 verified year -> TEMPORAL VALIDATION = BLOCKED
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Minimum verified years required for temporal validation
MINIMUM_VERIFIED_YEARS: int = 3
PREFERRED_VERIFIED_YEARS: int = 4


@dataclass(frozen=True)
class TemporalReadinessResult:
    """Result of temporal readiness validation."""

    passed: bool
    verified_years: tuple[int, ...]
    verified_count: int
    minimum_required: int
    has_gaps: bool
    gap_years: tuple[int, ...]
    chronologically_ordered: bool
    can_split_train_val_test: bool
    details: dict[str, Any]

    def __bool__(self) -> bool:
        return self.passed


class TemporalReadinessGate:
    """Validates temporal readiness for modelling."""

    def __init__(
        self,
        minimum_years: int = MINIMUM_VERIFIED_YEARS,
        preferred_years: int = PREFERRED_VERIFIED_YEARS,
    ):
        self.minimum_years = minimum_years
        self.preferred_years = preferred_years

    def validate(
        self,
        modelling_ready_years: dict[str, list[int]],
    ) -> TemporalReadinessResult:
        """Validate temporal readiness across all authorities.

        Args:
            modelling_ready_years: Dict of authority -> list of verified modelling-ready years.

        Returns:
            TemporalReadinessResult.

        """
        # Collect all verified years across authorities
        all_years = set()
        for years in modelling_ready_years.values():
            all_years.update(years)

        verified_years = tuple(sorted(all_years))
        verified_count = len(verified_years)

        # Check for gaps
        gap_years: list[int] = []
        if verified_years:
            full_range = range(min(verified_years), max(verified_years) + 1)
            gap_years = [y for y in full_range if y not in verified_years]

        has_gaps = len(gap_years) > 0
        chronologically_ordered = list(verified_years) == sorted(verified_years)
        can_split = verified_count >= self.minimum_years

        passed = can_split and chronologically_ordered

        details = {
            "verified_years_per_authority": modelling_ready_years,
            "total_verified_years": verified_count,
            "minimum_required": self.minimum_years,
            "preferred_years": self.preferred_years,
            "gap_years": list(gap_years),
            "can_forward_chain": can_split,
            "temporal_validation_status": "BLOCKED" if not passed else "READY",
        }

        return TemporalReadinessResult(
            passed=passed,
            verified_years=verified_years,
            verified_count=verified_count,
            minimum_required=self.minimum_years,
            has_gaps=has_gaps,
            gap_years=tuple(gap_years),
            chronologically_ordered=chronologically_ordered,
            can_split_train_val_test=can_split,
            details=details,
        )


def compute_temporal_readiness(
    modelling_ready_years: dict[str, list[int]],
    minimum_years: int = MINIMUM_VERIFIED_YEARS,
) -> TemporalReadinessResult:
    """Convenience function to compute temporal readiness."""
    gate = TemporalReadinessGate(minimum_years=minimum_years)
    return gate.validate(modelling_ready_years)
