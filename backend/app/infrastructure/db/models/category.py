"""Category master table — reservation categories for NEET counselling."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models._base import Base, TimestampMixin


class CategoryModel(Base, TimestampMixin):
    """Master list of reservation categories (GENERAL, OBC, SC, ST, EWS, etc.)."""

    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("code", name="uq_categories_code"),
        UniqueConstraint("name", name="uq_categories_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reservation_percentage: Mapped[float | None] = mapped_column(nullable=True)
    is_vertical: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<CategoryModel code={self.code!r} name={self.name!r} vertical={self.is_vertical}>"
