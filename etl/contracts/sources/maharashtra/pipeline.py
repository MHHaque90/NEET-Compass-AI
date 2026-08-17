"""Maharashtra ingestion pipelines: contract -> validate -> transform -> persist.

Persistence is abstracted behind a ``Loader`` protocol (upsert by composite
key, idempotent) and file-level deduplication behind a ``FileRegistry``
protocol. Both have in-memory implementations so the pipeline is fully
exercisable in unit tests without PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from etl.contracts.adapters import SourceAdapter
from etl.contracts.base import SourceContract
from etl.contracts.canonical import SourceMetadata
from etl.contracts.errors import ValidationError
from etl.contracts.sources.maharashtra.adapters import (
    MaharashtraAllotmentsAdapter,
    MaharashtraSeatMatrixAdapter,
)
from etl.contracts.sources.maharashtra.contracts import (
    allotments_2026_contract,
    seat_matrix_2026_contract,
)
from etl.contracts.sources.maharashtra.parsers import parse_csv
from etl.contracts.sources.maharashtra.provenance import (
    build_metadata,
    build_source_file_id,
    file_checksum,
)
from etl.contracts.validators import ContractValidator, ValidationMode

_SEAT_MATRIX_KEYS: tuple[str, ...] = (
    "college_id",
    "course_id",
    "quota_id",
    "category_id",
    "effective_year",
)
_ALLOTMENT_KEYS: tuple[str, ...] = (
    "college_id",
    "course_id",
    "quota_id",
    "category_id",
    "round_id",
    "rank",
)


@dataclass
class PipelineResult:
    """Outcome of a single file ingestion."""

    records: list[dict[str, Any]] = field(default_factory=list)
    metadata: SourceMetadata | None = None
    errors: list[ValidationError] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    records_transformed: int = 0
    records_skipped: int = 0
    file_ingested: bool = False


class FileRegistry(Protocol):
    """Port for detecting already-ingested source files (by checksum)."""

    def has_checksum(self, checksum: str) -> bool: ...

    def register(self, checksum: str, source_file_id: str) -> None: ...


class Loader(Protocol):
    """Port for upserting canonical records into a store."""

    def upsert(self, record: dict[str, Any]) -> bool: ...

    def count(self) -> int: ...


@dataclass
class InMemoryFileRegistry(FileRegistry):
    """In-memory checksum registry (used in tests; production swaps Postgres)."""

    _seen: set[str] = field(default_factory=set)

    def has_checksum(self, checksum: str) -> bool:
        return checksum in self._seen

    def register(self, checksum: str, source_file_id: str) -> None:
        self._seen.add(checksum)


@dataclass
class InMemoryLoader(Loader):
    """In-memory upsert store keyed by a composite canonical key.

    ``upsert`` returns ``True`` when a row was newly inserted and ``False``
    when an existing row (same composite key) was merged/updated, proving
    ingestion-level idempotency without a database.
    """

    key_fields: tuple[str, ...]
    _store: dict[tuple[Any, ...], dict[str, Any]] = field(default_factory=dict)

    def _key(self, record: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(record.get(name) for name in self.key_fields)

    def upsert(self, record: dict[str, Any]) -> bool:
        key = self._key(record)
        if key in self._store:
            self._store[key].update(record)
            return False
        self._store[key] = dict(record)
        return True

    def count(self) -> int:
        return len(self._store)

    def all(self) -> list[dict[str, Any]]:
        return list(self._store.values())


def _ingest(
    path: str | Path,
    registry: FileRegistry,
    loader: Loader,
    contract: SourceContract,
    adapter: SourceAdapter,
    source_url: str | None = None,
) -> PipelineResult:
    """Run the full ingestion pipeline for one CSV source file."""
    checksum = file_checksum(path)
    validator = ContractValidator(contract, ValidationMode.COMPATIBLE)
    source_file_id = build_source_file_id(
        checksum, contract.source_id, contract.dataset, contract.effective_year
    )
    metadata = build_metadata(
        source_id=contract.source_id,
        authority=contract.authority,
        dataset=contract.dataset,
        effective_year=contract.effective_year,
        publication_version=contract.publication_version,
        contract_version=str(contract.contract_version),
        checksum=checksum,
        source_file_id=source_file_id,
        source_url=source_url,
    )

    if registry.has_checksum(checksum):
        skipped = len(parse_csv(path))
        return PipelineResult(metadata=metadata, records_skipped=skipped, file_ingested=False)

    rows = parse_csv(path)
    columns = list(rows[0].keys()) if rows else []
    column_errors = validator.validate_columns(columns, contract.source_id, contract.dataset)

    source_errors = adapter.validate_source(rows, contract)

    adapter_result = adapter.transform(rows, contract, metadata)
    records = adapter_result.records
    record_errors = validator.validate_records(
        records,
        contract.source_id,
        contract.dataset,
        contract.effective_year,
        contract.publication_version,
    )

    bad_rows = {error.row for error in record_errors.errors if error.row is not None}
    valid_records: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if index in bad_rows:
            continue
        loader.upsert(record)
        valid_records.append(record)

    registry.register(checksum, source_file_id)

    return PipelineResult(
        records=valid_records,
        metadata=metadata,
        errors=list(column_errors) + list(record_errors.errors),
        notes=source_errors,
        records_transformed=len(valid_records),
        records_skipped=adapter_result.records_skipped + len(bad_rows),
        file_ingested=True,
    )


def ingest_seat_matrix(
    path: str | Path,
    registry: FileRegistry,
    loader: Loader,
    *,
    source_url: str | None = None,
) -> PipelineResult:
    """Ingest a Maharashtra seat-matrix CSV through the full pipeline."""
    return _ingest(
        path,
        registry,
        loader,
        seat_matrix_2026_contract(),
        MaharashtraSeatMatrixAdapter(),
        source_url=source_url,
    )


def ingest_allotments(
    path: str | Path,
    registry: FileRegistry,
    loader: Loader,
    *,
    source_url: str | None = None,
) -> PipelineResult:
    """Ingest a Maharashtra allotment CSV through the full pipeline."""
    return _ingest(
        path,
        registry,
        loader,
        allotments_2026_contract(),
        MaharashtraAllotmentsAdapter(),
        source_url=source_url,
    )


def seat_matrix_loader() -> InMemoryLoader:
    """Factory for an in-memory seat-matrix loader (composite key)."""
    return InMemoryLoader(key_fields=_SEAT_MATRIX_KEYS)


def allotment_loader() -> InMemoryLoader:
    """Factory for an in-memory allotment loader (composite key)."""
    return InMemoryLoader(key_fields=_ALLOTMENT_KEYS)


__all__ = [
    "FileRegistry",
    "InMemoryFileRegistry",
    "InMemoryLoader",
    "Loader",
    "PipelineResult",
    "allotment_loader",
    "ingest_allotments",
    "ingest_seat_matrix",
    "seat_matrix_loader",
]
