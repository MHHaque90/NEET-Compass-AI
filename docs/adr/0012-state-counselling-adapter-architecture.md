# ADR-0012: State Counselling Adapter Architecture

## Status
Proposed

## Context
Sprint 3.2 requires building a state counselling data ingestion framework that
can support individual Indian state/UT counselling authorities. The framework must
preserve the existing clean/hexagonal architecture and reuse the existing
contract architecture under `etl/contracts/`.

## Decision
Build a **contract-driven adapter** for each state, following the pattern
established by the MCC (Medical Counselling Committee) pilot in Sprint 3.1.

Each state adapter module under `etl/contracts/sources/<state>/` will contain:

1. **contracts.py** — SourceContract definition with field_mapping,
   validation_rules, expected_columns, required_columns
2. **mappings.py** — Abbreviation normalisation helpers (category, quota)
3. **adapters.py** — SourceAdapter subclass transforming external rows -> canonical
   records
4. **parsers.py** — CSV/HTML parsers producing row dicts keyed by external names
5. **provenance.py** — SHA-256 checksums, source_file_id, metadata assembly
6. **pipeline.py** — Ingestion pipeline orchestration (_ingest, registry, loader)

The Maharashtra pilot (``etl/contracts/sources/maharashtra/``) is the first
instance of this pattern. Future states follow the same module structure but
with state-specific normalisation logic.

## Alternative considered
**Direct database ingestion** — bypassing the contract layer to load source data
directly into PostgreSQL. Rejected because it violates the non-negotiable rule
that "External source data MUST NOT directly write to PostgreSQL" and removes
the contract validation, provenance, and idempotency guarantees.

## Consequences
- Reuse of MCC-provenance infrastructure (SHA-256, source_file_id, checksum)
- State-specific logic remains state-specific (mappings/adapters are not shared)
- New source addition requires: contracts.py, mappings.py, adapters.py, parsers.py,
  provenance.py, pipeline.py — following the established module structure
- Contract versioning (``1.0.0`` for pilot) provides backward compatibility
  when schema evolves