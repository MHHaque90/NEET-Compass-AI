"""Karnataka KEA source contract module.

Exports the contracts, mappings, parsers, adapters, provenance and pipeline
for the Karnataka KEA NEET UG state counselling data source.
"""

from etl.contracts.sources.karnataka.adapters import (
    KarnatakaAllotmentsAdapter,
    KarnatakaSeatMatrixAdapter,
)
from etl.contracts.sources.karnataka.contracts import (
    allotments_2026_contract,
    seat_matrix_2026_contract,
)
from etl.contracts.sources.karnataka.mappings import (
    normalize_karnataka_category,
    normalize_karnataka_quota,
)
from etl.contracts.sources.karnataka.parsers import clean, parse_csv
from etl.contracts.sources.karnataka.pipeline import (
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
from etl.contracts.sources.karnataka.provenance import (
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
    "KarnatakaAllotmentsAdapter",
    "KarnatakaSeatMatrixAdapter",
    "Loader",
    "PipelineResult",
    "allotment_loader",
    "allotments_2026_contract",
    "build_metadata",
    "build_source_file_id",
    "bytes_checksum",
    "clean",
    "file_checksum",
    "ingest_allotments",
    "ingest_seat_matrix",
    "normalize_karnataka_category",
    "normalize_karnataka_quota",
    "parse_csv",
    "seat_matrix_2026_contract",
    "seat_matrix_loader",
]
