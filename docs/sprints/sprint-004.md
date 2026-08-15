# Sprint Report: Sprint 4

## Sprint Goal

Implement core recommendation engine logic, integrate background task
processing for ETL pipelines and model training, and harden the API with
authentication, rate limiting, and comprehensive integration tests.

## Deliverables

1. **Recommendation Engine** — Domain logic for generating college
   recommendations based on rank, category, quota, and preference list,
   stored in the `recommendations` and `prediction_history` tables.
2. **Celery ETL Worker** — Production-ready Celery worker consuming the
   `etl` queue, processing source files, recording run status and errors
   in `etl_runs`, `etl_errors`, and `source_files`.
3. **Authentication Layer** — JWT-based auth with access/refresh tokens,
   role-based authorization (USER, ADMIN, SUPERADMIN), password hashing
   with bcrypt, and token revocation via the `users` and `auth_events`
   tables.
4. **Rate Limiting** — Per-user and per-IP rate limits using
   fastapi-limiter with Redis backend (100 req/min for authenticated
   users, 10 req/min for unauthenticated).
5. **Health Check Endpoint** — `/health` endpoint returning database
   connectivity, Redis connectivity, and model registry status.
6. **API Integration Tests** — Full-stack tests using TestClient and
   Docker-based PostgreSQL fixtures covering auth flows, recommendation
   generation, and error handling.
7. **ETL Documentation** — `docs/ETL_SPEC.md` updated with pipeline
   architecture, error handling patterns, and monitoring dashboards.
8. **Deployment Guide** — `docs/DEPLOYMENT.md` with Docker Compose setup,
   environment variable reference, and CI/CD pipeline overview.
9. **Testing Strategy** — `docs/TESTING_STRATEGY.md` documenting unit,
   integration, and contract testing approaches.

## Architecture Decisions

### Auth Model
- JWT access tokens (15 min expiry), refresh tokens (30 day expiry).
- Passwords hashed with bcrypt (14 rounds).
- Token refresh rotates the refresh token; stolen tokens are revocable
  via a denylist stored in `auth_events`.

### ETL Pipeline Stages
1. **Ingest** — Download or read source file, compute checksum, insert
   into `source_files`.
2. **Parse** — Parse CSV/Excel, validate row structure, write errors to
   `etl_errors`.
3. **Transform** — Map source columns to domain fields, apply category
   normalization.
4. **Load** — Bulk-insert rows with ON CONFLICT for upserts; update
   `etl_runs` with row/error counts.
5. **Validate** — Run data quality checks (duplicate seats, missing
   colleges, rank ordering).

### Rate Limiting Strategy
- Key on user ID for authenticated requests.
- Key on client IP for unauthenticated requests.
- 429 responses include `Retry-After` header.
- Redis counter with sliding window (Lua script for atomicity).

## Key Outcomes

| Metric | Sprint 3 | Sprint 4 |
|---|---|---|
| API endpoints | 15 | 38 |
| Auth endpoints | 0 | 5 |
| Celery tasks | 0 | 8 |
| ETL stages | 0 | 5 |
| Test coverage | 42 tests | 97 tests |
| Documentation pages | 20 | 23 |

## Risks & Mitigations

1. **JWT token theft** — Short-lived access tokens; refresh tokens are
   rotated and can be revoked. Users must re-authenticate after 30 days.
2. **ETL partial failure** — Each stage is checkpointed in `etl_runs`;
   a failed run can be resumed from the last successful stage.
3. **Rate limiter memory pressure** — Redis sliding-window counters are
   expired automatically after the window period; monitoring alerts on
   Redis memory above 80%.

## Sprint Retrospective

Integrating Celery proved the value of ADR-007's layered task design.
The custom BaseTask automatically captured all ETL errors, giving us
visibility into parsing issues early. The auth layer took longer than
planned due to JWT edge cases, but the domain test fixtures paid for
themselves by catching several bugs before they reached code review.
