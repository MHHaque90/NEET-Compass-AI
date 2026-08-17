"""Uttar Pradesh NEET UG source contract module.

Exports the contracts, mappings, parsers, adapters, provenance and pipeline
for the Uttar Pradesh NEET UG state counselling data source.
"""

from etl.contracts.sources.uttar_pradesh.adapters import (
    UttarPradeshAllotmentsAdapter,
    UttarPradeshSeatMatrixAdapter,
)
from etl.contracts.sources.uttar_pradesh.contracts import (
    allotments_2026_contract,
    seat_matrix_2026_contract,
)
from etl.contracts.sources.uttar_pradesh.mappings import (
    normalize_up_category,
    normalize_up_quota,
)
from etl.contracts.sources.uttar_pradesh.parsers import clean, parse_csv
from etl.contracts.sources.uttar_pradesh.pipeline import (
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
from etl.contracts.sources.uttar_pradesh.provenance import (
    PARSER_VERSION,
    build_metadata,
    build_source_file_id,
    bytes_checksum,
    file_checksum,
)

__all__ = [
    "PARSER_VERSION",
    "FileRegistry",
    "InMemoryFileRegistry",
    "InMemoryLoader",
    "Loader",
    "PipelineResult",
    "UttarPradeshAllotmentsAdapter",
    "UttarPradeshSeatMatrixAdapter",
    "allotment_loader",
    "allotments_2026_contract",
    "build_metadata",
    "build_source_file_id",
    "bytes_checksum",
    "clean",
    "file_checksum",
    "ingest_allotments",
    "ingest_seat_matrix",
    "normalize_up_category",
    "normalize_up_quota",
    "parse_csv",
    "seat_matrix_2026_contract",
    "seat_matrix_loader",
]
