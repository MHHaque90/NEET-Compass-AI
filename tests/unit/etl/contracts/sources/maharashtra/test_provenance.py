"""Tests for Maharashtra provenance: checksums, source-file id, metadata assembly."""

from __future__ import annotations

from etl.contracts.sources.maharashtra.provenance import (
    PARSER_VERSION,
    build_metadata,
    build_source_file_id,
    bytes_checksum,
    file_checksum,
)

SAMPLE = b"StateName,Institute\nMaharashtra,X\n"


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
    assert build_source_file_id(checksum, "mcc_state_maharashtra", "seat_matrix", 2026) == (
        build_source_file_id(checksum, "mcc_state_maharashtra", "seat_matrix", 2026)
    )
    other = build_source_file_id(bytes_checksum(b"other"), "mcc_state_maharashtra", "seat_matrix", 2026)
    assert other != build_source_file_id(checksum, "mcc_state_maharashtra", "seat_matrix", 2026)
    assert build_source_file_id(checksum, "mcc_state_maharashtra", "seat_matrix", 2026).startswith(
        "mcc_state_maharashtra_seat_matrix_2026_"
    )


def test_build_metadata_populates_provenance() -> None:
    checksum = bytes_checksum(SAMPLE)
    meta = build_metadata(
        source_id="mcc_state_maharashtra",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="seat_matrix",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        checksum=checksum,
    )
    assert meta.source_id == "mcc_state_maharashtra"
    assert meta.file_checksum == checksum
    assert meta.parser_version == PARSER_VERSION
    assert meta.effective_year == 2026
    assert meta.source_file_id == build_source_file_id(checksum, "mcc_state_maharashtra", "seat_matrix", 2026)
    assert meta.publication_version == "Round 1"


def test_build_metadata_carries_source_url() -> None:
    checksum = bytes_checksum(SAMPLE)
    meta = build_metadata(
        source_id="mcc_state_maharashtra",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="allotments",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        checksum=checksum,
        source_url="https://cetcell.mahacet.org/",
    )
    assert meta.source_url == "https://cetcell.mahacet.org/"


def test_provenance_taxonomy_is_complete() -> None:
    """Every real source record carries the full provenance taxonomy."""
    meta = build_metadata(
        source_id="mcc_state_maharashtra",
        authority="State Common Entrance Test Cell, Maharashtra",
        dataset="allotments",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        checksum=bytes_checksum(SAMPLE),
        source_url="https://cetcell.mahacet.org/",
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
    assert meta.source_id == "mcc_state_maharashtra"
    assert meta.dataset == "allotments"
    assert meta.effective_year == 2026
    assert meta.publication_version == "Round 1"
    assert meta.contract_version == "1.0.0"
