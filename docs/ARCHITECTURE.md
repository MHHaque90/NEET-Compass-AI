# Architecture

This document records the architectural decisions for NEET Compass AI and the
reasoning behind each one. It is the contract reviewers should hold the code
against.

---

## 1. System purpose

NEET Compass AI is an **Admission Intelligence Platform**. Given a candidate's
NEET All-India Rank (AIR), marks, category, domicile state, gender, PwD
status, minority status, quota type (AIQ / State), budget and preferred
states, the platform produces, per college:

- MBBS / BDS admission **probability**
- **Expected counselling round**
- **Confidence score**
- **Counselling strategy** (which quota to try, when to upgrade, risks)
- **Choice-filling order**
- **Explanations** for every recommendation

Because the output is high-stakes life advice, correctness, auditability and
explainability are first-class requirements — not afterthoughts.

## 2. Scope discipline (what we deliberately do NOT build yet)

Phase 1 deliberately excludes:
- **Prediction logic** — the scoring engine is a *port*; the default
  implementation (`UnavailableEngine`) refuses to fabricate numbers.
- **Product APIs** — only an infra health probe exists.
- **Frontend** — `frontend/` is a placeholder.
- **Dummy probabilities** — nothing returns invented values.

This keeps the riskiest part (inference quality) decoupled from the
foundation so it can be built and validated in isolation.

## 3. Layer architecture (clean / hexagonal)

```
┌──────────────────────────── api (FastAPI) ────────────────────────────┐
│   presentational glue: routes, request/response schemas (Phase 2)     │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │ depends on (interfaces)
┌──────────────────────── application (use cases) ─────────────────────┐
│   RecommendationService, StrategyService, Container (composition)    │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │ depends on (abstract ports only)
┌────────────────────────── domain (entities + ports) ─────────────────┐
│   CandidateProfile, College, AllotmentRecord, Recommendation, enums  │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │ implemented by
┌───────────────────────── infrastructure (adapters) ──────────────────┐
│   SQLAlchemy repositories, ETL pipeline, ML engine seam              │
└───────────────────────────────────────────────────────────────────────┘
```

Rules enforced by the codebase:
- **Domain has zero imports** from application, infrastructure, or FastAPI.
  It imports only stdlib + Pydantic.
- **Application never imports SQLAlchemy or FastAPI.** It talks to the world
  through ports defined in `domain/ports/`.
- **Infrastructure implements the ports.** Swapping PostgreSQL for another
  store, or the ETL source, touches only this layer.
- **The composition root** (`application/container.py`) is the single place
  that wires concrete implementations into services.

### Rationale
- *Testability:* every use case is unit-testable with fakes (see
  `backend/tests/unit/test_recommendation_service.py`) without a database.
- *Evolvability:* the ML model, the data source and the persistence engine
  can each be replaced independently.
- *Explainability:* domain entities carry the data (reasons, strategy) that
  the explanation layer needs, so "why" is preserved end-to-end.

## 4. SOLID mapping

| Principle | Where it lives |
| --- | --- |
| S — Single responsibility | One class per concern: entity vs ORM model vs repository vs source vs loader. |
| O — Open/closed | New engines, sources, loaders extend via new classes registered in the container — no edits to consumers. |
| L — Liskov substitution | Fakes in tests and the `UnavailableEngine` conform to the same port contracts as any future real engine. |
| I — Interface segregation | Separate ports: `AllotmentRepository`, `CollegeRepository`, `RecommendationRepository`, `RecommendationEngine`. |
| D — Dependency inversion | Application depends on `domain/ports` abstractions; infra implements them; wiring lives in the container. |

## 5. Dependency injection

- Constructor injection for all services (`RecommendationService` receives
  its engine and repositories).
- A lightweight composition root (`Container`) instead of a third-party
  container framework — the project is small and a framework adds coupling
  without benefit. FastAPI's `Depends` will use the container in Phase 2.
- The scoring engine is a container **singleton** (model loading is
  expensive); repositories are **per-session** and stateless.

## 6. The ML seam (future-proofing)

