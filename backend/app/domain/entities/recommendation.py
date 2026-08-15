"""The recommendation — the output contract of the platform.

Every recommendation is fully auditable: it references the candidate and
college, the engine that produced it, and the human-readable reasoning
behind each score. `probability` and `confidence` are `None` until a real
engine (rule-based or ML) is registered; the API contract stays stable
regardless.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import Course, RecommendationStatus


class Recommendation(BaseModel):
    """Immutable snapshot of one admission recommendation."""

    model_config = {"frozen": True}

    id: uuid.UUID | None = Field(default=None)
    candidate_id: uuid.UUID | None = Field(
        default=None, description="Persisted candidate id; None when candidate is not yet stored"
    )
    college_id: uuid.UUID | None = Field(default=None)
    course: Course

    # ── Engine output (None until a real engine runs) ──────────────────────
    probability: float | None = Field(default=None, ge=0, le=1)
    expected_round: int | None = Field(default=None, ge=1, le=5)
    confidence: float | None = Field(default=None, ge=0, le=1)
    engine_name: str = Field(default="rule-based")
    engine_version: str | None = None
    status: RecommendationStatus = RecommendationStatus.PENDING

    # ── Explainability ─────────────────────────────────────────────────────
    reasons: tuple[dict[str, Any], ...] = Field(
        default_factory=tuple,
        description="Ordered list of {type, message, data} explanation blocks",
    )
    strategy: dict[str, Any] = Field(
        default_factory=dict, description="Counselling strategy payload (rounds, risks, upgrades)"
    )
    choice_filling_order: tuple[uuid.UUID, ...] = Field(
        default_factory=tuple, description="Recommended order of college ids to fill"
    )
