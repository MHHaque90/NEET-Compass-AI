"""Data sources for ETL pipelines.

Each source is an adapter over a raw data origin. The actual scraping/parsing
of MCC and state cut-off releases is intentionally left as the first real
implementation task (Phase 2); the adapters below establish the contract and
handle the two most common file formats.
"""

from app.infrastructure.etl.sources.csv_source import CSVSource
from app.infrastructure.etl.sources.excel_source import ExcelSource

__all__ = ["CSVSource", "ExcelSource"]
