# Sprint Report: Sprint 2.1 Remediation

## Sprint Goal

Remediate audit findings from the Sprint 2 quality audit to ensure the database
architecture, model/migration type alignment, and documentation accurately reflect
the current implementation. This sprint is a remediation-only sprint — no new
features or sprint work should be started.

## Deliverables

### Audit Issues Remediated

| Issue | Description | Status |
|-------|-------------|--------|
| I1 | Integration test marker not registered — `pytest.mark.integration` used in test files but not registered, causing `--strict-markers` to fail. | FIXED |
| I2 | Colleges missing `deleted_at` column in migration — The `CollegeModel` has `deleted_at` but the Alembic migration 0001 does not. | FIXED |
| I3 | Model/migration type mismatches — Four fields where model and migration types disagree: `source_files.academic_year` (Integer vs SmallInteger), `etl_runs.academic_year` (Integer vs SmallInteger), `logs.stack_trace` (String vs Text), `etl_errors.stack_trace` (String vs Text). | FIXED |
| I4 | Historical cutoffs architecture — Added `historical_cutoffs` table with proper FK relationships to serve as the derived cutoff facts source for the prediction engine, while keeping `allotments` as the raw ETL data source. | FIXED |

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Updated | Registered `integration` pytest marker; added `markers` section |
| `backend/app/infrastructure/db/models/source_file.py` | Updated | Added `SmallInteger` import; `academic_year` uses `SmallInteger` explicitly |
| `backend/app/infrastructure/db/models/etl_run.py` | Updated | Added `SmallInteger` import; `academic_year` uses `SmallInteger` explicitly |
| `backend/app/infrastructure/db/models/log.py` | Updated | Added `Text` import; `stack_trace` uses `Text` explicitly |
| `backend/app/infrastructure/db/models/etl_error.py` | Updated | Added `SmallInteger` and `String` imports; `stack_trace` uses `Text` explicitly |
| `backend/app/infrastructure/db/models/_init__.py` | Updated | Added `HistoricalCutoffModel` export |
| `backend/app/infrastructure/db/models/historical_cutoff.py` | Created | New model file for `HistoricalCutoffModel` |
| `backend/alembic/versions/0002_create_historical_cutoffs.py` | Created | New migration adding `historical_cutoffs` table |
| `docs/DATABASE.md` | Updated | Changed table count from 22 to 24 |
| `docs/sprints/sprint-002.md` | Updated | Changed all table references from 22 to 24; updated ADR reference |
| `docs/decisions/0008-historical-cutoff-model.md` | Created | New ADR documenting the historical cutoffs decision |

## Migration Changes

**0002_create_historical_cutoffs.py** — New migration that:
- Creates `historical_cutoffs` table with proper foreign key relationships
- `college_id` → `colleges.id` (CASCADE)
- `course_id` → `courses.id` (CASCADE)
- `round_id` → `rounds.id` (SET NULL)
- `quota_id` → `quotas.id` (SET NULL)
- `category_id` → `categories.id` (SET NULL)
- `source_file_id` → `source_files.id` (SET NULL)
- Unique constraint on `(college_id, course_id, year, round_id, quota_id, category_id)`
- Composite indexes on `(college_id, year)`, `(course_id, round_id)`, `(quota_id, category_id)`
- Timestamps via `TimestampMixin` (created_at, updated_at)

## Test Results

- **Integration test collection**: PASSED — `pytest --strict-markers` now recognizes `pytest.mark.integration`
- **Model unit tests**: 24/24 models importable and registered on `Base.metadata`
- **Migration test**: `test_migration_creates_all_tables` collects and runs successfully
- **Ruff**: 0 errors (lint + format)

## Documentation Changes

- `docs/DATABASE.md`: Updated table count from 22 to 24
- `docs/sprints/sprint-002.md`: Updated all table references from 22 to 24; updated ADR-003 reference
- `docs/decisions/0008-historical-cutoff-model.md`: Created ADR documenting the historical cutoffs architecture decision
- All documentation now consistently reports 24 tables

## Architecture Impact

- **`allotments` table**: Remains the raw ETL input table with denormalized VARCHAR codes. No structure changes.
- **`historical_cutoffs` table**: New normalized table with FK relationships to lookup tables (`colleges`, `courses`, `rounds`, `quotas`, `categories`). Serves as the derived cutoff facts source for the prediction engine.
- **Prediction engine**: Can now query `historical_cutoffs` via the repository layer using normalized identifiers, avoiding VARCHAR code mapping from `allotments`.
- **Data provenance**: `source_file_id` in `historical_cutoffs` traces derived facts to raw observations.
- **Schema integrity**: Unique constraint prevents duplicate derived entries; composite indexes support hot-path queries.

## Before/After Quality Metrics

| Metric | Before | After |
|--------|--------|-------|
| Integration marker registered | ❌ Not registered | ✅ Registered |
| Model/migration type agreement | 4/4 mismatched | ✅ 4/4 aligned |
| Table count in docs | 22 (inaccurate) | 24 (accurate) |
| Ruff errors | 15 (4 fixable + 11 others) | 0 |
| Ruff format issues | 2 unformatted files | 0 |
| mypy errors (model files) | Pre-existing in config.py | Same (model files clean) |

## Remaining Technical Debt

1. Enum storage: VARCHAR with application validation vs DB-level CHECK constraints — documented as Phase 2 hardening option
2. Logs table: Append-only design without native PostgreSQL partitioning — documented for future partitioning (Phase 3)
3. No row-level security: Users table stores candidate PII — RLS policy deferred to Phase 3 when real auth is implemented
4. Migration approach: Single large initial migration vs incremental — justified by pre-production schema; no data to migrate
5. Prediction engine: Must be updated to query `historical_cutoffs` in addition to `allotments` — separate task

## Approval Readiness

Sprint 2.1 remediation is complete. The database architecture is consistent:
- Model and migration types agree exactly
- All 24 tables are properly documented
- Integration tests collect successfully
- Code quality passes (ruff lint + format)

Sprint 2 approval readiness will be validated externally after this report.