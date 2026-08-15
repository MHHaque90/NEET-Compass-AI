# ADR-003: Database Design

- **Status:** Accepted (Sprint 2)
- **Date:** 2026-08-10
- **Deciders:** Principal Database Architect, Lead Architect, Backend Team
- **Category:** Data

## Context

NEET Compass AI requires a production-grade PostgreSQL schema that supports:

1. **Historical counselling data** — 2020+ years without schema modifications
2. **Data versioning** — dataset, source, model, prediction, and ETL versioning
3. **Reproducibility** — every prediction must be reproducible from a specific dataset + model
4. **Data integrity** — prevent duplicate colleges, states, quotas, categories, seat matrices, cutoffs
5. **Auditability** — explainability trail for every prediction
6. **Performance** — fast hot-path queries for counselling recommendation
7. **Soft deletes** — preserve data for audit without physical deletion

The previous Sprint 1 schema had only 4 tables (colleges, candidates, allotments,
recommendations). Sprint 2 requires 24 tables with full normalization and
versioning support.

## Decision

### Schema Architecture

We adopt a **fully normalized, layered schema** with the following design:

#### Table Categories

1. **Lookup/Master Tables** — States, Districts, Categories, Quotas, Rounds, Courses
2. **Reference Data** — Colleges, Fees, Seat Matrix
3. **Domain Data** — Candidates, Allotments (historical cutoffs)
4. **User Data** — Users (candidate profiles for self-hosted usage)
5. **Prediction Pipeline** — Predictions, Prediction History, Model Versions
6. **ETL Infrastructure** — Data Sources, Source Files, ETL Runs, ETL Errors
7. **System Infrastructure** — Uploads, System Settings, Feature Flags, Logs

#### Primary Keys

- **UUID v4** (`gen_random_uuid()`) for all primary keys
- Rationale: Prevents enumeration attacks, enables horizontal sharding, globally unique across services
- PostgreSQL 13+ `gen_random_uuid()` is built-in, no extension needed

#### Timestamps

- **`created_at`** — set by database on INSERT (`server_default=now()`)
- **`updated_at`** — set by database on INSERT and UPDATE (`server_default=now(), onupdate=now()`)
- **`deleted_at`** — soft delete pattern; NULL = active, timestamp = soft-deleted
- All timestamps use `TIMESTAMPTZ` (timezone-aware) with UTC

#### Soft Delete Pattern

- Tables that represent reference data, user data, and configurations support soft deletes
- Lookup tables (States, Districts, Categories, Quotas, Rounds, Courses) support soft deletes to preserve audit
- The `deleted_at` column is NULL for active records
- Soft-deleted records are excluded from normal queries via a `WHERE deleted_at IS NULL` filter in repository queries

#### Normalization for Data Integrity

Each lookup table has:
- **Primary key** (UUID)
- **Code** (short code, e.g., "MBBS", "AIQ", "GENERAL")
- **Name** (human-readable name)
- **Unique constraints** on code and name to prevent duplicates
- **is_active** flag for lifecycle management
- **Timestamps** and **soft delete** support

#### Relationship Design

- All FKs reference the **lookup table** (e.g., `states.id`) not the domain enum value
- Domain enums are used in the application layer for validation
- The lookup tables can be seeded and extended without code changes
- `ON DELETE CASCADE` for child records when parent is destroyed
- `ON DELETE SET NULL` for audit references (preserving history)

### Versioning Strategy

Every prediction must be reproducible from:
1. **Dataset Version** — tracked via `source_files.source_version`
2. **Source Version** — tracked via `data_sources.data_version` and `source_files.source_version`
3. **Model Version** — tracked via `model_versions.version` and referenced in `predictions.model_version_id`
4. **Prediction Version** — tracked via `predictions.engine_version` and `predictions.id` (UUID)
5. **ETL Version** — tracked via `etl_runs.etl_version`

### Indexing Strategy

