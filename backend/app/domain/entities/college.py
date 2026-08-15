"""A college — the supply side of the admission market.

Carries only intrinsic attributes of the institution. Competitive dynamics
(how hard it is to get in) live in the historical ``AllotmentRecord`` data,
never hard-coded here.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from app.domain.enums import CollegeOwnership, Course, IndiaState


class College(BaseModel):
    model_config = {"frozen": True}

    id: uuid.UUID | None = Field(default=None, description="Persisted id, None when unsaved")
    code: str = Field(
        min_length=1, max_length=20, description="Stable institution code (e.g. NMC code)"
    )
    name: str = Field(min_length=1, max_length=255)
    state: IndiaState
    city: str = Field(min_length=1, max_length=100)
    course: Course
    ownership: CollegeOwnership
    annual_fee_inr: int = Field(ge=0, description="Tuition + hostel per academic year")
    total_seats: int = Field(ge=0, description="Total sanctioned seats for the course")
    aiq_seats: int = Field(ge=0, description="Seats allocated to All India Quota")

    @property
    def state_quota_seats(self) -> int:
        return self.total_seats - self.aiq_seats

    def is_within_budget(self, budget: int | None) -> bool:
        if budget is None:
            return True
        return self.annual_fee_inr <= budget
