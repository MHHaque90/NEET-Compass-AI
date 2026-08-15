"""Tests for the MCC seat-matrix adapter value transformations."""

from __future__ import annotations

from typing import Any

from etl.contracts.canonical import SourceMetadata
from etl.contracts.sources.mcc.adapters import MCCSeatMatrixAdapter
from etl.contracts.sources.mcc.contracts import seat_matrix_2025_contract
from etl.contracts.sources.mcc.provenance import bytes_checksum

_HEADER = [
    "StateName", "InstituteType", "Institute", "Quota", "Branch", "Category", "TotalSeats",
]


def _raw(category: str, quota: str, institute: str, seats: str) -> dict[str, Any]:
    return {
        "StateName": "Andhra Pradesh",
        "InstituteType": "All India except Central / University",
        "Institute": institute,
        "Quota": quota,
        "Branch": "MBBS (MBBS)",
        "Category": category,
        "TotalSeats": seats,
    }


def _metadata() -> SourceMetadata:
    return SourceMetadata(
        source_id="mcc",
        authority="MCC / DGHS",
        dataset="seat_matrix",
        effective_year=2025,
        publication_version="Round 1",
        contract_version="1.1.0",
        retrieval_timestamp="2025-01-01T00:00:00+00:00",
        source_file_id="mcc_seat_matrix_2025_abc123",
        file_checksum=bytes_checksum(b"sample"),
        parser_version="mcc_etl_v1",
    )


def test_adapter_maps_real_pdf_columns_to_canonical() -> None:
    contract = seat_matrix_2025_contract()
    adapter = MCCSeatMatrixAdapter()
    raw = [
        _raw(
            "BC NO", "All India",
            "ASCSR Govt Medical College, Nellore (200446)", "6",
        ),
        _raw(
            "OP PH", "Open Seat Quota",
            "AIIMS Mangalagiri, Guntur (200510)", "3",
        ),
        _raw(
            "BC PH", "All India",
            "ASCSR Govt Medical College, Nellore (200446)", "1",
        ),
    ]
    result = adapter.transform(raw, contract, _metadata())
    assert result.records_transformed == 3
    assert result.records_skipped == 0
    first, second, third = result.records
    assert first["college_id"] == "200446"
    assert first["category_id"] == "bc"
    assert first["pwd"] is False
    assert first["quota_id"] == "ai"
    assert first["course_id"] == "mbbs"
    assert first["total_seats"] == 6
    assert first["effective_year"] == 2025
    assert first["source_file_id"] == "mcc_seat_matrix_2025_abc123"
    assert second["college_id"] == "200510"
    assert second["category_id"] == "gn_pwd"
    assert second["pwd"] is True
    assert second["quota_id"] == "so"
    assert third["category_id"] == "bc_pwd"


def test_adapter_strips_empty_rows() -> None:
    contract = seat_matrix_2025_contract()
    adapter = MCCSeatMatrixAdapter()
    raw = [_raw("BC NO", "All India", "ASCSR, Nellore (200446)", "6"), {"Institute": ""}]
    result = adapter.transform(raw, contract, _metadata())
    assert result.records_transformed == 1
    assert result.records_skipped == 1


def test_adapter_validate_source_flags_missing_columns() -> None:
    contract = seat_matrix_2025_contract()
    adapter = MCCSeatMatrixAdapter()
    errors = adapter.validate_source([{"StateName": "X"}], contract)
    missing = [e for e in errors if "not found" in e]
    assert len(missing) >= 1
    assert adapter.validate_source([], contract) == ["Seat matrix source data is empty"]
