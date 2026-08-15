"""Tests for MCC CSV and PDF-table parsers."""

from __future__ import annotations

import csv

from etl.contracts.sources.mcc.parsers import (
    _find_header,
    _is_header_row,
    _text,
    extract_seat_matrix_rows,
    parse_csv,
)


def _write_csv(path, rows: list[list[str]], delimiter: str = ",") -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle, delimiter=delimiter).writerows(rows)


def test_parse_csv_strips_bom_and_whitespace(tmp_path) -> None:
    path = tmp_path / "x.csv"
    _write_csv(path, [["a", "b"], [" 1 ", " 2 "]])
    rows = parse_csv(path)
    assert rows == [{"a": "1", "b": "2"}]


def test_parse_csv_empty_file(tmp_path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    assert parse_csv(path) == []


def test_parse_csv_tab_delimited(tmp_path) -> None:
    path = tmp_path / "t.tsv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        handle.write("a\tb\n1\t2\n")
    rows = parse_csv(path, delimiter="\t")
    assert rows == [{"a": "1", "b": "2"}]


def test_parse_csv_handles_embedded_commas(tmp_path) -> None:
    path = tmp_path / "x.csv"
    _write_csv(
        path,
        [["name", "addr"], ["AIIMS", "Mangalagiri, Guntur, AP"]],
    )
    rows = parse_csv(path)
    assert rows == [{"name": "AIIMS", "addr": "Mangalagiri, Guntur, AP"}]


def test_header_detection_helpers() -> None:
    assert _is_header_row(
        ["StateName", "InstituteType", "Institute", "Quota", "Branch", "Category", "TotalSeats"]
    )
    assert not _is_header_row(["some", "other", "row"])
    with_title = [
        ["FINAL SEAT MATRIX (title)", "", "", "", "", "", ""],
        ["StateName", "InstituteType", "Institute", "Quota", "Branch", "Category", "TotalSeats"],
        ["Andhra Pradesh", "Govt", "X (123)", "All India", "MBBS (MBBS)", "BC NO", "5"],
    ]
    assert _find_header(with_title) == 1
    assert _text(None) == ""
    assert _text("  a b \n") == "a b"


def test_extract_real_pdf_tables(sample_seat_matrix_pdf) -> None:
    # Scope to the first page so the test stays fast locally; the fixture
    # skips entirely when MCC_SAMPLE_SEATMATRIX_PDF is unset (CI).
    rows = extract_seat_matrix_rows(sample_seat_matrix_pdf, page_numbers=[0])
    assert len(rows) >= 10
    assert all("TotalSeats" in row and "Institute" in row for row in rows[:10])
    assert rows[0]["TotalSeats"].isdigit()
