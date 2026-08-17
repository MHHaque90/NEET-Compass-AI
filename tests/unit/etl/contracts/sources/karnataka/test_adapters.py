"""Tests for the Karnataka KEA adapter value transformations."""

from __future__ import annotations

from etl.contracts.canonical import SourceMetadata
from etl.contracts.sources.karnataka.adapters import (
    KarnatakaAllotmentsAdapter,
    KarnatakaSeatMatrixAdapter,
)
from etl.contracts.sources.karnataka.contracts import (
    allotments_2026_contract,
    seat_matrix_2026_contract,
)
from etl.contracts.sources.karnataka.provenance import bytes_checksum

# --- Seat matrix test data ---


def _raw_seat_matrix(category: str, quota: str, institute: str, seats: str) -> dict[str, Any]:
    return {
        "Institute": institute,
        "Course": "MBBS",
        "Category": category,
        "Quota": quota,
        "TotalSeats": seats,
    }


def _metadata() -> SourceMetadata:
    return SourceMetadata(
        source_id="mcc_state_karnataka",
        authority="Karnataka Examinations Authority",
        dataset="seat_matrix",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="ka_seat_matrix_2026_abc123",
        file_checksum=bytes_checksum(b"sample"),
        parser_version="ka_etl_v1",
    )


def test_adapter_maps_real_columns_to_canonical() -> None:
    contract = seat_matrix_2026_contract()
    adapter = KarnatakaSeatMatrixAdapter()
    raw = [
        _raw_seat_matrix("GM", "AI", "RV College of Engineering", "150"),
        _raw_seat_matrix("SC", "AI", "RV College of Engineering", "50"),
        _raw_seat_matrix("ST", "AI", "RV College of Engineering", "10"),
        _raw_seat_matrix("CAT-1", "AI", "RV College of Engineering", "30"),
        _raw_seat_matrix("GM PwD", "AI", "BMC Medical College", "5"),
        _raw_seat_matrix("ST", "SO", "BMC Medical College", "8"),
    ]
    result = adapter.transform(raw, contract, _metadata())
    assert result.records_transformed == 6
    assert result.records_skipped == 0
    first, second, third, fourth, fifth, sixth = result.records
    assert first["college_name"] == "RV College of Engineering"
    assert first["quota_id"] == "ai"
    assert first["category_id"] == "gn"
    assert first["pwd"] is False
    assert first["total_seats"] == 150
    assert first["effective_year"] == 2026
    assert second["category_id"] == "sc"
    assert second["pwd"] is False
    assert second["quota_id"] == "ai"
    assert third["category_id"] == "st"
    assert third["pwd"] is False
    assert third["quota_id"] == "ai"
    assert fourth["category_id"] == "bc"
    assert fourth["pwd"] is False
    assert fourth["quota_id"] == "ai"
    assert fifth["category_id"] == "gn_pwd"
    assert fifth["pwd"] is True
    assert fifth["quota_id"] == "ai"
    assert sixth["category_id"] == "st"
    assert sixth["pwd"] is False
    assert sixth["quota_id"] == "so"


def test_adapter_strips_empty_institute_rows() -> None:
    contract = seat_matrix_2026_contract()
    adapter = KarnatakaSeatMatrixAdapter()
    raw = [_raw_seat_matrix("BC", "AI", "RV College of Engineering", "6"), {"Institute": ""}]
    result = adapter.transform(raw, contract, _metadata())
    assert result.records_transformed == 1
    assert result.records_skipped == 1


def test_adapter_validate_source_flags_missing_columns() -> None:
    contract = seat_matrix_2026_contract()
    adapter = KarnatakaSeatMatrixAdapter()
    errors = adapter.validate_source([{"Institute": "X"}], contract)
    missing = [e for e in errors if "not found" in e]
    assert len(missing) >= 1
    assert adapter.validate_source([], contract) == ["Karnataka seat matrix source data is empty"]


# --- Allotment test data ---


def _raw_allotment(category: str, rank: str = "42531") -> dict[str, Any]:
    return {
        "Institute": "RV College of Engineering",
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
        source_id="mcc_state_karnataka",
        authority="Karnataka Examinations Authority",
        dataset="allotments",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="ka_allotments_2026_abc123",
        file_checksum=bytes_checksum(b"sample"),
        parser_version="ka_etl_v1",
    )


def test_adapter_maps_real_allotment_columns() -> None:
    contract = allotments_2026_contract()
    adapter = KarnatakaAllotmentsAdapter()
    result = adapter.transform([_raw_allotment("GM")], contract, _metadata_allotment())
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
    adapter = KarnatakaAllotmentsAdapter()
    result = adapter.transform(
        [_raw_allotment("ST PwD", rank="510024")], allotments_2026_contract(), _metadata_allotment()
    )
    rec = result.records[0]
    assert rec["category_id"] == "st_pwd"
    assert rec["opening_rank"] == 510024


def test_adapter_never_emits_pii_columns() -> None:
    adapter = KarnatakaAllotmentsAdapter()
    raw = dict(_raw_allotment("GM"), **{"Candidate Name": "John Doe", "Percentile": "95.5"})
    result = adapter.transform([raw], allotments_2026_contract(), _metadata_allotment())
    for rec in result.records:
        assert not (set(rec) & {"Candidate Name", "Percentile"})