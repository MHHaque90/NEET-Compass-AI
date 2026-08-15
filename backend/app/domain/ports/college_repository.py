"""Port for reading college master data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.entities.college import College
from app.domain.enums import Course, IndiaState


class CollegeRepository(ABC):
    """Read-side contract for the college master catalog."""

    @abstractmethod
    def get_by_code(self, code: str) -> College | None:
        """Fetch a single college by its stable code."""

    @abstractmethod
    def find(
        self,
        *,
        course: Course | None = None,
        states: Sequence[IndiaState] | None = None,
        max_annual_fee: int | None = None,
    ) -> Sequence[College]:
        """Return colleges matching the given filters (all filters optional)."""
