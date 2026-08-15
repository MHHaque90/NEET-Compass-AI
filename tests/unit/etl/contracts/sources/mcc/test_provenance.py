"""Tests for provenance: checksums, source-file id, metadata assembly."""

from __future__ import annotations

from etl.contracts.sources.mcc.provenance import (
    PARSER_VERSION,
    build_metadata,
    build_source_file_id,
    bytes_checksum,
    file_checksum,
)

SAMPLE = b"StateName,Institute\nAndhra Pradesh,X\n"


def test_file_checksum_is_stable(tmp_path) -> None:
    path = tmp_path / "sample.csv"
    path.write_bytes(SAMPLE)
    assert file_checksum(path) == file_checksum(path)


def test_identical_files_share_checksum(tmp_path) -> None:
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_bytes(SAMPLE)
    b.write_bytes(SAMPLE)
    assert file_checksum(a) == file_checksum(b)


def test_different_content_different_checksum(tmp_path) -> None:
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_bytes(b"abc")
    b.write_bytes(b"abd")
    assert file_checksum(a) != file_checksum(b)


def test_source_file_id_is_deterministic() -> None:
    checksum = bytes_checksum(SAMPLE)
    assert build_source_file_id(checksum, "mcc", "seat_matrix", 2025) == (
        build_source_file_id(checksum, "mcc", "seat_matrix", 2025)
    )
    other = build_source_file_id(bytes_checksum(b"other"), "mcc", "seat_matrix", 2025)
    assert other != build_source_file_id(checksum, "mcc", "seat_matrix", 2025)
    assert build_source_file_id(checksum, "mcc", "seat_matrix", 2025).startswith(
        "mcc_seat_matrix_2025_"
    )


def test_build_metadata_populates_provenance() -> None:
    checksum = bytes_checksum(SAMPLE)
    meta = build_metadata(
        source_id="mcc",
        authority="MCC / DGHS",
        dataset="seat_matrix",
        effective_year=2025,
        publication_version="Round 1",
        contract_version="1.1.0",
        checksum=checksum,
    )
    assert meta.source_id == "mcc"
    assert meta.file_checksum == checksum
    assert meta.parser_version == PARSER_VERSION
    assert meta.effective_year == 2025
    assert meta.source_file_id == build_source_file_id(checksum, "mcc", "seat_matrix", 2025)
    assert meta.publication_version == "Round 1"


def test_build_metadata_carries_source_url() -> None:
    checksum = bytes_checksum(SAMPLE)
    meta = build_metadata(
        source_id="mcc",
        authority="MCC / DGHS",
        dataset="allotments",
        effective_year=2025,
        publication_version="Round 3",
        contract_version="1.1.0",
        checksum=checksum,
        source_url="https://mcc.nic.in/archive-ug/",
    )
    assert meta.source_url == "https://mcc.nic.in/archive-ug/"


def test_provenance_taxonomy_is_complete() -> None:
    """Every real source record carries the full provenance taxonomy.

    ``publication_version`` is the round (e.g. ``"Round 3"``); ``source_url``
    records where the file was pulled from; identity (``source_file_id``) is
    derived from content, not from the URL, so a changed file at the same URL
    produces a new identity while leaving record identity untouched.
    """
    meta = build_metadata(
        source_id="mcc",
        authority="MCC / DGHS",
        dataset="allotments",
        effective_year=2025,
        publication_version="Round 3",
        contract_version="1.1.0",
        checksum=bytes_checksum(SAMPLE),
        source_url="https://mcc.nic.in/archive-ug/",
    )
    for field in (
        "source_id",
        "dataset",
        "effective_year",
        "publication_version",
        "contract_version",
        "source_url",
        "file_checksum",
        "source_file_id",
        "parser_version",
        "retrieval_timestamp",
    ):
        assert getattr(meta, field) not in (None, ""), field
    assert meta.source_id == "mcc"
    assert meta.dataset == "allotments"
    assert meta.effective_year == 2025
    assert meta.publication_version == "Round 3"
    assert meta.contract_version == "1.1.0"
