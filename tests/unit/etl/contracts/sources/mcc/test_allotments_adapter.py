"""Tests for the MCC allotments adapter value transformations + PII guard."""

from __future__ import annotations

from typing import Any

from etl.contracts.canonical import SourceMetadata
from etl.contracts.sources.mcc.adapters import MCCAllotmentsAdapter
from etl.contracts.sources.mcc.contracts import (
    ALLOTMENT_PRIVACY_BLOCKLIST,
    allotments_2025_contract,
)
from etl.contracts.sources.mcc.provenance import bytes_checksum

_HEADER = [
    "Institute Code", "Institute Name", "Course", "Quota", "Category",
    "Round", "Rank", "Score", "Seats",
]


def _metadata() -> SourceMetadata:
    return SourceMetadata(
        source_id="mcc", authority="MCC / DGHS", dataset="allotments",
        effective_year=2025, publication_version="Round 3", contract_version="1.1.0",
        retrieval_timestamp="2025-01-01T00:00:00+00:00",
        source_file_id="mcc_allotments_2025_abc123", file_checksum=bytes_checksum(b"sample"),
        parser_version="mcc_etl_v1",
    )


def _raw(category: str, rank: str = "42531", score: str = "188.50") -> dict[str, Any]:
    return {
        "Institute Code": "200510",
        "Institute Name": "AIIMS Mangalagiri, Guntur",
        "Course": "MBBS (MBBS)",
        "Quota": "AI",
        "Category": category,
        "Round": "Round 3",
        "Rank": rank,
        "Score": score,
        "Seats": "1",
    }


def test_adapter_maps_real_allotment_columns() -> None:
    contract = allotments_2025_contract()
    adapter = MCCAllotmentsAdapter()
    result = adapter.transform([_raw("GN")], contract, _metadata())
    assert result.records_transformed == 1
    rec = result.records[0]
    assert rec["college_id"] == "200510"
    assert rec["course_id"] == "mbbs"
    assert rec["quota_id"] == "ai"
    assert rec["category_id"] == "gn"
    assert rec["round_id"] == "round_3"
    assert rec["rank"] == 42531
    assert rec["score"] == 188.5
    assert rec["seat_count"] == 1


def test_adapter_parses_pwd_category() -> None:
    adapter = MCCAllotmentsAdapter()
    result = adapter.transform(
        [_raw("GN PwD", rank="510024")], allotments_2025_contract(), _metadata()
    )
    rec = result.records[0]
    assert rec["category_id"] == "gn_pwd"
    assert rec["rank"] == 510024


def test_adapter_never_emits_pii_columns() -> None:
    adapter = MCCAllotmentsAdapter()
    raw = dict(_raw("GN"), **{"Candidate Name": "John Doe", "Percentile": "95.5"})
    result = adapter.transform([raw], allotments_2025_contract(), _metadata())
    for rec in result.records:
        assert not (set(rec) & ALLOTMENT_PRIVACY_BLOCKLIST)


def test_adapter_validate_source_rejects_pii_columns() -> None:
    contract = allotments_2025_contract()
    adapter = MCCAllotmentsAdapter()
    raw = {"Institute Code": "200510", "Candidate Name": "John Doe", "Rank": "1"}
    errors = adapter.validate_source([raw], contract)
    assert any("PII" in e for e in errors)


def test_adapter_validate_source_flags_missing_columns() -> None:
    contract = allotments_2025_contract()
    adapter = MCCAllotmentsAdapter()
    errors = adapter.validate_source([{"Rank": "1"}], contract)
    assert any("not found" in e for e in errors)
