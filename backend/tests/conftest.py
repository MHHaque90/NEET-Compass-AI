"""Shared test fixtures.

Unit tests never touch a database — every external collaborator is a fake
implementing a domain port. This keeps the suite fast and deterministic.
"""

from __future__ import annotations

import uuid

import pytest

from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.college import College
from app.domain.enums import (
    Category,
    CollegeOwnership,
    Course,
    Gender,
    IndiaState,
    PwdStatus,
    QuotaType,
)


@pytest.fixture
def sample_candidate() -> CandidateProfile:
    return CandidateProfile(
        air=5000,
        marks=600,
        category=Category.GENERAL,
        domicile_state=IndiaState.KARNATAKA,
        gender=Gender.NEUTRAL,
        pw_d=PwdStatus.NONE,
        quota_type=QuotaType.AIQ,
        budget=2_000_000,
        preferred_states=(IndiaState.KARNATAKA, IndiaState.TAMIL_NADU),
    )


@pytest.fixture
def sample_college() -> College:
    return College(
        id=uuid.uuid4(),
        code="KAR-MYS-001",
        name="Mysore Medical College",
        state=IndiaState.KARNATAKA,
        city="Mysore",
        course=Course.MBBS,
        ownership=CollegeOwnership.GOVERNMENT,
        annual_fee_inr=50_000,
        total_seats=150,
        aiq_seats=30,
    )


@pytest.fixture
def expensive_college() -> College:
    return College(
        id=uuid.uuid4(),
        code="KAR-PVT-099",
        name="Private Medical College",
        state=IndiaState.KARNATAKA,
        city="Bengaluru",
        course=Course.MBBS,
        ownership=CollegeOwnership.PRIVATE,
        annual_fee_inr=15_000_000,
        total_seats=200,
        aiq_seats=40,
    )
