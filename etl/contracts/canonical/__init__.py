"""Canonical contract models for NEET Compass AI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class College:
    """Canonical college representation."""

    college_id: str
    college_name: str
    state_id: str | None = None
    district_id: str | None = None
    authority: str | None = None
    college_type: str | None = None


@dataclass(frozen=True)
class Course:
    """Canonical course representation."""

    course_id: str
    course_name: str
    course_type: str | None = None
    duration_years: int | None = None


@dataclass(frozen=True)
class SeatMatrix:
    """Canonical seat matrix representation."""

    college_id: str
    course_id: str
    quota_id: str
    category_id: str
    total_seats: int
    effective_year: int


@dataclass(frozen=True)
class Allotment:
    """Canonical allotment representation."""

    allotment_id: str | None = None
    college_id: str = ""
    course_id: str = ""
    quota_id: str = ""
    category_id: str = ""
    round_id: str = ""
    rank: int | None = None
    score: float | None = None
    seat_count: int = 1
    effective_year: int = 0
    publication_version: str = ""
    source_file_id: str | None = None


@dataclass(frozen=True)
class HistoricalCutoff:
    """Canonical historical cutoff representation."""

    college_id: str
    course_id: str
    year: int
    round_id: str
    quota_id: str
    category_id: str
    cutoff_rank: int | None = None
    cutoff_score: float | None = None
    source_file_id: str | None = None


@dataclass(frozen=True)
class Fee:
    """Canonical fee representation."""

    college_id: str
    course_id: str
    quota_id: str
    fee_amount: float
    fee_type: str = "annual"
    effective_year: int = 0


@dataclass(frozen=True)
class Quota:
    """Canonical quota representation."""

    quota_id: str
    quota_name: str
    quota_type: str | None = None


@dataclass(frozen=True)
class Category:
    """Canonical category representation."""

    category_id: str
    category_name: str
    category_type: str | None = None


@dataclass(frozen=True)
class Round:
    """Canonical round representation."""

    round_id: str
    round_name: str
    round_number: int | None = None
    round_type: str | None = None


@dataclass(frozen=True)
class State:
    """Canonical state representation."""

    state_id: str
    state_name: str
    state_code: str | None = None


@dataclass(frozen=True)
class District:
    """Canonical district representation."""

    district_id: str
    district_name: str
    state_id: str
    district_code: str | None = None


@dataclass(frozen=True)
class SourceMetadata:
    """Provenance metadata for sourced data."""

    source_id: str
    authority: str
    dataset: str
    effective_year: int
    publication_version: str
    contract_version: str
    retrieval_timestamp: str
    source_file_id: str | None = None
    file_checksum: str | None = None
    parser_version: str | None = None
    source_url: str | None = None
