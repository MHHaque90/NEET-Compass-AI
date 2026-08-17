# ADR-0013: Karnataka KEA State Counselling Adapter Architecture

## Status
Implemented

## Context
Sprint 3.3 requires building a state counselling data ingestion framework for
the Karnataka KEA (Karnataka Examinations Authority) NEET UG counselling.
The framework must preserve the existing clean/hexagonal architecture and
reuse the existing contract architecture under `etl/contracts/`.

## Decision
Build a **contract-driven adapter** for Karnataka KEA, following the pattern
established by the Maharashtra pilot in Sprint 3.2 and the MCC pilot in
Sprint 3.1.

Each state adapter module under `etl/contracts/sources/karnataka/` will contain:

1. **contracts.py** — SourceContract definition with field_mapping,
   validation_rules, expected_columns, required_columns
2. **mappings.py** — Abbreviation normalisation helpers (category, quota)
3. **adapters.py** — SourceAdapter subclass transforming external rows -> canonical
   records
4. **parsers.py** — CSV/HTML parsers producing row dicts keyed by external names
5. **provenance.py** — SHA-256 checksums, source_file_id, metadata assembly
6. **pipeline.py** — Ingestion pipeline orchestration (_ingest, registry, loader)

The Maharashtra pilot (`etl/contracts/sources/maharashtra/`) is the first
instance of this pattern. Karnataka KEA follows the same module structure
but with state-specific normalisation logic.

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
- Contract versioning (`1.0.0` for pilot) provides backward compatibility
  when schema evolves

## Consequences
- Reuse of MCC-provenance infrastructure (SHA-256, source_file_id, checksum)
- State-specific logic remains state-specific (mappings/adapters are not shared)
- New source addition requires: contracts.py, mappings.py, adapters.py, parsers.py,
  provenance.py, pipeline.py — following the established module structure
- Contract versioning (`1.0.0` for pilot) provides backward compatibility
  when schema evolves