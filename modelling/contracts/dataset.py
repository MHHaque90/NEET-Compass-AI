"""
Modelling Dataset Contract - Phase 2
Formal interface for the canonical modelling dataset.

Distinguishes: SOURCE_FACTS | DERIVED_FEATURES | TARGETS | PROVENANCE | TEMPORAL_METADATA
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class QuotaType(str, Enum):
    AI = "ai"
    STATE_QUOTA = "so"
    MANAGEMENT = "mm"
    DEEMED_UNIVERSITY = "du"
    ALL_INDIA_MINORITY = "am"
    CENTRAL_UNIVERSITY = "cu"
    ESIC = "es"
    ARMED_FORCES = "af"
    NRI = "nr"


class CategoryType(str, Enum):
    GN = "gn"
    BC = "bc"
    EW = "ew"
    SC = "sc"
    ST = "st"
    GN_PWD = "gn_pwd"
    BC_PWD = "bc_pwd"
    EW_PWD = "ew_pwd"
    SC_PWD = "sc_pwd"
    ST_PWD = "st_pwd"


class RoundType(str, Enum):
    ROUND_1 = "round_1"
    ROUND_2 = "round_2"
    ROUND_3 = "round_3"
    STRAY_VACANCY = "stray_vacancy"


class AuthorityType(str, Enum):
    MCC = "MCC"
    MAHARASHTRA = "MAHARASHTRA"
    KARNATAKA = "KARNATAKA"
    UTTAR_PRADESH = "UTTAR_PRADESH"


@dataclass(frozen=True)
class SourceFacts:
    """
    SOURCE FACTS - Directly from canonical ETL output (SeatMatrix + Allotment)
    These fields are verifiable, provenance-tracked, and already exist in architecture.
    """

    counselling_year: int
    state: str
    counselling_authority: AuthorityType
    round: RoundType
    course: str
    institute: str
    institute_code: str
    quota: QuotaType
    category: CategoryType
    total_seats: int
    allotment_count: int
    closing_rank: int | None = None
    score: float | None = None
    opening_rank: int | None = None
    vacancy_seats: int | None = None

    def __post_init__(self):
        if self.counselling_year < 2021 or self.counselling_year > 2030:
            raise ValueError(f"Invalid counselling_year: {self.counselling_year}")
        if self.total_seats < 0:
            raise ValueError(f"total_seats cannot be negative: {self.total_seats}")
        if self.allotment_count < 0:
            raise ValueError(f"allotment_count cannot be negative: {self.allotment_count}")
        if self.closing_rank is not None and self.closing_rank < 1:
            raise ValueError(f"closing_rank must be >= 1: {self.closing_rank}")
        if self.opening_rank is not None and self.opening_rank < 1:
            raise ValueError(f"opening_rank must be >= 1: {self.opening_rank}")


@dataclass(frozen=True)
class DerivedFeatures:
    """
    DERIVED FEATURES - Computed at dataset construction time.
    Must be computable at PREDICTION TIME using only information available then.
    """

    round_number: int
    is_first_round: bool
    category_quota_combo: str
    institute_type: str
    state_quota_indicator: bool
    year_index: int
    seat_count_log: float
    historical_closing_rank_median: float | None = None
    historical_closing_rank_p10: float | None = None
    historical_closing_rank_p90: float | None = None
    seat_availability_ratio: float | None = None
    prior_year_closing_rank: int | None = None
    prior_year_seat_count: int | None = None
    seat_count_change_pct: float | None = None
    feature_version: str = "features_v1"

    def __post_init__(self):
        if self.round_number < 1 or self.round_number > 4:
            raise ValueError(f"round_number must be 1-4: {self.round_number}")
        if self.year_index < 0:
            raise ValueError(f"year_index cannot be negative: {self.year_index}")
        if self.seat_count_log < 0:
            raise ValueError(f"seat_count_log cannot be negative: {self.seat_count_log}")


@dataclass(frozen=True)
class Targets:
    """
    TARGETS - What we might predict.
    Current status: NO_TARGET_READY per target-definition-phase4.md
    """

    closing_rank: int | None = None
    opening_rank: int | None = None
    admission_probability: float | None = None
    seat_allocation: str | None = None
    vacancy_after_round: int | None = None
    target_version: str = "targets_v1"
    target_ready: bool = False
    target_readiness_reason: str = "NO_TARGET_READY"

    def __post_init__(self):
        if self.admission_probability is not None:
            if not 0.0 <= self.admission_probability <= 1.0:
                raise ValueError(
                    f"admission_probability must be in [0,1]: {self.admission_probability}"
                )
        if self.closing_rank is not None and self.closing_rank < 1:
            raise ValueError(f"closing_rank must be >= 1: {self.closing_rank}")
        if self.opening_rank is not None and self.opening_rank < 1:
            raise ValueError(f"opening_rank must be >= 1: {self.opening_rank}")


@dataclass(frozen=True)
class Provenance:
    """
    PROVENANCE - Required for every modelling record.
    Every record MUST carry full provenance for reproducibility and audit.
    """

    source_file_id: str
    file_checksum: str
    source_url: str
    parser_version: str
    retrieval_timestamp: datetime
    contract_version: str
    adapter_version: str
    transformation_version: str
    feature_version: str
    quality_gate_version: str

    def __post_init__(self):
        if not self.source_file_id:
            raise ValueError("source_file_id is required")
        if not self.file_checksum:
            raise ValueError("file_checksum is required")
        if len(self.file_checksum) != 64:
            raise ValueError(f"file_checksum must be SHA-256 (64 chars): {self.file_checksum}")


@dataclass(frozen=True)
class TemporalMetadata:
    """
    TEMPORAL METADATA - Information about temporal boundaries and availability.
    Critical for leakage prevention and temporal validation.
    """

    prediction_time: datetime
    latest_allowed_year: int
    latest_allowed_round: RoundType
    feature_computation_timestamp: datetime
    temporal_availability_verified: bool = True
    leakage_check_passed: bool = True

    def __post_init__(self):
        if self.latest_allowed_year < 2021:
            raise ValueError(f"latest_allowed_year must be >= 2021: {self.latest_allowed_year}")


@dataclass(frozen=True)
class ModellingRecord:
    """
    Canonical modelling dataset record.
    One row per: college × course × quota × category × round × year
    Source of truth: Aggregated from canonical SeatMatrix + Allotment records.
    """

    source_facts: SourceFacts
    derived_features: DerivedFeatures
    targets: Targets
    provenance: Provenance
    temporal_metadata: TemporalMetadata
    dataset_version: str
    record_id: str

    def __post_init__(self):
        if not self.record_id:
            raise ValueError("record_id is required")
        if not self.dataset_version:
            raise ValueError("dataset_version is required")


@dataclass(frozen=True)
class ModellingDatasetContract:
    """
    Formal modelling dataset interface.
    Defines the complete contract for a modelling dataset version.
    """

    dataset_version: str
    created_timestamp: datetime
    source_file_ids: list[str]
    source_checksums: dict[str, str]
    transformation_version: str
    feature_version: str
    quality_gate_version: str
    quality_gate_results: dict[str, Any]
    row_count: int
    column_count: int
    year_range: tuple[int, int]
    authorities: list[AuthorityType]
    target_variables: list[str]
    schema_hash: str
    modelling_ready: bool = False
    temporal_validation_blocked: bool = True
    target_readiness: str = "NO_TARGET_READY"
    notes: str = ""

    def __post_init__(self):
        if not self.dataset_version:
            raise ValueError("dataset_version is required")
        if self.row_count < 0:
            raise ValueError(f"row_count cannot be negative: {self.row_count}")
        if self.column_count < 0:
            raise ValueError(f"column_count cannot be negative: {self.column_count}")
        if self.year_range[0] > self.year_range[1]:
            raise ValueError(f"Invalid year_range: {self.year_range}")


def compute_record_id(record: ModellingRecord) -> str:
    """Compute deterministic record ID from source facts."""
    import hashlib

    key = f"{record.source_facts.counselling_year}|{record.source_facts.counselling_authority.value}|{record.source_facts.institute_code}|{record.source_facts.course}|{record.source_facts.quota.value}|{record.source_facts.category.value}|{record.source_facts.round.value}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def compute_dataset_version(
    source_file_ids: list[str],
    transformation_version: str,
    feature_version: str,
    quality_gate_version: str,
) -> str:
    """Compute deterministic dataset version from components."""
    import hashlib

    sorted_ids = "|".join(sorted(source_file_ids))
    components = f"{sorted_ids}|{transformation_version}|{feature_version}|{quality_gate_version}"
    return hashlib.sha256(components.encode()).hexdigest()[:16]
