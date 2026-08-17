"""End-to-end pipeline tests: ingestion, validation, idempotency, PII guard."""

from __future__ import annotations

from etl.contracts.errors import ErrorCode
from etl.contracts.sources.karnataka.pipeline import (
    InMemoryFileRegistry,
    allotment_loader,
    ingest_allotments,
    ingest_seat_matrix,
    seat_matrix_loader,
)
from etl.contracts.sources.karnataka.provenance import build_source_file_id, file_checksum


def test_full_ingest_seat_matrix_succeeds(seat_matrix_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = seat_matrix_loader()

    result = ingest_seat_matrix(seat_matrix_csv, registry, loader)

    assert result.file_ingested is True
    assert result.errors == []
    assert result.records_transformed == 8
    assert result.records_skipped == 0
    assert loader.count() == 8
    assert result.metadata is not None
    assert result.metadata.file_checksum is not None
    expected_id = build_source_file_id(result.metadata.file_checksum, "mcc_state_karnataka", "seat_matrix", 2026)
    assert result.metadata.source_file_id == expected_id
    assert result.metadata.file_checksum == file_checksum(seat_matrix_csv)


def test_ingestion_is_idempotent_by_checksum(seat_matrix_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = seat_matrix_loader()

    first = ingest_seat_matrix(seat_matrix_csv, registry, loader)
    assert first.file_ingested is True
    assert loader.count() == 8

    second = ingest_seat_matrix(seat_matrix_csv, registry, loader)
    assert second.file_ingested is False
    assert second.records_transformed == 0
    assert second.records_skipped == 8
    assert loader.count() == 8  # no second write


def test_duplicate_rows_within_a_file_are_rejected(duplicate_seat_matrix_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = seat_matrix_loader()

    result = ingest_seat_matrix(duplicate_seat_matrix_csv, registry, loader)

    dups = [e for e in result.errors if e.error_code == ErrorCode.DUPLICATE_RECORD]
    assert len(dups) == 1
    assert result.records_transformed == 1
    assert loader.count() == 1


def test_invalid_category_is_captured_as_enum_error(bad_seat_matrix_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = seat_matrix_loader()

    result = ingest_seat_matrix(bad_seat_matrix_csv, registry, loader)

    assert result.file_ingested is True
    assert result.records_transformed == 0
    enum_errors = [e for e in result.errors if e.error_code == ErrorCode.INVALID_ENUM_VALUE]
    assert len(enum_errors) == 1
    assert loader.count() == 0


def test_full_ingest_allotments_succeeds(allotment_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = allotment_loader()

    result = ingest_allotments(allotment_csv, registry, loader)

    assert result.file_ingested is True
    assert result.errors == []
    assert result.records_transformed == 4
    assert loader.count() == 4
    loaded = loader.all()
    ranks = {rec["opening_rank"] for rec in loaded}
    assert ranks == {1, 5001, 10001, 8001}
    assert all(isinstance(r, int) for r in ranks)
    categories = {rec["category_id"] for rec in loaded}
    assert {"gn", "sc", "st_pwd"} <= categories


def test_pii_allotment_is_not_loaded(pii_allotment_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = allotment_loader()

    result = ingest_allotments(pii_allotment_csv, registry, loader)

    assert result.file_ingested is True
    loaded = loader.all()
    for rec in loaded:
        assert not (set(rec) & {"Candidate Name", "Percentile"})


def test_source_url_is_carried_in_metadata(seat_matrix_csv) -> None:
    registry = InMemoryFileRegistry()
    loader = seat_matrix_loader()
    url = "https://cetonline.karnataka.gov.in/kea/"

    result = ingest_seat_matrix(seat_matrix_csv, registry, loader, source_url=url)

    assert result.file_ingested is True
    assert result.metadata is not None
    assert result.metadata.source_url == url


def test_three_runs_same_source_url_changed_bytes(tmp_path, seat_matrix_csv) -> None:
    """Run 1/2/3: same URL stays one logical source; a content change at that
    URL regenerates the file identity but never duplicates existing rows.

    - Run 1: ingest the file -> 8 rows, source identity from content checksum.
    - Run 2: same bytes, same URL -> short-circuits on checksum, no writes.
    - Run 3: same URL, *changed* bytes -> new checksum -> new source_file_id,
      re-ingest merges: 7 untouched rows keep their keys, the republished row
      adds one new key. Nothing is duplicated and no ingestion is lost.
    """
    registry = InMemoryFileRegistry()
    loader = seat_matrix_loader()

    run1 = ingest_seat_matrix(seat_matrix_csv, registry, loader, source_url="https://cetonline.karnataka.gov.in/kea/")
    assert run1.file_ingested is True
    assert run1.records_transformed == 8
    assert loader.count() == 8

    run2 = ingest_seat_matrix(seat_matrix_csv, registry, loader, source_url="https://cetonline.karnataka.gov.in/kea/")
    assert run2.file_ingested is False
    assert run2.records_transformed == 0
    assert run2.records_skipped == 8
    assert loader.count() == 8  # no duplicate rows on re-run

    changed = tmp_path / "seatmatrix_ka_r1_2026_v2.csv"
    # Replace a TotalSeats value (does not affect composite key)
    changed.write_bytes(seat_matrix_csv.read_bytes().replace(b"150", b"999", 1))

    run3 = ingest_seat_matrix(changed, registry, loader, source_url="https://cetonline.karnataka.gov.in/kea/")
    assert run3.file_ingested is True  # same source_url, new bytes
    assert run3.records_transformed == 8  # all 8 rows ingested; TotalSeats not in composite key
    assert loader.count() == 8  # no new duplicate keys

    assert run1.metadata is not None and run2.metadata is not None and run3.metadata is not None
    assert run1.metadata.source_url == run2.metadata.source_url == "https://cetonline.karnataka.gov.in/kea/"
    assert run3.metadata.source_url == "https://cetonline.karnataka.gov.in/kea/"
    # Content identity drives file identity; URL identity does not change.
    assert run1.metadata.source_file_id == run2.metadata.source_file_id
    assert run3.metadata.source_file_id != run1.metadata.source_file_id