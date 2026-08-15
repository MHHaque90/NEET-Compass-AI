# ETL Specification

## Overview

The ETL (Extract, Transform, Load) framework ingests historical NEET
counselling data from official sources (MCC, state counselling authorities)
into the database with full audit trail, versioning, and quality tracking.

## Architecture

```
Source  →  Transformer  →  Validator  →  Loader
 (file)     (normalize)    (contract)   (idempotent upsert)
```

### Source
Thin adapter that reads raw data files (Excel, CSV, future: PDF/web scraper).
Returns a pandas DataFrame with raw, unvalidated rows.

### Transformer
Normalizes raw data to the canonical schema using a per-release `column_map`.
Each data source ships with different column headers; the column_map maps
source-specific headers to canonical column names.

### Validator
Pydantic-based validation that fails **all-or-nothing**. A corrupted release
must never produce a partial, misleading dataset.

### Loader
Resolves reference data (college codes, states, etc.) to internal IDs and
upserts in batches with `ON CONFLICT DO NOTHING` for idempotency.

## Data Sources

The authoritative inventory of official sources (authority, URL, dataset,
priority, verification state) lives in
[`docs/data-sources/source-registry.md`](data-sources/source-registry.md) and
its machine-readable mirror [`config/data_sources.yaml`](../config/data_sources.yaml).
That layer — not this document — is the source of truth for where data comes
from. This section only lists the source families ETL consumes.

| Code | Name | URL | Type | Notes |
|------|------|-----|------|-------|
| `mcc_official` | MCC Official | mcc.nic.in | OFFICIAL | Main All India Quota data |
| `mcc_state` | State Counselling | state websites | OFFICIAL | Per-state releases |
| `college_website` | College Websites | Individual | COLLEGE | Fee and seat data |
| `nmc_registry` | NMC College List | nmc.org.in | OFFICIAL | Institution master list |

## Source File Tracking

Every source file is tracked in the `source_files` table with:

- `data_source_id` — which source it came from
- `file_name` — original filename
- `file_version` — version of the release
- `academic_year` — the counselling year
- `checksum_sha256` — for deduplication
- `status` — DISCOVERED → DOWNLOADED → VALIDATED → LOADED
- `source_version` — version of the source data
- `etl_version` — version of the ETL pipeline that processed it

## Pipeline Configuration

Pipelines are declared in `etl/config/pipelines.yaml`:

```yaml
pipelines:
  allotment:
    name: "allotment"
    description: "Ingest MCC/state cut-off data"
    source:
      type: "excel"
      path: "./data/raw/mcc_cuttOffs_2024.xlsx"
    transformer:
      column_map:
        "College Code": "college_code"
        "College Name": "college_name"
        "Opening AIR": "opening_rank"
        "Closing AIR": "closing_rank"
        "Quota": "quota_type"
        "Category": "category"
        "Gender": "gender"
    validator:
      model: "AllotmentRowValidation"
      strict: true
    loader:
      batch_size: 1000
      table: "allotments"
      dedup_key:
        - "college_code"
        - "counselling_year"
        - "round_number"
        - "quota_type"
        - "category"
        - "gender"
        - "is_pwd"
```

## ETL Run Tracking

Every ETL run is recorded in the `etl_runs` table:

| Field | Description |
|-------|-------------|
| `pipeline_name` | Which pipeline ran |
| `run_type` | FULL, INCREMENTAL, BACKFILL, REPROCESS, VALIDATION |
| `status` | PENDING, RUNNING, COMPLETED, FAILED, PARTIAL, CANCELLED |
| `config_snapshot` | Full config used for this run |
| `total_files` | Number of files to process |
| `processed_files` | Files actually processed |
| `total_rows` | Total rows encountered |
| `loaded_rows` | Rows successfully upserted |
| `error_rows` | Rows that failed validation |
| `started_at` / `completed_at` | Run timing |
| `duration_seconds` | Total run time |
| `etl_version` | Code version |
| `code_version` | Git commit hash |
| `triggered_by` | User, scheduler, or API |
| `quality_score` | Data quality metric (0-1) |

## Error Tracking

Every ETL error is recorded in the `etl_errors` table:

| Field | Description |
|-------|-------------|
| `etl_run_id` | Which run produced the error |
| `source_file_id` | Which source file |
| `stage` | EXTRACT, TRANSFORM, VALIDATE, LOAD |
| `severity` | INFO, WARNING, ERROR, CRITICAL |
| `error_code` | Classification code |
| `error_message` | Human-readable message |
| `row_number` | Row in the source file |
| `column_name` | Column that failed |
| `raw_value` | Original value |
| `expected_value` | What was expected |
| `is_resolved` | Manual resolution flag |
| `resolution_notes` | How it was fixed |

## Running ETL

### Via CLI

```bash
# Run a specific pipeline
python etl/run.py --pipeline allotment --year 2024 --round ROUND_1

# Run all pipelines for a year
python etl/run.py --all --year 2024

# Re-run a specific run
python etl/run.py --rerun <run_id>
```

### Via API (Planned Phase 3)

```bash
# Trigger ETL
POST /api/v1/etl/run
{
  "pipeline": "allotment",
  "data_source_id": "...",
  "academic_year": 2024
}
```

## Quality Guarantees

1. **Atomicity** — A failed validation cancels the entire batch
2. **Idempotency** — Re-running ETL does not create duplicates
3. **Auditability** — Every step is logged with timestamps and provenance
4. **Reproducibility** — The same source file + ETL version produces the same output

## Versioning

- Each ETL run records the `etl_version` and `code_version` (git commit)
- Source files track `source_version` and `etl_version`
- This enables full reproducibility: re-run any past ETL with the same version

## Future Enhancements (Phase 3+)

- Web scraper sources for MCC and state websites
- PDF parsing for releases that only provide PDF
- Incremental ETL (fetch only new files)
- Real-time streaming ETL with change data capture
- Data quality dashboards and drift detection
- Automated alerting on ETL failures
