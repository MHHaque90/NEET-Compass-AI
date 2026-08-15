"""Parsers that turn MCC source material into rows.

* ``parse_csv`` reads a UTF-8 (BOM-tolerant) CSV produced by MCC or an
  operator export into ``list[dict]`` with the *external* column names the
  contract expects.
* ``extract_seat_matrix_rows`` renders MCC seat-matrix PDF tables into the
  same row shape. pdfplumber is imported lazily so the module stays importable
  in minimal environments.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Sequence
from pathlib import Path

from etl.contracts.sources.mcc.contracts import SEAT_MATRIX_COLUMNS


def parse_csv(path: str | Path, delimiter: str = ",") -> list[dict[str, str]]:
    """Parse a CSV file into a list of row dictionaries.

    Tolerates a UTF-8 BOM (``utf-8-sig``) and strips surrounding whitespace
    from every cell. Returns an empty list for an empty file.
    """
    text = Path(path).read_text(encoding="utf-8-sig")
    if not text.strip():
        return []
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows: list[dict[str, str]] = []
    for raw in reader:
        row = {clean(k): clean(v) for k, v in raw.items() if k is not None}
        if row:
            rows.append(row)
    return rows


def clean(value: object) -> str:
    """Strip whitespace; normalise ``None`` to an empty string."""
    if value is None:
        return ""
    return str(value).strip()


def _is_header_row(cells: Sequence[str]) -> bool:
    """True if a table row carries the seat-matrix column headers."""
    normalised = [c.strip().lower() for c in cells if c]
    return "totalseats" in normalised or "statename" in normalised


def extract_seat_matrix_rows(
    pdf_path: str | Path, *, page_numbers: Sequence[int] | None = None
) -> list[dict[str, str]]:
    """Extract seat-matrix rows from an MCC PDF.

    Each MCC seat-matrix page contains one table whose first populated row is
    the header (``StateName``, ``InstituteType``, ``Institute``, ``Quota``,
    ``Branch``, ``Category``, ``TotalSeats``); the row above is a spanning
    title. This function returns one dict per data row, keyed by the header
    names, so downstream the rows look identical to ``parse_csv`` output.

    Raises:
        ImportError: if ``pdfplumber`` is not installed in the environment.

    """
    import pdfplumber

    rows: list[dict[str, str]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = (
            [pdf.pages[i] for i in page_numbers]
            if page_numbers is not None
            else pdf.pages
        )
        for page in pages:
            for table in page.find_tables():
                extracted = table.extract()
                header_idx = _find_header(extracted)
                if header_idx is None:
                    continue
                header = [_text(cell) for cell in extracted[header_idx]]
                for record in extracted[header_idx + 1 :]:
                    if not any(_text(cell) for cell in record):
                        continue
                    row = {
                        header[i]: _text(cell)
                        for i, cell in enumerate(record)
                        if i < len(header)
                    }
                    if row.get("Institute") and row.get("TotalSeats"):
                        rows.append(row)
    return rows


def _find_header(rows: Sequence[Sequence[str | None]]) -> int | None:
    """Index of the row that holds the seat-matrix column headers."""
    for idx, row in enumerate(rows):
        cells = [_text(c) for c in row]
        if _is_header_row(cells):
            return idx
    return None


def _text(cell: str | None) -> str:
    """Normalise a pdfplumber cell to a single-line string."""
    if cell is None:
        return ""
    return cell.strip().replace("\n", " ").replace("\r", " ")


# Re-export the canonical external column names so callers can validate the
# output of a fresh parse against the declared contract schema.
__all__ = ["SEAT_MATRIX_COLUMNS", "clean", "extract_seat_matrix_rows", "parse_csv"]
