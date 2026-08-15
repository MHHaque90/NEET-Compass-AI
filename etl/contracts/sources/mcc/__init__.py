"""MCC source contracts, adapters, and ingestion pipeline.

Sprint 3.1 implements the MCC pilot for the two PII-free, high-priority
datasets: ``seat_matrix`` (sanctioned seats) and ``allotments`` (per-round
rank/score/seat counts). Both flow through the contract -> adapter ->
validator -> pipeline machinery declared in ``etl.contracts``.
"""

from etl.contracts.sources.mcc.adapters import (
    MCCAllotmentsAdapter,
    MCCSeatMatrixAdapter,
)
from etl.contracts.sources.mcc.contracts import (
    allotments_2025_contract,
    seat_matrix_2025_contract,
)
from etl.contracts.sources.mcc.download import download_file
from etl.contracts.sources.mcc.parsers import extract_seat_matrix_rows, parse_csv
from etl.contracts.sources.mcc.pipeline import (
    FileRegistry,
    InMemoryFileRegistry,
    InMemoryLoader,
    Loader,
    PipelineResult,
    allotment_loader,
    ingest_allotments,
    ingest_seat_matrix,
    seat_matrix_loader,
)
from etl.contracts.sources.mcc.provenance import (
    build_metadata,
    build_source_file_id,
    bytes_checksum,
    file_checksum,
    now_iso,
)

__all__ = [
    "FileRegistry",
    "InMemoryFileRegistry",
    "InMemoryLoader",
    "Loader",
    "MCCAllotmentsAdapter",
    "MCCSeatMatrixAdapter",
    "PipelineResult",
    "allotment_loader",
    "allotments_2025_contract",
    "build_metadata",
    "build_source_file_id",
    "bytes_checksum",
    "download_file",
    "extract_seat_matrix_rows",
    "file_checksum",
    "ingest_allotments",
    "ingest_seat_matrix",
    "now_iso",
    "parse_csv",
    "seat_matrix_2025_contract",
    "seat_matrix_loader",
]
