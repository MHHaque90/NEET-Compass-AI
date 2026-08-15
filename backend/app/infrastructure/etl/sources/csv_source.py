"""CSV file source."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from app.infrastructure.etl.base import RawRow, Source


class CSVSource(Source):
    """Reads a UTF-8 CSV with a header row into raw dict rows."""

    def read(self) -> Iterable[RawRow]:
        with Path(self.path).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                yield dict(row)
