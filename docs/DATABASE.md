# Database Design

## Overview

The NEET Compass AI database is a production-grade PostgreSQL 16 schema with 24
tables organized into 7 logical categories. See [ADR-003: Database Design](decisions/0003-database-design.md)
for the full architectural rationale.

## Table Categories

| Category | Tables | Purpose |
|----------|--------|---------|
| Lookup | states, districts, categories, quotas, rounds, courses | Reference data |
| Reference | colleges, fees, seat_matrix | Institution data |
| Domain | allotments, candidates, recommendations, predictions, prediction_history | Counselling data |
| User | users, uploads | Platform users |
| ETL | data_sources, source_files, etl_runs, etl_errors | Data ingestion |
| System | model_versions, feature_flags, system_settings, logs | Infrastructure |

## Design Principles

### Primary Keys
- **UUID v4** (`gen_random_uuid()`) for all tables
- PostgreSQL 13+ built-in UUID generation (no extension required)

### Timestamps
- `created_at` — row creation (server-side default)
- `updated_at` — last modification (auto-update)
- `deleted_at` — soft delete (NULL = active)
- All are `TIMESTAMPTZ` in UTC

### Soft Delete
Implemented on reference, user, and lookup tables. Immutable audit tables
(allotments, recommendations, predictions, logs) are append-only.

### Enum Storage
Enums stored as VARCHAR with `native_enum=False` — validated at the
application boundary via Pydantic and StrEnum. This allows adding new enum
values with only a code change, no schema migration.

### Foreign Key Actions
| Action | Use Case |
|--------|----------|
| `CASCADE` | Child records deleted when parent destroyed |
| `SET NULL` | Audit references preserved (candidate, user, source file) |
| `RESTRICT` | Not currently used (all FKs allow deletion) |

## Indexing Strategy

| Index | Columns | Purpose |
|-------|---------|---------|
| `ix_allotments_college_year_round` | college_id, counselling_year, round_number | Per-college history |
| `ix_allotments_cohort` | quota_type, category, gender, is_pwd, counselling_year | Cohort filtering |
| `ix_recommendations_candidate` | candidate_id, created_at | Latest recommendation lookups |
| `ix_fees_college_year` | college_id, academic_year | Fee lookups by college |
| `ix_seat_matrix_college_year` | college_id, academic_year | Seat lookups by college |
| `ix_predictions_user_created` | user_id, created_at | User prediction history |
| `ix_prediction_history_rank` | prediction_id, probability | Ordered recommendations |
| `ix_model_versions_production` | is_production, model_name | Active model lookup |

See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for the complete column-by-column reference.

## Data Versioning

Every prediction is reproducible by tracing through:

```
predictions.model_version_id → model_versions
predictions.engine_name/version → version reference
source_files.source_version → Dataset Version
data_sources.data_version → Source Version
etl_runs.etl_version → ETL Version
predictions.id → Prediction Version
```

## Migration Workflow

```bash
# Apply all migrations
alembic upgrade head

# Check current revision
alembic current

# Create new migration
alembic revision -m "description"

# Rollback one revision
alembic downgrade -1
```

## Operational Guidelines

### Backups
Use `pg_dump` with compression. See [INSTALLATION.md](../INSTALLATION.md) for scripts.

### Partitioning (Phase 3)
Plans to partition `allotments` by `counselling_year` and `logs` by date.

### Connection Pooling
Application uses SQLAlchemy with pool_size=5, max_overflow=10, pool_timeout=30s,
pool_pre_ping=true.

### Monitoring
Monitor query performance on:
- `allotments` cohort filter queries
- `predictions` by user date range
- `seat_matrix` by college/year
