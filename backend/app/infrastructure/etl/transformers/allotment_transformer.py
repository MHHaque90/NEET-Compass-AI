"""Transformer for allotment/cut-off data.

Published cut-off sheets use different header names every year and every
state. The transformer is configured with a column map and normalizes raw
rows to the canonical keys understood by ``AllotmentRow``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import ClassVar

from app.infrastructure.etl.base import RawRow, Transformer


@dataclass(frozen=True)
class AllotmentTransformer(Transformer):
    """Maps raw columns -> canonical columns and coerces types.

    Args:
        column_map: {raw header: canonical header}. Unknown raw columns are
            ignored; missing canonical columns cause a row to be skipped
            (counted by the pipeline logger).
        year: counselling year to stamp onto rows that lack a year column.

    """

    column_map: Mapping[str, str]
    year: int

    _CANONICAL: ClassVar[frozenset[str]] = frozenset(
        {
            "college_code",
            "course",
            "counselling_year",
            "round_number",
            "quota_type",
            "category",
            "gender",
            "is_pwd",
            "opening_rank",
            "closing_rank",
            "opening_marks",
            "closing_marks",
        }
    )

    def transform(self, rows: Iterable[RawRow]) -> Iterable[RawRow]:
        for raw in rows:
            normalized = self._normalize(raw)
            if normalized is not None:
                yield normalized

    def _normalize(self, raw: RawRow) -> RawRow | None:
        if not any(str(value).strip() for value in raw.values()):
            return None  # blank trailer row

        out: dict[str, object] = {}
        for raw_name, canonical in self.column_map.items():
            value = raw.get(raw_name)
            if value is None:
                continue
            coerced = self._coerce(canonical, value)
            if coerced is None:
                continue
            out[canonical] = coerced

        if "counselling_year" not in out:
            out["counselling_year"] = self.year

        # A row without ranks is a footnote, not data.
        if not {"opening_rank", "closing_rank"}.issubset(out):
            return None

        return out

    @staticmethod
    def _coerce(canonical: str, value: object) -> object:
        if canonical in {"opening_rank", "closing_rank", "round_number", "counselling_year"}:
            text = str(value).strip()
            return int(text.replace(",", "")) if text else None
        if canonical in {"opening_marks", "closing_marks"}:
            text = str(value).strip()
            return float(text) if text else None
        if canonical in {"course", "quota_type", "category", "gender"}:
            return str(value).strip().upper()
        if canonical == "is_pwd":
            return str(value).strip().upper() in {"Y", "YES", "1", "TRUE", "PWD"}
        return value
