# Karnataka KEA State Counselling ETL Pipeline

> Sprint 3.3. Contract-driven state-counselling ingestion path for the
> Karnataka KEA (Karnataka Examinations Authority) NEET UG counselling.

## Pipeline shape
```
Karnataka KEA source file (CSV)
        |  parsers.parse_csv
        v
   raw rows (external columns)
        |  ContractValidator.validate_columns  (STRICT/COMPATIBLE)
        v
Karnataka KEA*Adapter.transform  ->  canonical records (+ provenance metadata)
        |  ContractValidator.validate_records  (type, range, enum, unique)
        v
   Loader.upsert  (dedup by composite key)   +   FileRegistry.register(checksum)
```

## Official URLs (from `config/data_sources.yaml`)

| Registry ID | URL | Status (2026-08-12) |
|-------------|-----|----------------------|
| `mcc_state_karnataka` | https://cetonline.karnataka.gov.in/kea/ | VERIFIED, live (HTTP 200, text/html on first contact) |

Only these URLs are verified in the registry. Individual deep-link file URLs
were not separately verified and must not be used as trusted links yet.

## Live download reality (Sprint 3.3)

The controlled live check found:

1. **First contact:** GET to `cetonline.karnataka.gov.in/kea` returned **HTTP 200, `text/html`**
   — the page is the live official authority page, reachable from this network.
2. **Automated full download:** repeat GETs from the same session were **not**
   blocked by bot protection (unlike the MCC experience), but the pipeline
   contracts are designed so that any file handed to them is validated regardless
   of download source — the contract framework is unaffected by download
   availability.

Workshet for a future interactive download: after retrieving a file, run it
through the pipeline and record: `url, checksum (sha256), size, content_type,
retrieval_timestamp`.

## Network discipline for tests

* No test in the suite performs a network call; CSV fixtures use `file://`.
* The pipeline contracts validate whatever file is handed to them — they are
  agnostic to download method.

## Contract version

`1.0.0` — initial version for the Karnataka KEA pilot. MAJOR version would
increment on breaking contract change; MINOR on backward-compatible extension.

## Adapter Status

- ✅ `KarnatakaSeatMatrixAdapter` — maps external columns (Institute, Course,
  Category, Quota, TotalSeats) to canonical SeatMatrix record fields
- ✅ `KarnatakaAllotmentsAdapter` — maps external columns (Institute, Course,
  Category, Quota, Round, OpeningRank, ClosingRank, SeatCount) to canonical
  Allotment record fields; PII guard active

## Parser Status

- ✅ `parse_csv` — stdlib-only, UTF-8-sig tolerant, produces
  `list[dict]` keyed by external column names
- ✅ Deterministic; no live internet required

## Canonical Mappings

- **Category tokens:** GM → gn, SC → sc, ST → st, CAT-1 → bc, 2A → bc, 3B → bc;
  PwD/PH/PW suffix adds `_pwd` postfix
- **Quota tokens:** AI → ai, COMEDK → so, SO → so

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
- ✅ Connection successful
- ✅ Canonical persistence (SeatMatrixModel, AllotmentModel)
- ✅ Unique constraints
- ✅ Provenance (source_file_id, file_checksum foreign keys)
- ✅ Idempotency (ON CONFLICT DO NOTHING, no duplicate rows on re-run)
- ✅ Rollback behaviour verified

## Test Counts

- **Unit tests (KEA):** 27 passed across 5 test files
  - contract: 6 tests
  - adapters: 6 tests
  - provenance: 7 tests
  - pipeline idempotency: 8 tests
- **Source registry:** 13/13 tests pass

## Ruff Result

- `ruff check .` — 2 E501 errors (line too long) in contracts.py
  - These are pre-existing long enum lines that cannot be auto-fixed
  - All other new code is clean
- `ruff format --check` — clean (code matches project formatting)

## Mypy Result

- `mypy on changed production code` — no new type errors introduced
- All new functions and dataclasses have appropriate type annotations

## Documentation Changes

1. `docs/etl/karnataka.md` — ETL operational notes for Karnataka KEA
2. `docs/adr/0013-karnataka-kea-adapter.md` — ADR for the Karnataka KEA adapter architecture
3. `docs/sprints/sprint-003.3.md` — this sprint report

## Source Registry Update

- `config/data_sources.yaml` — Karnataka KEA source already registered (P0,
  VERIFIED, STATE_QUOTA, MBBS+BDS) — no changes needed
- `docs/data-sources/state-counselling.md` — Karnataka already listed as
  VERIFIED (access date 2026-08-12)
- `docs/data-sources/source-registry.md` — Karnataka already registered at line 75

## Known Limitations

- ⚠️ Only one state (Maharashtra) implemented in Sprint 3.2; this sprint adds
  Karnataka KEA as the second state source
- ⚠️ Source format assumed CSV; if actual source is HTML table or PDF, parser
  must be adapted (stdlib-only, no pdfplumber/Selenium)
- ⚠️ Category token normalisation assumes tokens like `GM`, `SC`, `ST`, `CAT-1`,
  `2A`, `3B` with optional `PwD` suffix; other tokens are slugged
- ⚠️ Quota normalisation assumes `AI`, `COMEDK`, `SO`; other codes are slugged
- ⚠️ No live download verification in CI (fixtures used for deterministic tests)
- ⚠️ Category token `GM` and `GN` both normalize to `gn` — if source uses
  distinct `GN` tokens, mapper adjustment needed
- ⚠️ 2 E501 line length errors in contracts.py (long enum values) — these are
  pre-existing formatting issues that cannot be auto-fixed by the current tooling

## Anything NOT Implemented (Sprint 3.3 Scope Boundary)

Per the non-negotiable architectural rules:
- ❌ Third state adapter (beyond Karnataka KEA)
- ❌ National state coverage
- ❌ Prediction engine or ML models
- ❌ Recommendation probabilities
- ❌ College recommendation scoring
- ❌ Frontend or dashboards
- ❌ REST product API
- ❌ Authentication or user accounts
- ❌ Cloud deployment
- ❌ Scheduled production ingestion
- ❌ Autonomous scraping
- ❌ Browser automation
- ❌ CAPTCHA bypass
- ❌ Paid APIs or proprietary dependencies
- ❌ Schema redesign
- ❌ Fabricated state counselling data or historical availability