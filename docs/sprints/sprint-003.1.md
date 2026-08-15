# Sprint Report: Sprint 3.1

## Sprint Goal

Stand up the first official-data ETL pipeline for the NEET Compass AI
backend: a contract-driven ingestion path for Medical Counselling Committee
(MCC) 2025 data, anchored on the PII-free seat-matrix dataset and including
the allotment-result schema with candidate-PII explicitly excluded.

## Deliverables

1. **Source contract framework** — `etl/contracts/sources/mcc/` package that
   reuses the existing `SourceContract` / `SourceAdapter` / `ContractValidator`
   architecture (`etl.contracts`).
   - `contracts.py` — versioned `SourceContract` for `seat_matrix` and
     `allotments` (contract version `1.1.0`, effective year `2025`).
   - `mappings.py` — MCC abbreviation to canonical `quota_id` / `category_id`
     maps for both the seat-matrix and allotment vocabularies.
   - `parsers.py` — UTF-8 (BOM)-tolerant CSV parser + a `pdfplumber`-backed
     seat-matrix PDF table extractor.
   - `adapters.py` — `MCCSeatMatrixAdapter` and `MCCAllotmentsAdapter`.
   - `download.py` — retry-capable `urllib` downloader (stdlib only).
   - `provenance.py` — deterministic SHA-256 checksums and `source_file_id`.
   - `pipeline.py` — orchestrator plus `FileRegistry` / `Loader` ports with
     in-memory fakes.
2. **Tests** — 46 unit tests under `tests/unit/etl/contracts/sources/mcc/`,
   grounded in the real MCC 2025 PDF tables and abbreviation keys.
3. **Configuration** — `pyproject.toml` gains `.` on `pythonpath` (so the
   repo-root `etl` package is importable from tests) and a `tests.*` mypy
   override mirroring the existing test-suite overrides.
4. **Documentation** — this report and `docs/adr/0011-mcc-contract-pilot.md`.

## Architecture Decisions

### Canonical identifiers are strings, not enums

The canonical `SeatMatrix` / `Allotment` dataclasses already declare
`quota_id` and `category_id` as strings. The MCC source, however, uses two
different abbreviation schemes for the same concept (`OP` vs `GN` for open
seat; `PH` vs `PwD` for disability). The mappers in `mappings.py` collapse
both onto one canonical vocabulary (`gn`, `bc`, `ew`, `sc`, `st` with a
`_pwd` suffix) so a single downstream model works for both datasets. Mapping
the canonical strings onto the `app.domain.enums` (`Category`, `QuotaType`)
happens at the ORM boundary in Sprint 3.2; that boundary is the one place the
enum vocabulary is enforced, not the source contract.

### Candidate PII is excluded by contract, not by after-the-fact scrubbing

The `allotments` contract declares exactly nine non-PII columns as expected.
The adapter emits only canonical fields and additionally refuses (as a
pipeline note) any source column matching the
`ALLOTMENT_PRIVACY_BLOCKLIST` (`Candidate Name`, `Percentile`, `Aadhaar`,
`Contact No`, ...). A regression test asserts no PII key ever appears in a
loaded record.

### Persistence is a port, not a hard dependency

`etl.contracts.sources.mcc.pipeline` defines `FileRegistry` and `Loader` as
`Protocol`s with `InMemory*` implementations, so ingestion is fully
testable end-to-end (including idempotency) without PostgreSQL. The
production SQLAlchemy loader is wired in by the host application in
Sprint 3.2.

## Pipeline Flow

```
MCC source file (PDF table / CSV)
        |  parsers.parse_csv  |  parsers.extract_seat_matrix_rows
        v
   raw rows (external columns)
        |  ContractValidator.validate_columns  (STRICT/COMPATIBLE)
        v
   MCC*Adapter.transform  ->  canonical records (+ provenance metadata)
        |  ContractValidator.validate_records  (type, range, enum, unique)
        v
   Loader.upsert  (dedup by composite key)   +   FileRegistry.register(checksum)
```

Re-running the same file: `FileRegistry.has_checksum` returns true and the
pipeline short-circuits with `file_ingested=False`. Within a file, the
`unique_key` validator rejects duplicate composite keys (`DUPLICATE_RECORD`).

## Key Outcomes

| Metric | Baseline | Sprint 3.1 |
| --- | --- | --- |
| Contract-protected data sources | 0 | 2 (`seat_matrix`, `allotments`) |
| Adapter/transform tests | 0 | 10 |
| Pipeline idempotency tests | 0 | 5 |
| New code mypy (strict) | clean | clean |
| New code ruff | clean | clean |
| Real-PDF extraction test | n/a | passing (env-gated) |

## Risks & Mitigations

1. **Database integration is not exercised here** — PostgreSQL is unavailable
   in this environment (`ModuleNotFoundError: No module named 'psycopg2'` /
   service not running). The persistence boundary is therefore proven with
   in-memory fakes against the `Loader` / `FileRegistry` ports. A real
   PostgreSQL round-trip is a Sprint 3.2 milestone (see ADR-0011).
2. **The allotment PDF I inspected is a human-readable report**, not the
   machine-readable allotment CSV. The allotment contract columns are the
   well-known MCC allotment-CSV schema; the PII-exclusion behaviour is tested
   directly on the adapter and is therefore independent of report-vs-CSV
   layout.
3. **`pdfplumber` is an optional dependency** of the parser — imported lazily,
   so `etl` remains importable in minimal environments. The real-PDF test is
   gated behind the `MCC_SAMPLE_SEATMATRIX_PDF` env var / fixture and skips in
   CI when unset.
4. **Realtime download is only exercised via `file://`** — no network calls in
   the test suite. Production HTTPS downloads (with the MCC user-agent and
   retry/backoff) remain unproven here.

## Sprint Retrospective

The contract layer paid off immediately: the seat-matrix and allotment
adapters share one `ContractValidator` and one pipeline, and the PII guard is a
single blocklist check rather than ad-hoc scrubbing. The only friction was
keeping the `etl` package importable from `tests/` (repo-root `pythonpath`),
which a one-line `pyproject.toml` change resolved.
