"""Recommendation audit table — every generated recommendation, immutable.

Stores the full explainable snapshot (reasons, strategy, choice order) plus
engine provenance so decisions can be reviewed, debugged, and model-versions
compared after the fact.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Course, RecommendationStatus
from app.infrastructure.db.models._base import Base, TimestampMixin


class RecommendationModel(Base, TimestampMixin):
    __tablename__ = "recommendations"
    __table_args__ = (Index("ix_recommendations_candidate", "candidate_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True
    )
    college_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True
    )
    course: Mapped[Course] = mapped_column(
        Enum(Course, name="course", native_enum=False, length=10, validate_strings=True),
        nullable=False,
    )

    # ── Engine output ──────────────────────────────────────────────────────
    probability: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    expected_round: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    engine_name: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(
            RecommendationStatus,
            name="recommendation_status",
            native_enum=False,
            length=16,
            validate_strings=True,
        ),
        nullable=False,
    )

    # ── Explainability payloads ────────────────────────────────────────────
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    strategy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    choice_filling_order: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RecommendationModel id={self.id} engine={self.engine_name} status={self.status}>"
