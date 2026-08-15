# ADR-008: Historical Cutoff Model

- **Status:** Accepted (Sprint 2.1 Remediation)
- **Date:** 2026-08-12
- **Deciders:** Lead Software Architect, Senior Database Architect
- **Category:** Data Architecture

## Context

NEET Compass AI requires a mechanism to serve derived historical cutoff information
to the prediction engine. The `allotments` table stores raw counselling allotment
observations as loaded from external data sources, with denormalized VARCHAR codes
for course, quota, and category. The prediction engine needs a normalized,
foreign-key-referenced representation of historical cutoff features (opening rank,
closing rank, opening marks, closing marks) keyed by college, course, quota, category,
and round.

## Decision

### Schema Architecture: `allotments` vs `historical_cutoffs`

We adopt a **dual-table architecture** with a clear semantic distinction:

#### `allotments` — Raw counselling allotment facts

- Stores ETL-loaded cut-off observations as-is from external sources
- Uses denormalized VARCHAR codes (course, quota_type, category) for maximum
  flexibility during data import
- Includes additional fields such as `seats_offered`, `college_code`, and
  `counselling_date` that are specific to the raw allotment format
- ETL idempotency is guaranteed by the unique constraint on
  `(college_id, counselling_year, round_number, quota_type, category, gender, is_pwd)`
- Remains the **canonical source** of raw cut-off data

#### `historical_cutoffs` — Derived historical cutoff facts

- Provides a normalized schema with proper foreign key relationships to lookup
  tables (`colleges.id`, `courses.id`, `rounds.id`, `quotas.id`, `categories.id`)
- Contains only the fields needed by the prediction engine: `opening_rank`,
  `closing_rank`, `opening_marks`, `closing_marks`, keyed by normalized identifiers
- Includes `source_file_id` for data provenance tracking, plus `created_at` and
  `updated_at` timestamps
- Has a unique constraint on `(college_id, course_id, year, round_id, quota_id,
  category_id)` to prevent duplicate derived entries
- **Does not duplicate raw allotment records** — it represents derived facts that
  the prediction engine can query efficiently without dealing with VARCHAR codes
- The prediction engine obtains historical cutoff features by querying this table,
  joining through normalized identifiers instead of parsing denormalized codes

### Migration

A new Alembic migration (0002) adds the `historical_cutoffs` table with:
- Appropriate foreign key constraints with `ON DELETE CASCADE/SET NULL`
- Composite indexes for hot-path query patterns
- A unique constraint preventing duplicate college/course/year/round/quota/category combinations

### Data Provenance

The `source_file_id` column in `historical_cutoffs` tracks which ETL source file
 contributed the data, enabling traceability from derived cutoff features back to
 the original raw allotment observations.

### Prediction Engine Integration

The prediction engine will query `historical_cutoffs` via the repository layer,
using the normalized FK relationships. This avoids the complexity of mapping
VARCHAR codes from `allotments` and provides a stable schema for the prediction
features even when raw ETL data format changes.

## Consequences

### Positive

- **Clean separation** between raw ETL data (`allotments`) and derived analytics
  (`historical_cutoffs`)
- **Normalized FK relationships** enable efficient prediction engine queries
  without VARCHAR code mapping
- **Data provenance** through `source_file_id` traces derived facts to raw
  observations
- **Unique constraint** prevents duplicate derived entries
- **Prediction engine** can depend on a stable schema even as ETL import formats
  evolve
- **No data duplication** — `historical_cutoffs` contains derived facts, not
  copies of raw allotment rows

### Negative

- Additional migration and model file
- Additional table to maintain and keep in sync
- Prediction engine must be updated to query `historical_cutoffs` instead of
  (or in addition to) `allotments`

### Neutral

- The `allotments` table continues to serve as the raw ETL input table
- Both tables can be queried independently; the choice depends on the use case

## Migration History

| Revision | Action |
|----------|--------|
| 0001 | Initial schema with `allotments` table (raw ETL data) |
| 0002 | Added `historical_cutoffs` table (derived cutoff facts) |

## References

- [ADR-003: Database Design](0003-database-design.md)
- [docs/DATABASE.md](DATABASE.md)
- [docs/DATA_DICTIONARY.md](DATA_DICTIONARY.md)