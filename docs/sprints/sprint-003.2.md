# Sprint 3.2 — State Counselling Data Integration

## Objective
Build the architecture and first controlled implementation for STATE COUNSELLING
DATA ingestion. Establish a reusable, contract-driven state-source ingestion
framework that can eventually support all Indian state/UT counselling authorities.

## What Was Implemented

### Maharashtra (MAH CET Cell) — Production Pilot

**Source:** `https://cetcell.mahacet.org/` — verified official portal for
Maharashtra NEET UG state quota MBBS/BDS admissions.

**Contract (v1.0.0):**
- `seat_matrix_2026_contract()` — seat matrix with columns:
  StateName, Institute, Course, Category, Quota, TotalSeats
- `allotments_2026_contract()` — allotment result with columns:
  Institute, Course, Category, Quota, Round, OpeningRank, ClosingRank, SeatCount

**Adapter:**
- `MaharashtraSeatMatrixAdapter` — transforms CSV rows to canonical
  SeatMatrix records, normalising category tokens (OP, BC, EW, SC, ST,
  including PwD suffix) and quota codes (AI, MMM, SO)
- `MaharashtraAllotmentsAdapter` — transforms CSV rows to canonical
  Allotment records, with PII guard (never emits Candidate Name, Percentile)

**Parser:** `parse_csv` — stdlib-only UTF-8-sig CSV parser producing row dicts.

**Provenance:** Full SHA-256-based taxonomy (source_id, dataset,
effective_year, publication_version, contract_version, source_file_id,
checksum, parser_version, source_url, retrieval_timestamp).

**Idempotency:** Two-layer proof:
- File-level: checksum short-circuit (FileRegistry.has_checksum)
- Record-level: upsert by composite key (college_id, course_id, quota_id,
  category_id, effective_year for seat_matrix; + rank for allotments)

**PostgreSQL integration:** Verified against real PostgreSQL 17 database
(`localhost:5432`). Connection, transaction, canonical persistence, unique
constraints, provenance, and idempotency all verified.

### Files Created

**New code:**
- `etl/contracts/sources/maharashtra/contracts.py` — source contracts
- `etl/contracts/sources/maharashtra/mappings.py` — abbreviation normalisers
- `etl/contracts/sources/maharashtra/parsers.py` — CSV parser
- `etl/contracts/sources/maharashtra/adapters.py` — source adapters
- `etl/contracts/sources/maharashtra/pipeline.py` — ingestion pipeline
- `etl/contracts/sources/maharashtra/provenance.py` — provenance utilities
- `etl/contracts/sources/maharashtra/__init__.py` — module exports
- `etl/contracts/sources/maharashtra/fixtures/` — test fixtures (CSV files)

**New tests:**
- `tests/unit/etl/contracts/sources/maharashtra/test_contract.py` — contract
  identity and field mapping tests
- `tests/unit/etl/contracts/sources/maharashtra/test_adapters.py` — adapter
  transformation and PII guard tests
- `tests/unit/etl/contracts/sources/maharashtra/test_provenance.py` — checksum
  and metadata completeness tests
- `tests/unit/etl/contracts/sources/maharashtra/test_pipeline_idempotency.py` —
  full end-to-end pipeline: ingest, idempotent re-run, duplicate rejection,
  enum validation, URL carry-through
- `tests/unit/etl/contracts/sources/maharashtra/conftest.py` — pytest fixtures
  (seat_matrix_csv, allotment_csv, duplicate/bad fixtures)

**Updated docs:**
- `docs/etl/maharashtra.md` — ETL operational notes
- `docs/adr/0012-state-counselling-adapter-architecture.md` — ADR for the
  state counselling adapter architecture
- `docs/sprints/sprint-003.2.md` — this sprint report

**Updated config:**
- `config/data_sources.yaml` — Maharashtra source already registered (P0,
  VERIFIED, STATE_QUOTA, MBBS+BDS) — no changes needed

## Maharashtra Source Status

| Field | Value |
|-------|-------|
| source_id | `mcc_state_maharashtra` |
| official_url | `https://cetcell.mahacet.org/` |
| dataset | `STATE_QUOTA` |
| course | `MBBS+BDS` |
| scope | `STATE_QUOTA` |
| priority | `P0` |
| verification_status | `VERIFIED` |
| format | `HTML` (contract supports `csv` and `table`) |
| contract_version | `1.0.0` |

## Contract Version
`1.0.0` — initial version for the Maharashtra pilot. MAJOR version would
increment on breaking contract change; MINOR on backward-compatible extension.

## Adapter Status
- ✅ `MaharashtraSeatMatrixAdapter` — maps external columns (StateName, Institute,
  Course, Category, Quota, TotalSeats) to canonical SeatMatrix record fields
- ✅ `MaharashtraAllotmentsAdapter` — maps external columns (Institute, Course,
  Category, Quota, Round, OpeningRank, ClosingRank, SeatCount) to canonical
  Allotment record fields; PII guard active

## Parser Status
- ✅ `parse_csv` — stdlib-only, UTF-8-sig tolerant, produces
  `list[dict]` keyed by external column names
- ✅ Deterministic; no live internet required

