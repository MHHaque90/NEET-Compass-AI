# ADR-006: API Design Pattern

- **Status:** Proposed (Sprint 3)
- **Date:** 2026-08-10
- **Deciders:** Lead Architect, Backend Engineering Team, Frontend Lead
- **Category:** Technical

## Context

The NEET Compass AI backend exposes REST APIs consumed by web, mobile, and
command-line clients. The existing Sprint 0/1/2 codebase has no explicit API
conventions — routes are defined ad-hoc in endpoint files without consistency.

Key requirements:

1. **Consistency** — All endpoints must follow a predictable structure so
   frontend and CLI tooling can be auto-generated.
2. **Type-safety** — Request and response schemas must be serializable and
   validated at the boundary; no raw dicts leaking in or out.
3. **Backward compatibility** — Clients must opt-in to breaking changes; the
   default should always be the stable contract.
4. **FastAPI-native** — Leverage Pydantic v2 models, dependency injection,
   and automatic OpenAPI generation rather than building abstractions over
   bare Flask/Starlette responses.

## Decision

We adopt a **layered pattern** inspired by FastAPI's dependency-injection
philosophy:

### 1. Route Files (`app/interfaces/api/v1/routes/*.py`)

Thin HTTP controllers that:

- Declare the FastAPI router (`APIRouter`).
- Depend on service-layer functions (never touch repositories directly).
- Return Pydantic response schemas only.
- Never contain business logic.

```
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/colleges", tags=["colleges"])

@router.get("/{college_id}", response_model=CollegeDetailSchema)
async def get_college(
    college_id: UUID,
    service: CollegeService = Depends(get_college_service),
) -> CollegeDetailSchema:
    college = await service.get_by_id(college_id)
    if college is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return college
```

### 2. Request / Response Schemas (`app/interfaces/api/v1/schemas/*.py`)

Pure Pydantic v2 models declaring the wire format. Two base patterns:

- `BaseSchema` — base for responses; includes `ConfigDict(from_attributes=True)`.
- `BaseRequestSchema` — base for payloads; adds `model_config = ConfigDict(extra="forbid")`.

This prevents clients from silently sending unexpected fields.

### 3. Service Layer (`app/application/services/*.py`)

Contains all business logic. Stateless, injected via FastAPI `Depends`.

### 4. Repository Layer (`app/infrastructure/repositories/*.py`)

Persistence abstractions. Return domain entities or `None`.

### 5. Versioning

- URL versioning: `/api/v1/` prefix on all routes.
- Deprecation header on responses when an endpoint is slated for removal:
  `Deprecation: true` and `Sunset: <date>`.

### 6. Pagination

All list endpoints follow cursor-based pagination with a `Link` header:

```
Link: <https://api.neetcompass.example/v1/colleges?cursor=xyz>; rel="next"
```

Query params: `cursor` (opaque string), `limit` (default 20, max 100).

## Consequences

- **Pros:** Auto-generated OpenAPI docs, consistent payloads, clear layer
  boundaries, easy testing with FastAPI's `TestClient`.
- **Cons:** More files and layers than a minimal Flask API; new contributors
  must learn the layered structure.
- **Neutral:** Some duplication between Pydantic schemas and SQLAlchemy models
  is acceptable and preferred over reflection.

## Alternatives Considered

1. **GraphQL** — Rejected. The data is tabular (colleges, cutoffs, seats).
   REST with careful resource modelling covers 95% of use cases and has a
   lower learning curve for contributors.
2. **Pure Flask + Marshmallow** — Rejected. FastAPI natively provides the
   validation, dependency injection, and OpenAPI generation we need.
3. **Single-layer "fat controller"** — Rejected. Makes business-logic reuse
   across CLI tooling impossible and tight-couples HTTP and domain logic.
