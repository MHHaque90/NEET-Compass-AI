# ADR-007: Background Task Processing with Celery

- **Status:** Proposed (Sprint 4)
- **Date:** 2026-08-10
- **Deciders:** Lead Architect, ML Engineer, DevOps
- **Category:** Infrastructure

## Context

NEET Compass AI performs three categories of long-running work that should
not block HTTP request threads:

1. **ETL Pipelines** — Daily ingestion of MCC and state counselling data
   (multi-gigabyte CSVs from `mcc.gov.in` and state APIs).
2. **Model Training** — Retraining recommendation engines with fresh cut-off
   data (hours of compute on CPU).
3. **Batch Predictions** — Generating recommendations for bulk uploads or
   scheduled counselling cycles.

The previous Sprint 0/1/2 schema already includes `etl_runs`,
`etl_errors`, `model_versions`, and `source_files` tables to track this work,
but the execution layer itself has not been implemented.

Requirements:

- Tasks must be distributed across multiple workers.
- Tasks must survive worker crashes (at-least-once semantics).
- Task state and progress must be visible to users via API.
- Workers must be able to read/write the same PostgreSQL database.

## Decision

We integrate **Celery 5.x** with the following design:

### Architecture

```
                    ┌─────────────┐
                    │   Web API   │
                    └──────┬──────┘
                           │ tasks.enqueue()
                           ▼
                    ┌─────────────┐
                    │ Celery App  │
                    └──────┬──────┘
                ┌──────────┴──────────┐
                │                     │
          ┌─────▼─────┐         ┌─────▼─────┐
          │  Worker   │         │  Worker   │
          │ (ETL)     │         │ (ML)      │
          └─────┬─────┘         └─────┬─────┘
                │                     │
                ▼                     ▼
         ┌─────────────────────────────────────┐
         │       PostgreSQL (shared)          │
         │  (etl_runs, source_files, etc.)   │
         └─────────────────────────────────────┘
```

### Configuration

1. **Broker:** Redis (running in Docker alongside the app).
2. **Result backend:** PostgreSQL (via `celery.backends.database`), so
   task metadata (status, progress, results) persists alongside domain data
   and can be queried by the API layer without a separate Redis dependency.
3. **Task routing:** Tasks are routed by name pattern:
   - `etl.*` → `etl` queue (consumed by ETL workers).
   - `ml.*` → `ml` queue (consumed by ML workers).
   - `default` → `default` queue.

### Task Decorator

All tasks inherit from a custom `BaseTask` that automatically:

- Records start/end time in `etl_runs` or `model_versions`.
- Captures exceptions and writes to `etl_errors`.
- Updates the `status` column on the owning row.
- Emits metrics to `feature_flags` for observability.

```python
from app.infrastructure.celery_app import app, BaseTask

class BaseModelTask(BaseTask):
    def persist_status(self, version: ModelVersionModel, status: str):
        version.status = status
        self.db_session.commit()

@app.task(bind=True, base=BaseModelTask, name="ml.train")
def train_model(self, model_name: str, dataset_version: str):
    ...
```

### Concurrency

- ETL workers: `--concurrency=4 --pool=solo`
- ML workers: `--concurrency=1 --pool=solo` (memory-bound)

### Scheduling

Periodic tasks (daily ETL, weekly model retraining) use Celery Beat with
`DatabaseScheduler` so schedules are user-configurable via the admin API.

## Consequences

- **Pros:** Mature ecosystem, battle-tested, easy horizontal scaling, rich
  observability via Flower.
- **Cons:** Additional infra (Redis, extra container); at-least-once
  semantics require idempotent task bodies.
- **Neutral:** The PostgreSQL result backend creates a subtle dependency on
  the same DB used for domain data, but this is acceptable because task
  tables have separate naming prefixes.

## Alternatives Considered

1. **RQ (Redis Queue)** — Rejected. Lacks native result persistence and
  scheduling flexibility needed for ML training workflows.
2. **Dramatiq** — Rejected. Smaller community; the team has more experience
  with Celery.
3. **Django-Q / Huey** — Rejected. Tied to specific framework assumptions;
  Celery integrates cleanly with FastAPI.
4. **Self-managed asyncio tasks** — Rejected for production. Fine for
  dev/testing but cannot distribute across nodes or survive crashes.
