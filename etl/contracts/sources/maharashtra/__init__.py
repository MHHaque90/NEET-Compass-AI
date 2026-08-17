"""Maharashtra (MAH CET Cell) source contracts, adapters, and ingestion pipeline.

Sprint 3.2 implements the Maharashtra state-counselling pilot for the
PII-free seat-matrix and allotment datasets. Both flow through the
contract -> adapter -> validator -> pipeline machinery declared in
``etl.contracts``.
"""

from etl.contracts.sources.maharashtra.adapters import (
    MaharashtraAllotmentsAdapter,
    MaharashtraSeatMatrixAdapter,
)
from etl.contracts.sources.maharashtra.contracts import (
    allotments_2026_contract,
    seat_matrix_2026_contract,
)
from etl.contracts.sources.maharashtra.parsers import clean, parse_csv
from etl.contracts.sources.maharashtra.pipeline import (
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
from etl.contracts.sources.maharashtra.provenance import (
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
    "MaharashtraAllotmentsAdapter",
    "MaharashtraSeatMatrixAdapter",
    "PipelineResult",
    "allotment_loader",
    "allotments_2026_contract",
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
    "seat_matrix_2026_contract",
    "seat_matrix_loader",
]
