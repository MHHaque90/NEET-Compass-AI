"""Port for reading historical allotment (cut-off) data.

Defined in terms of the *query intents* the application needs, not in terms
of SQL or ORM objects. Implementations are free to back this by PostgreSQL,
a columnar store, or a denormalized analytics table.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.entities.allotment import AllotmentRecord
from app.domain.enums import Category, Course, Gender, PwdStatus, QuotaType


class AllotmentRepository(ABC):
    """Read-side contract for historical counselling data."""

    @abstractmethod
    def history_for(
        self,
        college_id: uuid.UUID,
        *,
        quota_type: QuotaType,
        category: Category,
        gender: Gender,
        pw_d: PwdStatus,
        course: Course,
        years: Sequence[int] | None = None,
    ) -> Sequence[AllotmentRecord]:
        """Return allotment rows matching the exact quota bucket of a candidate.

        ``years`` filters to recent years when provided; ``None`` means all
        available history.
        """

    @abstractmethod
    def closing_rank_for(
        self,
        college_id: uuid.UUID,
        *,
        quota_type: QuotaType,
        category: Category,
        gender: Gender,
        pw_d: PwdStatus,
        year: int,
        round_number: int,
    ) -> int | None:
        """Return the closing AIR for a specific college/round/cohort.

        ``None`` when no allotment exists for that combination (e.g. the
        college did not open seats for a reserved category that year).
        """