`domain/ports/recommendation_engine.py` defines the only contract a scoring
model must satisfy:

```python
class RecommendationEngine(ABC):
    name: str
    version: str
    def predict(self, candidate, college_id) -> Recommendation: ...
```

- **Any** future implementation (rule-based from closing ranks, logistic
  regression, gradient boosting, neural net, or an ensemble) plugs in here.
- Model versioning is stored on every `Recommendation` (`engine_name`,
  `engine_version`) so outcomes are attributable to a specific model.
- Feature engineering starts from `CandidateProfile.feature_vector()`.
- `PredictionUnavailable` is the sanctioned "cannot score this" path — it is
  downgraded to a `DEGRADED` recommendation with a `data_gap` reason instead
  of a fabricated number.

## 7. Entities vs ORM models (persistence ignorance)

Domain entities (Pydantic) and ORM models (SQLAlchemy) are **separate
classes**. Repositories translate between them.

- Why not SQLAlchemy models directly as entities? Because the domain layer
  would then be coupled to the ORM, breaking clean architecture and making
  unit tests require a database session.
- Cost: a small amount of mapping code in each repository. Worth it.

## 8. Enum strategy

Enums (`Category`, `QuotaType`, `Gender`, `Course`, …) are `StrEnum` in the
domain and stored as **VARCHAR with Python-side validation** (`native_enum=False`),
not native PostgreSQL enums.

Rationale:
- NEET policy changes regularly (new categories, new gender flags). Adding a
  value to a native PG enum is an ALTER TYPE migration on every environment;
  a VARCHAR change is a code deploy.
- All values are validated at the boundary (Pydantic), so corrupt values never
  reach the DB.
- Trade-off: DB does not enforce the value set. The CHECK constraints are
  therefore documented as a Phase 2 hardening option for high-integrity tables
  (e.g. `category` on `allotments`).

## 9. Data model highlights

- `allotments` is the analytic core: one row per published cut-off line, with
  a **unique constraint on (college, year, round, quota, category, gender,
  pwd)** that makes ETL idempotent (`ON CONFLICT DO NOTHING`).
- Composite indexes serve the two hot read paths: per-college history and the
  cohort filter.
- `recommendations` is an immutable audit log: reasons, strategy and choice
  order stored as JSONB, engine provenance included.
- UUID primary keys with `gen_random_uuid()` (PostgreSQL 13+ builtin).

See [docs/data-model.md](data-model.md).

## 10. ETL design

The ingestion framework (`backend/app/infrastructure/etl/`) is built from
four single-responsibility primitives:

```
Source  →  Transformer  →  Validator  →  Loader
 (file)     (normalize)    (contract)   (idempotent upsert)
```

- Sources are thin adapters (Excel/CSV today; MCC scraper, PDF parser later).
- Transformers use a per-release `column_map` because every state and year
  ships different headers.
- Validators use Pydantic and fail **all-or-nothing** — a corrupted release
  must never produce a partial, misleading dataset.
- The loader resolves college codes to ids and upserts in batches.
- Pipelines are declared in `etl/config/pipelines.yaml` and run via
  `etl/run.py`, sharing the backend's models and session.

## 11. Configuration & security

- `pydantic-settings` reads `.env`; `Settings` is a process-wide singleton.
- Secrets live in environment, never in code. `.env` is git-ignored.
- `SECRET_KEY` is seeded for Phase 2 auth but unused today.
- In production: `APP_ENV=production` disables `/docs` and the OpenAPI schema.

## 12. Testing strategy

- Unit tests cover domain invariants and use-case orchestration with fakes
  (no DB).
- ETL transformer/validator logic is tested on in-memory data.
- Integration tests (real Postgres, real HTTP) live under `tests/` and are
  the Phase 2+ responsibility.
- Quality gate: `ruff`, `black`, `mypy`, `pytest` (see `Makefile` and CI hook
  in `.pre-commit-config.yaml`).

## 13. Roadmap

- **Phase 2** — REST API on the use cases, persistence of candidates,
  recommendation endpoints, CORS-constrained clients.
