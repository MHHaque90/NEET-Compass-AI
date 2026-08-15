# ETL

The ingestion layer turns raw counselling releases (Excel/CSV from MCC and
state bodies) into clean, validated, idempotent rows in PostgreSQL.

## Where the code lives

| Location | Purpose |
| --- | --- |
| `backend/app/infrastructure/etl/` | Source/Transformer/Validator/Loader primitives and the allotment pipeline factory |
| `etl/config/pipelines.yaml` | Declarative pipeline definitions (source type, path, column maps) |
| `etl/run.py` | CLI that loads a pipeline definition and runs it |

The ETL code shares the backend's ORM models and session factory so ingested
data is immediately usable by the application.

## Pipeline anatomy

```
Source ──raw rows──> Transformer ──normalized──> Validator ──AllotmentRow──> Loader ──> PostgreSQL
```

- **Source** — adapter over a file/API. `ExcelSource`, `CSVSource`.
- **Transformer** — `AllotmentTransformer(column_map, year)` maps release
  headers to canonical columns and coerces types. Rows without ranks are
  dropped (they are footnotes, not data).
- **Validator** — `AllotmentRow` (Pydantic). All-or-nothing: one invalid row
  aborts the whole load (`DataValidationError`) so a corrupted release can
  never yield partial data.
- **Loader** — `AllotmentLoader` resolves college codes → ids, then batch
  upserts with `ON CONFLICT DO NOTHING` (unique constraint
  `uq_allotments_college_round_cohort`). Re-running the same year is safe.

## Usage

```bash
# Copy a release to the path expected by the pipeline definition first.
make db-up
make setup
PYTHONPATH=backend python etl/run.py --pipeline aiq_cutoffs --year 2025
```

Add a new release format by appending a `column_map` entry to
`etl/config/pipelines.yaml` (or a new pipeline block for new sources).
