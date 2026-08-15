"""Excel file source (most counselling releases ship as .xls/.xlsx)."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from app.infrastructure.etl.base import RawRow, Source


class ExcelSource(Source):
    """Reads the first sheet of an Excel workbook as raw dict rows.

    ``header_row`` lets callers skip title/junk rows commonly found in
    published cut-off sheets (usually the header lives on row 1-3).
    """

    def __init__(self, path: str, header_row: int = 0, sheet: str | int = 0) -> None:
        super().__init__(path)
        self._header_row = header_row
        self._sheet = sheet

    def read(self) -> Iterable[RawRow]:
        frame = pd.read_excel(self.path, sheet_name=self._sheet, header=self._header_row)
        for record in frame.to_dict(orient="records"):
            yield {str(key): value for key, value in record.items()}