- **Phase 2** — real scoring engines: rule-based closing-rank analysis first,
  then statistical/ML models behind the same port.
- **Phase 3** — source scrapers for MCC + state releases, nightly automated
  ETL, drift/quality monitors on the data.
- **Phase 3** — frontend (choice-filling UI), auth, billing.
- **Phase 4** — streaming/columnar analytics for large history, model registry,
  A/B testing of engine versions.

## 14. Feature flag infrastructure

A provider-backed feature flag system lives in `feature_flags/` with
capability gates in `services/` and the flag catalogue in `config/flags.yaml`.
It is **pure infrastructure** — no prediction logic, no business logic, no
frontend. Full API and rationale are documented in
[`feature_flags/README.md`](../feature_flags/README.md).

### 14.1 Sources and precedence

Every flag resolves against a chain of sources, in declared order
(highest wins):

```
ENV  >  MEMORY  >  DATABASE  >  CONFIG_FILE  >  code default (lowest)
```

- **ENV** — `FF_<UPPER_SNAKE>` variables; authoritative kill switches that
  bypass targeting rules.
- **MEMORY** — in-process runtime overrides.
- **DATABASE** — rows in the small `feature_flags` table (runtime toggles).
- **CONFIG_FILE** — `overrides:` in `config/flags.yaml` (deploy baseline).
- **DEFAULT** — the `default:` in each flag definition.

Precedence is declared by source type (`SOURCE_PRECEDENCE` in
`feature_flags/evaluator.py`), never by registration order, so the verdict is
stable no matter how providers are wired.

### 14.2 Dependency injection

`FeatureFlagContainer` (in `feature_flags/container.py`) is the single
composition root: it builds the provider chain from configuration and wires a
singleton `FeatureFlagService`. Consumers (including the `services/` gates)
receive the flag service by constructor. Tests and alternate deployments can
inject their own providers directly — nothing else changes.

### 14.3 Introspection (Sprint 1.2)

`feature_flags/introspection.py` adds a read-only, DI-compatible view over the
same definitions and providers, exposed via
`FeatureFlagContainer.introspection()` (or `build_flag_introspection(...)`).
No UI or REST layer: callers invoke it directly.

`FeatureFlagIntrospection.all_flags()` returns a `FlagIntrospectionReport` —
one `FlagIntrospection` record per flag, sorted by name, exposing:

| Field | Meaning |
| --- | --- |
| `name` / `description` | The flag's identity (from the definition). |
| `current_value` | The resolved verdict (`is_enabled` would agree). |
| `source` / `source_provider` | Winning `FlagSource` + the concrete provider class that decided it. |
| `priority` | Precedence rank of the winning source (0 = ENV … 5 = UNKNOWN). |
| `default_value` | The code/config baseline. |
| `last_modified` | `updated_at` of the DB row when the database owns the flag, else `None`. |
| `environment_override` / `database_override` / `config_override` / `memory_override` | Each source's own value, so the winning override is always traceable. |
| `environment_var` | The exact env variable (`FF_…`) that would control the flag. |

Design points:
- **Same state, no drift.** Introspection reuses the evaluator and the exact
  providers the evaluation path uses; there is no second "display state".
- **Source-agnostic overrides.** Per-source values are collected by
  `FlagSource` via the `FlagProvider` contract, so a future provider (Redis,
  remote flag service) appears in introspection automatically.
- **Time metadata is opt-in.** `FlagProvider.get_updated_at()` defaults to
  `None`; only time-aware providers (the database) override it. Adding a
  timestamp source is a single method override — no interface break.
- **Fail-fast preserved.** Malformed overrides raise typed errors through
  introspection exactly as they do through evaluation.
- **No breaking changes.** `FeatureFlagService`, the gates, and the provider
  contract are unchanged; the `models.py` module became the `models/` package
  (re-exporting the same symbols) to house `models/introspection.py`.
- **Unit tested.** `feature_flags/tests/test_introspection.py` covers the
  catalogue listing, every override source, priority ranking, last-modified
  semantics, unknown-flag policy, evaluation parity, and container wiring.
