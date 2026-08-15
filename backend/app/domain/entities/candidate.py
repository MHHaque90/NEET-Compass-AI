"""The candidate — everything we know about a NEET applicant.

This is the canonical input contract of the whole platform. Every future
entry point (REST, ML model feature vector, ETL import) must produce a
``CandidateProfile`` before anything else can happen, which keeps the
domain isolated from transport concerns.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import (
    Category,
    Gender,
    IndiaState,
    MinorityStatus,
    PwdStatus,
    QuotaType,
)

NEET_MAX_MARKS = 720


class CandidateProfile(BaseModel):
    """Validated, self-describing candidate input.

    ``BaseModel`` (Pydantic) is used instead of a plain dataclass so that
    validation happens at the boundary where untrusted input arrives; the
    object is immutable from that point on.
    """

    model_config = {"frozen": True}

    air: int = Field(ge=1, description="All-India Rank (1 = best)")
    marks: int = Field(ge=0, le=NEET_MAX_MARKS, description="NEET marks out of 720")
    category: Category
    domicile_state: IndiaState
    gender: Gender
    pw_d: PwdStatus = PwdStatus.NONE
    minority: MinorityStatus = MinorityStatus.NONE
    quota_type: QuotaType = QuotaType.AIQ
    budget: int | None = Field(
        default=None, ge=0, description="Annual budget in INR (None = unlimited)"
    )
    preferred_states: tuple[IndiaState, ...] = Field(
        default_factory=tuple,
        description="States the candidate is willing to study in (empty = all)",
    )

    def prefers_state(self, state: IndiaState) -> bool:
        return state in self.preferred_states

    def feature_vector(self) -> dict[str, Any]:
        """Deterministic dict representation consumed by ML feature stores.

        Explicitly excluded from ML features: anything that could leak the
        answer or personal identity. This method is the contract the future
        feature-transformer pipeline will extend.
        """
        return {
            "air": self.air,
            "marks": self.marks,
            "category": self.category.value,
            "domicile_state": self.domicile_state.value,
            "gender": self.gender.value,
            "pw_d": self.pw_d.value,
            "minority": self.minority.value,
            "quota_type": self.quota_type.value,
            "budget": self.budget,
            "preferred_states": [s.value for s in self.preferred_states],
        }
