"""Factory for the allotment/cut-off ETL pipeline."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from sqlalchemy.orm import Session

from app.infrastructure.etl.base import Pipeline, Source
from app.infrastructure.etl.loaders.allotment_loader import AllotmentLoader
from app.infrastructure.etl.sources.csv_source import CSVSource
from app.infrastructure.etl.sources.excel_source import ExcelSource
from app.infrastructure.etl.transformers.allotment_transformer import AllotmentTransformer


def build_allotment_pipeline(
    *,
    source_type: str,
    path: str,
    year: int,
    column_map: Mapping[str, str],
    session_factory: Callable[[], Session],
    batch_size: int = 1000,
) -> Pipeline:
    """Build a pipeline that ingests one counselling year's cut-off data.

    Args:
        source_type: ``"excel"`` or ``"csv"``.
        path: absolute or relative path to the raw release file.
        year: NEET counselling year to stamp onto the data.
        column_map: {raw header -> canonical header} for ``AllotmentTransformer``.
        session_factory: SQLAlchemy session factory for the loader.
        batch_size: rows per loader batch (default 1000).

    """
    source: Source
    if source_type == "excel":
        source = ExcelSource(path)
    elif source_type == "csv":
        source = CSVSource(path)
    else:
        raise ValueError(f"Unsupported source_type: {source_type!r}")

    return Pipeline(
        name=f"allotments-{year}",
        source=source,
        transformer=AllotmentTransformer(column_map=column_map, year=year),
        loader=AllotmentLoader(session_factory=session_factory, batch_size=batch_size),
    )