Every table has:
- **Primary key index** (implicit from PK constraint)
- **Created/updated timestamp** columns (no separate index)
- **Business query indexes** on FK columns and hot-path filters

Composite indexes for hot queries:
- `allotments`: `(college_id, counselling_year, round_number)` — per-college history
- `allotments`: `(quota_type, category, gender, is_pwd, counselling_year)` — cohort filter
- `predictions`: `(candidate_id, created_at)` — latest recommendation lookups
- `seat_matrix`: `(college_id, academic_year)` — per-college seat counts
- `fees`: `(college_id, academic_year)` — per-college fees

### Data Quality Constraints

#### Unique Constraints (Prevent Duplicates)

- `colleges.code` — prevents duplicate college codes
- `allotments`: `(college_id, year, round, quota, category, gender, pwd)` — idempotent ETL
- `seat_matrix`: `(college_id, course, quota, category, year)` — prevents duplicate seat entries
- `categories.code` — prevents duplicate categories
- `quotas.code` — prevents duplicate quotas
- `rounds.code` and `rounds.round_number` — prevents duplicate rounds
- `courses.code` — prevents duplicate courses
- `data_sources.code` — prevents duplicate data sources
- `source_files`: `(source_id, year, file_name, version)` — prevents duplicate file tracking

#### Check Constraints (Data Validation)

- `allotments.closing_rank >= allotments.opening_rank` — rank sanity
- `seat_matrix.seats_sanctioned >= seat_matrix.seats_filled` — capacity sanity
- `predictions.top_probability` between 0 and 1 (enforced in application layer)
- `model_versions.is_production` — only one production version per model (enforced via unique partial index)
- `feature_flags.rollout_percentage` between 0 and 100 (enforced in application layer)

### Foreign Key Strategy

| Relationship | On Delete | Rationale |
|-------------|-----------|-----------|
| `allotments.college_id → colleges.id` | CASCADE | Delete college → delete its cutoffs |
| `recommendations.candidate_id → candidates.id` | SET NULL | Keep recommendations, purge candidate PII |
| `recommendations.college_id → colleges.id` | CASCADE | Delete college → delete its recommendations |
| `predictions.user_id → users.id` | SET NULL | Keep predictions, purge user PII |
| `prediction_history.prediction_id → predictions.id` | CASCADE | Delete prediction → delete history |
| `etl_errors.etl_run_id → etl_runs.id` | CASCADE | Delete run → delete errors |
| `system_settings.feature_flag_id → feature_flags.id` | SET NULL | Settings outlive flag definitions |

### Enum Strategy

Enums are stored as **VARCHAR with application-level validation** (`native_enum=False`),
not as native PostgreSQL enums. This allows adding new enum values with only a code
deployment, no schema migration required.

- Validated in the domain layer via StrEnum
- Validated at boundaries via Pydantic
- Database has no native enum type constraints (documented as a Phase 2 hardening option)

## Consequences

### Positive
- Full data integrity with normalization and unique constraints
- Easy to add new enum values without migrations
- Reproducible predictions via comprehensive versioning
- Fast queries via composite indexes on hot paths
- Audit trail preserved via soft deletes and immutable logs
- UUID primary keys prevent enumeration and support sharding

### Negative
- More tables = more FK joins (mitigated by application caching)
- Soft deletes add complexity to queries (mitigated by repository abstraction)
- VARCHAR enums lose DB-level validation (mitigated by application boundary validation)

### Neutral
- The `logs` table is append-only and may require partitioning in production
- Lookup tables can be seeded from a JSON or CSV seed file
- The schema supports 2020+ years by storing `counselling_year` as a smallint, not hardcoded

## References

- [ADR-001: Technology Stack](0001-tech-stack.md)
- [ADR-004: Versioning](0004-versioning.md)
- [docs/DATABASE.md](DATABASE.md)
- [docs/data-model.md](../data-model.md)
- [docs/DATA_DICTIONARY.md](DATA_DICTIONARY.md)
