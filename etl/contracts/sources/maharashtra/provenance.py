"""Maharashtra provenance: deterministic file identity and SHA-256 checksums.

Two files from MAH CET Cell describing the same cohort must hash to the same
checksum so re-ingestion can be detected (idempotency) and audit trails can
prove no rows were silently dropped. The ``source_file_id`` is derived
deterministically from the checksum so the same bytes always produce the same
identity, regardless of when ingestion ran.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from etl.contracts.canonical import SourceMetadata
from etl.contracts.canonical.checksum import compute_checksum, compute_file_checksum

PARSER_VERSION = "mah_etl_v1"


def file_checksum(path: str | Path) -> str:
    """SHA-256 hex digest of a file's bytes."""
    return compute_file_checksum(str(path))


def bytes_checksum(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes."""
    return compute_checksum(data)


def build_source_file_id(checksum: str, source_id: str, dataset: str, effective_year: int) -> str:
    """Deterministic identifier for an ingested source file.

    Same (checksum, source, dataset, year) -> same id, so the file registry
    can recognise a re-submitted file without storing the bytes.
    """
    return f"{source_id}_{dataset}_{effective_year}_{checksum[:12]}"


def build_metadata(
    source_id: str,
    authority: str,
    dataset: str,
    effective_year: int,
    publication_version: str,
    contract_version: str,
    checksum: str,
    parser_version: str = PARSER_VERSION,
    source_file_id: str | None = None,
    source_url: str | None = None,
) -> SourceMetadata:
    """Assemble provenance metadata for a batch of canonical records."""
    if source_file_id is None:
        source_file_id = build_source_file_id(checksum, source_id, dataset, effective_year)
    return SourceMetadata(
        source_id=source_id,
        authority=authority,
        dataset=dataset,
        effective_year=effective_year,
        publication_version=publication_version,
        contract_version=contract_version,
        retrieval_timestamp=datetime.now(UTC).isoformat(),
        source_file_id=source_file_id,
        file_checksum=checksum,
        parser_version=parser_version,
        source_url=source_url,
    )


def now_iso() -> str:
    """Current UTC timestamp in ISO-8601."""
    return datetime.now(UTC).isoformat()
