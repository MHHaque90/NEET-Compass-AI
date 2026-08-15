"""A single historical allotment row.

Every row is one real counselling event from the raw cut-off/allotment
tables released by MCC (AIQ) and state bodies. This is the raw material the
ML model will learn from and the source of every data-backed explanation.
"""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums import Category, Course, Gender, PwdStatus, QuotaType


class AllotmentRecord(BaseModel):
    """Immutable historical fact: college X closed at rank Y in round Z.

    ``opening_*``/``closing_*`` use **ranks and marks** both because some
    states publish only marks and some only ranks.
    """

    model_config = {"frozen": True}

    id: uuid.UUID | None = Field(default=None)
    college_id: uuid.UUID
    college_code: str = Field(min_length=1, max_length=20)
    course: Course
    counselling_year: int = Field(ge=2013, description="NEET counselling began in 2013")
    counselling_date: date | None = None
    round_number: int = Field(ge=1, le=5)
    is_stray_round: bool = False
    quota_type: QuotaType
    category: Category
    gender: Gender
    pw_d: PwdStatus = PwdStatus.NONE
    opening_rank: int = Field(ge=1)
    closing_rank: int = Field(ge=1)
    opening_marks: float | None = Field(default=None, ge=0, le=720)
    closing_marks: float | None = Field(default=None, ge=0, le=720)
    seats_offered: int = Field(default=1, ge=0)