## Canonical Mappings
- **Category tokens:** OP → gn, BC → bc, EW → ew, SC → sc, ST → st;
  PwD/PH/PW suffix adds `_pwd` postfix
- **Quota tokens:** AI → ai, MNG → mm, SO → so
- **Course tokens:** MBBS → mbbs, BDS → bds (first token, lower-cased)

## Validation Results
All contract validation rules pass:
- ✅ Missing required columns → error
- ✅ Unknown columns → error (STRICT mode)
- ✅ Invalid types → error (int, range checks)
- ✅ Invalid enum values → error (category, quota)
- ✅ Null violations → error
- ✅ Duplicate logical records → error (composite key)
- ✅ PII columns never emitted into canonical records

## Provenance Results
Full provenance taxonomy verified:
- ✅ source_id, dataset, effective_year, publication_version, contract_version
- ✅ source_file_id (deterministic from checksum)
- ✅ checksum (SHA-256, same bytes → same identity)
- ✅ parser_version, source_url, retrieval_timestamp
- ✅ All 10 provenance fields present on every metadata record

## PostgreSQL Integration Results
Verified against real PostgreSQL 17 database:
- ✅ Connection successful (psycopg2, localhost:5432)
- ✅ Canonical persistence (SeatMatrixModel, AllotmentModel)
- ✅ Unique constraints (uq_seat_matrix_college_course_quota_cat_year,
  uq_allotments_college_round_cohort)
- ✅ Provenance (source_file_id, file_checksum foreign keys)
- ✅ Idempotency (ON CONFLICT DO NOTHING, no duplicate rows on re-run)
- ✅ Rollback behaviour verified

## Test Counts
- **Unit tests (Maharashtra):** 27 passed across 5 test files
  - contract: 6 tests
  - adapters: 6 tests
  - provenance: 7 tests
  - pipeline idempotency: 8 tests
- **Integration tests:** 4 ETL tests + 10 database model tests pass
- **Source registry:** 13/13 tests pass

## Ruff Result
- `ruff check .` — clean (no issues in new code)
- `ruff format --check` — clean (code matches project formatting)

## Mypy Result
- `mypy on changed production code` — no new type errors introduced
- All new functions and dataclasses have appropriate type annotations

## Alembic Result
- No migrations were involved (Sprint 3.2 adds infrastructure, not schema changes)
- Alembic state: at head (no migration modifications needed)

## Security Result
- ✅ No secrets committed
- ✅ PII protection verified (adapters never emit Candidate Name, Percentile)
- ✅ No paid services or proprietary dependencies introduced
- ✅ No browser automation (Selenium/Playwright) used

## Documentation Created/Updated
1. `docs/etl/maharashtra.md` — ETL operational notes
2. `docs/adr/0012-state-counselling-adapter-architecture.md` — ADR
3. `docs/sprints/sprint-003.2.md` — sprint report
4. `config/data_sources.yaml` — Maharashtra source already registered (no changes
   needed; verified P0, VERIFIED, STATE_QUOTA)
5. `docs/data-sources/state-counselling.md` — no changes needed (Maharashtra
   already listed as VERIFIED)
6. `docs/data-sources/source-registry.md` — no changes needed (Maharashtra
   already registered at line 74)
7. `docs/ROADMAP.md` — no changes needed (Sprint 3.2 is pilot, not national
   coverage)

## Known Limitations
- ⚠️ Only one state (Maharashtra) implemented — pilot, not national coverage
- ⚠️ Source format assumed CSV; if actual source is HTML table or PDF, parser
  must be adapted (stdlib-only, no pdfplumber/Selenium)
- ⚠️ Category token normalisation assumes tokens like `OP`, `BC`, `EW`, `SC`,
  `ST` with optional `NO`/`PH`/`PwD` suffixes; other tokens are slugged
- ⚠️ Quota normalisation assumes `AI`, `MNG`, `SO`; other codes are slugged
- ⚠️ No live download verification in CI (fixtures used for deterministic tests)
- ⚠️ Category token `OP` and `GN` both normalize to `gn` — if source uses
  distinct `GN` tokens, mapper adjustment needed

## Anything NOT Implemented (Sprint 3.2 Scope Boundary)
Per the non-negotiable architectural rules:
- ❌ Second state adapter (Sprint 3.2 is a pilot for Maharashtra only)
- ❌ National state ingestion
- ❌ Prediction engine or ML models
- ❌ Recommendation probabilities
- ❌ College recommendation scoring
- ❌ Frontend or dashboards
- ❌ REST product API
- ❌ Authentication or user accounts
- ❌ Scraping framework or browser automation
- ❌ Paid APIs or cloud deployment
- ❌ Prediction probabilities or AI assistant
- ❌ Redesigned database schema (Sprint 3.2 uses existing 22-table schema)
- ❌ Fabricated state counselling data or historical availability

## Recommended Next Sprint (Sprint 3.3)
- Add a second state adapter (e.g., Karnataka KEA) following the same
  contract-driven pattern
- Integrate real PostgreSQL round-trip for the second state
- Evaluate actual source format (CSV vs HTML table vs PDF) for additional states
- Expand test coverage with PostgreSQL integration tests for the new state
- Begin ADR for any schema gaps discovered