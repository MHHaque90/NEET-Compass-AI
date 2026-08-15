# Sprint Report: Sprint 3

## Sprint Goal

Implement the API layer following the ADR-006 design pattern (layered FastAPI
with Pydantic schemas, service/repository separation), establish the background
task processing foundation (ADR-007, Celery integration), and begin building
endpoint coverage for the core domain entities (colleges, cutoffs, predictions).

## Deliverables

1. **API Skeleton** — FastAPI application factory pattern with v1 router structure, CORS, and global exception handlers.
2. **Pydantic Schemas** — Complete request/response schemas for all domain tables, following BaseSchema / BaseRequestSchema pattern.
3. **Service Layer** — Stateless service classes for CollegeService, AllotmentService, UserService, PredictionService, ETLService.
4. **Repository Layer** — Async SQLAlchemy repositories returning domain entities, with cursor-based pagination helpers.
5. **Celery Integration** — celery_app.py with PostgreSQL result backend, Redis broker config, task routing.
6. **API Tests** — Integration tests covering authentication, college filtering, prediction creation flow.
7. **OpenAPI Generation** — Swagger UI at /docs, ReDoc at /redoc.
8. **API Documentation** — docs/API_SPEC.md detailing all endpoints, request/response schemas, auth flows, and rate limits.
9. **ADR-006 & ADR-007** — Architecture Decision Records for API design pattern and background task processing.

## Architecture Decisions

### ADR-006: API Design Pattern (Accepted — Sprint 3)
- Layered pattern: routes -> schemas -> services -> repositories -> models
- Pydantic v2 base schemas with from_attributes=True for responses
- Request schemas reject extra fields (extra=forbid)
- URL versioning: /api/v1/ prefix
- Cursor-based pagination with Link header
- FastAPI TestClient for integration testing

### ADR-007: Background Task Processing (Proposed — Sprint 3)
- Celery 5.x with Redis broker and PostgreSQL result backend
- Task routing by name pattern: etl.*, ml.*, default
- Custom BaseTask with automatic status updates
- Celery Beat with DatabaseScheduler for periodic tasks
- Separate worker pools: ETL (--concurrency=4), ML (--concurrency=1)

## Key Outcomes

| Metric | Sprint 2 | Sprint 3 |
|---|---|---|
| Database tables | 22 | 22 (locked) |
| API endpoints | 0 | 15+ |
| Pydantic schemas | 0 | 44+ |
| Service classes | 0 | 5 |
| Repository classes | 0 | 5 |
| Test coverage | 12 tests | 42 tests |
| Documentation pages | 18 | 20 |

## Risks & Mitigations

1. **Async SQLAlchemy learning curve** — Mitigated by pairing new contributors with database architects and writing thorough repository tests.
2. **Celery task idempotency** — All tasks that modify state check a status column before proceeding and use atomic updates.
3. **OpenAPI drift** — CI runs openapi-spec-validator against every PR touching routes; schema tests ensure Pydantic models match the DB.

## Sprint Retrospective

The team successfully locked the database architecture at Sprint 2 and used
that stable foundation to accelerate Sprint 3 delivery. The layered API
pattern proved straightforward to implement once the decision was made,
and existing Pydantic experience from earlier phases reduced ramp-up time.
