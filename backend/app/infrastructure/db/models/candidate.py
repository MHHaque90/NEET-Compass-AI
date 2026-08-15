"""Candidate profiles table — persisted audit copy of each applicant."""

from __future__ import annotations

import uuid

from sqlalchemy import JSON, Boolean, Enum, Integer, Numeric, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Category, Gender, IndiaState, QuotaType
from app.infrastructure.db.models._base import Base, TimestampMixin

_STATE_ENUM = Enum(IndiaState, name="state", native_enum=False, length=40, validate_strings=True)


class CandidateModel(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    air: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    marks: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="category", native_enum=False, length=32, validate_strings=True),
        nullable=False,
    )
    domicile_state: Mapped[IndiaState] = mapped_column(_STATE_ENUM, nullable=False)
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, name="gender", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    is_pwd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_minority: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quota_type: Mapped[QuotaType] = mapped_column(
        Enum(QuotaType, name="quota_type", native_enum=False, length=16, validate_strings=True),
        nullable=False,
    )
    budget_inr: Mapped[int | None] = mapped_column(Numeric(12, 2), nullable=True)
    preferred_states: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CandidateModel air={self.air} category={self.category}>"
