"""Tests for the Maharashtra adapter value transformations."""

from __future__ import annotations

from etl.contracts.canonical import SourceMetadata
from etl.contracts.sources.maharashtra.adapters import (
    MaharashtraAllotmentsAdapter,
    MaharashtraSeatMatrixAdapter,
)
from etl.contracts.sources.maharashtra.contracts import (
    allotments_2026_contract,
    seat_matrix_2026_contract,
)
from etl.contracts.sources.maharashtra.provenance import bytes_checksum

# --- Seat matrix test data ---

_SEAT_MATRIX_HEADER = [
    "StateName", "Institute", "Course", "Category", "Quota", "TotalSeats",
]


def _raw_seat_matrix(category: str, quota: str, institute: str, seats: str) -> dict[str, Any]:
    return {
        "StateName": "Maharashtra",
        "Institute": institute,
        "Course": "MBBS",
        "Category": category,
        "Quota": quota,
        "TotalSeats": seats,
    }


def _metadata() -> SourceMetadata:
    return SourceMetadata(
        source_id="mcc_state_maharashtra",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="seat_matrix",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="mah_seat_matrix_2026_abc123",
        file_checksum=bytes_checksum(b"sample"),
        parser_version="mah_etl_v1",
    )


def test_adapter_maps_real_columns_to_canonical() -> None:
    contract = seat_matrix_2026_contract()
    adapter = MaharashtraSeatMatrixAdapter()
    raw = [
        _raw_seat_matrix("OP", "AI", "ASCSR Govt Medical College, Nellore", "100"),
        _raw_seat_matrix("BC", "AI", "ASCSR Govt Medical College, Nellore", "50"),
        _raw_seat_matrix("ST PwD", "MM", "AIIMS Mumbai", "20"),
    ]
    result = adapter.transform(raw, contract, _metadata())
    assert result.records_transformed == 3
    assert result.records_skipped == 0
    first, second, third = result.records
    assert first["college_name"] == "ASCSR Govt Medical College, Nellore"
    assert first["quota_id"] == "ai"
    assert first["category_id"] == "gn"
    assert first["pwd"] is False
    assert first["total_seats"] == 100
    assert first["effective_year"] == 2026
    assert second["category_id"] == "bc"
    assert second["pwd"] is False
    assert second["quota_id"] == "ai"
    assert third["category_id"] == "st_pwd"
    assert third["pwd"] is True
    assert third["quota_id"] == "mm"


def test_adapter_strips_empty_institute_rows() -> None:
    contract = seat_matrix_2026_contract()
    adapter = MaharashtraSeatMatrixAdapter()
    raw = [_raw_seat_matrix("BC", "AI", "ASCSR, Nellore", "6"), {"Institute": ""}]
    result = adapter.transform(raw, contract, _metadata())
    assert result.records_transformed == 1
    assert result.records_skipped == 1


def test_adapter_validate_source_flags_missing_columns() -> None:
    contract = seat_matrix_2026_contract()
    adapter = MaharashtraSeatMatrixAdapter()
    errors = adapter.validate_source([{"StateName": "X"}], contract)
    missing = [e for e in errors if "not found" in e]
    assert len(missing) >= 1
    assert adapter.validate_source([], contract) == ["Maharashtra seat matrix source data is empty"]


# --- Allotment test data ---

_ALLOTMENT_HEADER = [
    "Institute", "Course", "Category", "Quota", "Round", "OpeningRank",
    "ClosingRank", "SeatCount",
]


def _raw_allotment(category: str, rank: str = "42531", score: str = "188.50") -> dict[str, Any]:
    return {
        "Institute": "ASCSR Govt Medical College, Nellore",
        "Course": "MBBS",
        "Category": category,
        "Quota": "AI",
        "Round": "Round 1",
        "OpeningRank": rank,
        "ClosingRank": str(int(rank) + 100),
        "SeatCount": "1",
    }


def _metadata_allotment() -> SourceMetadata:
    return SourceMetadata(
        source_id="mcc_state_maharashtra",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="allotments",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="mah_allotments_2026_abc123",
        file_checksum=bytes_checksum(b"sample"),
        parser_version="mah_etl_v1",
    )


def test_adapter_maps_real_allotment_columns() -> None:
    contract = allotments_2026_contract()
    adapter = MaharashtraAllotmentsAdapter()
    result = adapter.transform([_raw_allotment("GN")], contract, _metadata_allotment())
    assert result.records_transformed == 1
    rec = result.records[0]
    assert rec["course_id"] == "mbbs"
    assert rec["quota_id"] == "ai"
    assert rec["category_id"] == "gn"
    assert rec["round_id"] == "round_1"
    assert rec["opening_rank"] == 42531
    assert rec["closing_rank"] == 42631
    assert rec["seat_count"] == 1


def test_adapter_parses_pwd_category() -> None:
    adapter = MaharashtraAllotmentsAdapter()
    result = adapter.transform(
        [_raw_allotment("GN PwD", rank="510024")], allotments_2026_contract(), _metadata_allotment()
    )
    rec = result.records[0]
    assert rec["category_id"] == "gn_pwd"
    assert rec["opening_rank"] == 510024


def test_adapter_never_emits_pii_columns() -> None:
    adapter = MaharashtraAllotmentsAdapter()
    raw = dict(_raw_allotment("GN"), **{"Candidate Name": "John Doe", "Percentile": "95.5"})
    result = adapter.transform([raw], allotments_2026_contract(), _metadata_allotment())
    for rec in result.records:
        assert not (set(rec) & {"Candidate Name", "Percentile"})
