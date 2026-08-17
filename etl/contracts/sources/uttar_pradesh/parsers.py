"""Parsers that turn Uttar Pradesh source material into rows.

Provides ``parse_csv`` — a stdlib-only CSV parser (UTF-8-sig tolerant, whitespace-
stripped cells) that produces ``list[dict]`` keyed by the *external* column names
the Uttar Pradesh contract expects. This mirrors the shape used by the MCC
and Karnataka ``parse_csv`` so downstream the rows look identical to contract
validation.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path


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


__all__ = ["clean", "parse_csv"]
