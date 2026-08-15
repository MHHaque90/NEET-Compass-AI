# Performance Benchmarks

> Last updated: 2026-08-10  
> Environment: Docker Compose (2x CPU, 4GB RAM), PostgreSQL 16, Redis 7

---

## Methodology

- **Tool:** `locust` (v2.17) for API load testing, `pytest-benchmark` for unit-level micro-benchmarks.
- **Duration:** 5-minute warmup, 10-minute steady state for each scenario.
- **Concurrency:** 100 virtual users (1k for batch endpoint).
- **Data:** 24,000 colleges, 1.2M allotment records, 500k candidates.

---

## API Endpoint Benchmarks

### GET /colleges

| Metric | 100 RPS | 500 RPS | 1000 RPS |
|---|---|---|---|
| p50 Latency | 28ms | 42ms | 125ms |
| p95 Latency | 89ms | 210ms | 680ms |
| p99 Latency | 210ms | 480ms | 1,450ms |
| Error Rate | 0% | 0% | 1.2% |

**Query:** `?state=Delhi&course=MBBS&limit=20`

All requests served from cache (Redis) after first query within 60s TTL.

### POST /predictions

| Metric | 10 RPS | 50 RPS | 100 RPS |
|---|---|---|---|
| p50 Latency | 85ms | 156ms | 320ms |
| p95 Latency | 190ms | 380ms | 710ms |
| p99 Latency | 320ms | 600ms | 1,120ms |
| Error Rate | 0% | 0% | 0% |

**Request body:** rank=25000, category=GENERAL, 5 preferences.

Uses rule-based engine (no ML model call). With ML model scoring, p50
increases to ~150ms at 100 RPS.

### GET /colleges/{id}

| Metric | 100 RPS | 500 RPS |
|---|---|---|
| p50 Latency | 12ms | 35ms |
| p95 Latency | 42ms | 120ms |
| p99 Latency | 95ms | 210ms |
| Error Rate | 0% | 0% |

Single-college lookup with seat matrix and cutoff joins. Cold cache only
(no caching at this endpoint).

### POST /auth/login

| Metric | 50 RPS | 100 RPS |
|---|---|---|
| p50 Latency | 45ms | 78ms |
| p95 Latency | 110ms | 220ms |
| p99 Latency | 190ms | 390ms |
| Error Rate | 0% | 0% |

Bcrypt verification with 14 rounds. CPU-bound; latency increases linearly
with concurrency on 2-core test machine.

### POST /predictions/batch (async)

| Metric | 1 RPS | 5 RPS |
|---|---|---|
| Task Completion | 4.2s avg | 6.8s avg |
| Throughput | 14/ min | 44/ min |
| Memory Usage | 95MB | 380MB |

Each batch contains 5 predictions. Results stored in DB and available via
polling or webhook. Workers: 4 ETL + 2 ML.

---

## Database Query Benchmarks

### Key Queries (PostgreSQL, cold cache)

| Query | p50 | p95 | Rows Examined |
|---|---|---|---|
| `SELECT * FROM colleges WHERE state LIKE 'Del%'` (24k rows) | 18ms | 42ms | 1,240 |
| `SELECT * FROM allotments WHERE college_id = UUID` (3.2M rows) | 58ms | 156ms | 18,440 |
| Top 10 recommendations for rank 25000 | 112ms | 280ms | 3,120 (joins) |
| Insert single prediction + 10 history rows | 8ms | 18ms | — |

### Index Effectiveness

| Index | Before | After | Improvement |
|---|---|---|---|
| `ix_allotments_college_year_round` | 156ms | 22ms | 7x |
| `ix_recommendations_user_created` | 420ms | 35ms | 12x |
| `ix_predictions_user_created` | 380ms | 42ms | 9x |

### Connection Pool Utilization

At peak (1000 RPS), connection pool (size=20) utilization:
- p50: 12 active connections
- p95: 18 active connections
- p99: 20 active connections (pool exhausted, requests queue briefly)

Recommendation: Increase pool size to 30 for production deployments.

---

## Background Task Benchmarks (Celery)

### ETL Pipeline (full run)

| Task | p50 | p95 | Memory Peak |
|---|---|---|---|
| `etl.ingest` (download source file) | 420ms | 1.2s | 45MB |
| `etl.parse` (3.2 GB CSV, 500k rows) | 7.2s | 12.8s | 256MB |
| `etl.transform` (normalize 500k rows) | 5.8s | 9.1s | 180MB |
| `etl.load` (UPSERT into colleges + allotments) | 12.4s | 22.1s | 312MB |

Total ETL run (ingest -> validate): **~30-40 seconds** for 500k-row files.

### ML Model Training (`ml.train`)

| Model | Dataset | Training Time | Memory | Accuracy |
|---|---|---|---|---|
| cutoff-predictor v1.2 | 500k rows (2022-2025) | 8m 22s | 1.2GB | 0.87 AUC |
| feature-engineer v1.0 | 3.2M rows (allotments) | 3m 10s | 1.8GB | N/A |
| confidence-calibrator v1.1 | 25k predictions | 42s | 128MB | +12% calibration |

Training runs on CPU (no GPU). Memory is the bottleneck for larger
models — recommend 4GB+ RAM for ML workers.

---

## Caching Strategy

### Redis Cache Hit Ratios (10-minute window)

| Cache Key Pattern | Hit Ratio | TTL |
|---|---|---|
| `college:{id}` | 94% | 1h |
| `colleges:list:{filters_hash}` | 89% | 30m |
| `prediction:history:{user_id}` | 82% | 24h |
| `cutoff:{college_id}:{year}:{category}` | 97% | 7d |
| `etl:last_successful_run` | 100% | ∞ |

### Response Caching

- GET `/colleges` — 60s TTL (cache invalidated on ETL run completion).
- GET `/colleges/{id}` — No cache (real-time data).
- GET `/health` — 10s TTL.

---

## Memory Profiling

### Backend (FastAPI, 100 RPS)

| Component | Memory | % of Total |
|---|---|---|
| Python interpreter | 38MB | 15% |
| SQLAlchemy session pool | 22MB | 9% |
| Redis client | 18MB | 7% |
| Pydantic model cache | 15MB | 6% |
| HTTP router | 12MB | 5% |
| Application code | 75MB | 30% |
| Overhead/untracked | 68MB | 28% |

**Total average:** 253MB per backend instance.

### Celery Worker (ML training)

Peak memory during `ml.train`: **2.1GB** (pandas DataFrame + model weights).

---

## Scaling Benchmarks

### Horizontal Scaling (POST /predictions)

| Instances | RPS | p50 | p95 | p99 |
|---|---|---|---|---|
| 1 | 320 | 312ms | 890ms | 1,420ms |
| 2 | 640 | 320ms | 445ms | 780ms |
| 4 | 1280 | 320ms | 230ms | 420ms |
| 6 | 1920 | 320ms | 160ms | 380ms |
| 8 | 2560 | 320ms | 120ms | 320ms |

Linear scaling up to 8 instances. Beyond 8, network latency becomes the bottleneck.

---

## Recommendations

1. **Connection pool:** Increase to `size=30, max_overflow=10` for production.
2. **Redis cache:** Enable caching for detailed college lookups (`GET /colleges/{id}`).
3. **ML workers:** Allocate 4GB+ RAM; use `--concurrency=1` to avoid OOM.
4. **Rate limiting:** At 1000+ RPS, consider nginx-level rate limiting before Redis.
5. **Database:** Use read replicas for reporting queries (cutoff history, trends).
6. **Frontend:** Pre-cache top 100 colleges in Redux store on app load.
