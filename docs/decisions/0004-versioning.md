# ADR-004: Data and Model Versioning

- **Status:** Accepted (Sprint 2)
- **Date:** 2026-08-10
- **Deciders:** Lead Architect, Principal Database Architect, ML Engineer
- **Category:** Data

## Context

NEET Compass AI must guarantee that **every prediction is reproducible**.
A prediction made today must yield identical results when re-run tomorrow,
even if:

- The underlying historical cut-off data has been updated (ETL re-run)
- The machine learning model has been retrained with new parameters
- The counselling logic has been modified

The following versioning dimensions must be tracked:

1. **Dataset Version** — which version of the historical cut-off data was used
2. **Source Version** — which version of the source file (MCC/state release)
3. **Model Version** — which trained model produced the prediction
4. **Prediction Version** — which prediction run (with its config and inputs)
5. **ETL Version** — which version of the ETL pipeline processed the data

The previous Sprint 1 schema had no explicit versioning beyond
`engine_version` on the recommendations table. Sprint 2 requires
comprehensive versioning across all lifecycle stages.

## Decision

### Versioning Approach

We use **explicit version columns** on every relevant table rather than
temporal tables or event sourcing. This keeps the schema simple and
queryable while providing full reproducibility.

#### Dataset Version

Tracked via:
- `data_sources.data_version` — the version of the data source
- `source_files.source_version` — the version of the specific file
- `source_files.etl_version` — which ETL pipeline version processed it
- `etl_runs.etl_version` — which ETL pipeline version was used

Each data source gets a monotonically increasing version string. When the
MCC releases new cut-offs, the source version increments, and all derived
ETL runs, source files, and downstream predictions reference the new
source version.

#### Model Version

Tracked via `model_versions` table:

| Column | Description |
|--------|-------------|
| `model_name` | e.g., "rank_predictor", "recommendation_engine" |
| `version` | e.g., "1.0.0", "2024-07-01" |
| `model_type` | RULE_BASED, LOGISTIC_REGRESSION, GRADIENT_BOOSTING, etc. |
| `status` | TRAINING, TRAINED, VALIDATING, VALIDATED, STAGING, PRODUCTION, etc. |
| `is_production` | Boolean — only one production version per model name |
| `training_data_version` | Links to the dataset used for training |
| `validation_data_version` | Links to the dataset used for validation |
| `training_metrics` | JSON — accuracy, precision, recall, etc. |
| `validation_metrics` | JSON — validation metrics |
| `feature_names` | JSON list — features the model expects |
| `parent_model_id` | Self-referencing FK for model lineage |

Models are **immutable** once registered. New versions are created as new
rows, never updated. Only the `is_production` flag is toggled to switch
versions.

**Unique Constraint:** `(model_name, version)` ensures no duplicate versions.

**Production Constraint:** A partial unique index on
`(model_name) WHERE is_production = true AND deleted_at IS NULL`
guarantees only one production version per model.

#### Prediction Version

Tracked via `predictions` table with the following versioning columns:

| Column | Description |
|--------|-------------|
| `engine_name` | e.g., "rule_based", "gradient_boosting_v1" |
| `engine_version` | Version of the engine code |
| `model_version_id` | FK → `model_versions.id` |
| `session_id` | Correlation ID for the prediction session |

Each prediction also stores:
- `request_metadata` — input parameters, candidate profile, feature vectors
- `response_metadata` — output parameters, selected colleges, timing
- `processing_time_ms` — for performance tracking
- `engine_name` / `engine_version` — provenance

Predictions are **immutable** — once created, they are never updated.
The `prediction_history` table stores the granular per-college recommendations.

**Reproducibility Query:**

```sql
-- Given a prediction ID, reproduce the exact same output
SELECT ph.*
FROM prediction_history ph
JOIN predictions p ON ph.prediction_id = p.id
JOIN model_versions mv ON p.model_version_id = mv.id
WHERE p.id = :prediction_id;
```

#### ETL Version

Tracked via:
- `etl_runs.etl_version` — the version of the ETL pipeline code
- `source_files.etl_version` — which ETL processed the file
- `etl_runs.code_version` — git commit hash for full traceability

ETL runs are immutable records of pipeline execution. They capture:
- Input configuration (`config_snapshot`)
- Processing statistics (`total_files`, `processed_files`, `total_rows`, etc.)
- Error metrics (`error_count`, `error_summary`)
- Quality metrics (`quality_score`, `validation_passed`, `validation_failed`)
- Timing (`started_at`, `completed_at`, `duration_seconds`)

### Versioning Workflow

```
1. Data Source version changes → Source file discovered
2. ETL pipeline runs (with etl_version) → etl_runs record + source_file record
3. Seats and fees loaded → seat_matrix + fees linked to source_file
4. Prediction requested → predictions record links to model_version
5. Prediction result stored → prediction_history linked to prediction
6. To reproduce: query predictions → join model_versions + source_files + etl_runs
```

### Data Lineage

The full lineage from raw data to prediction:

```
data_sources (data_version)
    └── source_files (source_version, etl_version)
        └── etl_runs (etl_version)
            └── seat_matrix / fees (via source_file_id FK)
                └── allotments (historical cutoffs, via source_file_id FK)
                    └── predictions (via model_version_id)
                        └── prediction_history (individual college recommendations)
```

### Reproducibility Guarantee

To reproduce any prediction:
1. Identify the prediction by ID or session_id
2. Trace to its model_version (engine_name, engine_version, model_version_id)
3. Trace to the training_data_version used by that model
4. Trace to the source_files and etl_runs that produced the training data
5. All data is immutable — the lineage path is fixed at prediction time

### Audit Trail for Versioning

Every versioned table includes:
- `created_at` / `updated_at` timestamps
- Soft delete support (`deleted_at`) for non-destructive updates
- For models: `deprecated_at`, `deprecated_by`, `deprecation_reason` for graceful model retirement

### Environment Tagging

All versioned artifacts also carry environment context:
- `model_versions` can be scoped to development, staging, or production
- Feature flags (`feature_flags`) control which model versions are active per environment
- System settings (`system_settings`) can override model selection per environment

## Consequences

### Positive
- Full reproducibility: any prediction can be traced back to its data, code, and model
- Auditability: every version change is logged
- Safety: model rollbacks are possible by flipping `is_production`
- Transparency: stakeholders can see exactly which data and model produced a recommendation

### Negative
- More storage overhead from version history
- Slightly more complex queries (need to join version tables)
- Requires discipline to version everything consistently
- Migration scripts may need to backfill version columns

### Neutral
- Versioning is manual (developer sets version strings)
- No automated version bumping (can be added in Phase 3)
- Historical data is preserved indefinitely (cleanup policy is Phase 3)

## References

- [ADR-003: Database Design](0003-database-design.md)
- [docs/DATABASE.md](DATABASE.md)
- [docs/DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- [docs/PREDICTION_SPEC.md](PREDICTION_SPEC.md)
