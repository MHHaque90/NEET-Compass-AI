# Ingestion idempotency

> Sprint 3.1A. Two complementary idempotency layers — file-level
> (checksum short-circuit) and record-level (composite-key upsert) — and a
> three-run proof that re-running a source is safe.

## Layer 1 — file idempotency (short-circuit)

`FileRegistry.has_checksum(checksum)` guards the whole pipeline. If a file's
SHA-256 was already registered, ingestion stops before any parsing:

* `file_ingested=False`
* `records_transformed=0`
* `records_skipped=<row count of the known file>`

Nothing is re-validated or re-written; the code path is cheap and deterministic.

## Layer 2 — record idempotency (upsert by composite key)

Each record is upserted on a composite canonical key:

* Seat matrix: `(college_id, course_id, quota_id, category_id, effective_year)`
* Allotments: `(college_id, course_id, quota_id, category_id, round_id, rank)`

An `InMemoryLoader` merges on that key and returns `False` for updates, `True`
for inserts, so idempotency is provable without a database.

In production the SQLAlchemy `AllotmentLoader`
(`backend/.../etl/loaders/allotment_loader.py`) inserts with
`ON CONFLICT DO NOTHING` against the cohort unique constraint
`uq_allotments_college_round_cohort`. The emitted SQL is verified — without a
live database — by `tests/unit/infrastructure/etl/test_allotment_loader_sql.py`,
which compiles the loader's statement on the PostgreSQL dialect and asserts the
`ON CONFLICT ... DO NOTHING` clause.

## Layer 3 — content identity vs record identity

`SourceMetadata` separates two notions:

* **Source identity** — derived from content (checksum) and stored in
  `source_file_id`. Changes when the bytes change.
* **Record identity** — the composite key(s) already present in the store.
  Unchanged by re-downloading or re-ingesting.

So a file that is *edited* by the authority at the **same URL** is correctly
recognised as a new source (new `source_file_id`) while its unchanged records
merge in-place and its changed records add/update — no duplicates, no lost
rows.

## Three-run proof

`test_three_runs_same_source_url_changed_bytes` (in
`tests/unit/.../test_pipeline_idempotency.py`):

| Run | Input | `file_ingested` | Rows written | Store size | Finding |
|-----|-------|-----------------|--------------|------------|---------|
| 1 | File A at URL U | True | 8 | 8 | initial ingest |
| 2 | File A at URL U (identical bytes) | False | 0 | 8 | checksum short-circuit, zero duplicate writes |
| 3 | File B (same URL U, changed bytes: one category republished) | True | 8 | 9 (7 merged keys + 1 new key) | new `source_file_id`, unchanged rows merge, changed row adds, nothing duplicated |

The same `source_url` is recorded on all three runs; `source_file_id(Run1) ==
source_file_id(Run2) != source_file_id(Run3)`.

## What would the real database do?

A live PostgreSQL round-trip is the integration suite's job. In the Sprint
3.1A sandbox this is **BLOCKED**: a PostgreSQL 17 server is running on
`localhost:5432`, but the on-file dev credentials
(`postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass`)
are rejected (`FATAL: password authentication failed for user "neet"`), there
is no `.env` override, and the backend integration suite hangs against the
rejected server. The conftest's silent SQLite fallback could mask this, so
real-database verification remains pending a working `DATABASE_URL`. Until
then the SQL layer is verified by compilation (above) and the logic by the
in-memory ports.