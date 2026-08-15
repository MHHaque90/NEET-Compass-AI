"""User table — platform users (candidates, admins, etc.)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import Category, Gender, QuotaType
from app.infrastructure.db.models._base import Base, TimestampMixin


class UserModel(Base, TimestampMixin):
    """Platform users — candidates who register for predictions."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_phone", "phone"),
        Index("ix_users_air", "air"),
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("phone", name="uq_users_phone"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Candidate profile fields (denormalized for prediction convenience)
    air: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[Category | None] = mapped_column(
        Enum(Category, name="category", native_enum=False, length=32, validate_strings=True),
        nullable=True,
    )
    domicile_state_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("states.id", ondelete="SET NULL"), nullable=True
    )
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender", native_enum=False, length=16, validate_strings=True),
        nullable=True,
    )
    is_pwd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_minority: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quota_type: Mapped[QuotaType | None] = mapped_column(
        Enum(QuotaType, name="quota_type", native_enum=False, length=16, validate_strings=True),
        nullable=True,
    )
    budget_inr: Mapped[int | None] = mapped_column(Numeric(12, 2), nullable=True)
    preferred_states: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<UserModel email={self.email!r} name={self.full_name!r} air={self.air}>"
