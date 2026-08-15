# NEET Compass AI

**Admission Intelligence Platform** — recommend the best MBBS/BDS colleges for
any NEET candidate from historical counselling data, with probability,
expected counselling round, confidence, counselling strategy, choice-filling
order, and an explanation for every recommendation.

> **Phase 1 status:** complete repository scaffold, clean layered architecture,
> database schema + migrations, ETL pipeline framework, ML integration seam,
> and the test/quality toolchain. No prediction logic, no frontend, and no
> product APIs yet — by design (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).

---

## Repository layout

```
neet-compass-ai/
├── backend/            FastAPI service (clean architecture, see below)
│   ├── app/
│   │   ├── core/           config, logging, DB session
│   │   ├── domain/         entities, enums, ports (pure business logic)
│   │   ├── application/    use cases + DI container
│   │   ├── infrastructure/ SQLAlchemy, repositories, ETL, ML seam
│   │   └── api/            FastAPI wiring (Phase 2 routes)
│   ├── alembic/            database migrations
│   └── tests/              backend unit tests
├── feature_flags/      provider-backed feature flag engine (incl. introspection)
│   ├── models/             flag definitions + introspection snapshots
│   ├── providers/          env / memory / database / config-file sources
│   └── tests/              flag system unit tests
├── services/           capability gates for the Rule / ML / LLM / Experimental engines
├── config/             flags.yaml (flag catalogue + deploy-baseline overrides)
├── frontend/           placeholder (no frontend in Phase 1)
├── database/           SQL notes / seed material
├── etl/                pipeline definitions + CLI runner
├── scripts/            entrypoint / bootstrap helpers
├── tests/              repo-wide integration tests (Phase 2+)
├── docs/               architecture & data-model docs
├── docker/             docker-specific config
├── data/               raw/ processed/ exports/ cache/ (git-ignored)
├── requirements.txt    runtime deps
├── requirements-dev.txt dev/test/quality deps
├── pyproject.toml      tooling config (ruff, black, pytest, mypy)
├── docker-compose.yml
├── Makefile
├── .pre-commit-config.yaml
└── .env.example
```

## Quick start (local dev)

Prerequisites: Python 3.12+, Docker, Make.

```bash
# 1. Environment
cp .env.example .env

# 2. Database + cache
make db-up

# 3. Virtualenv with dev deps
make setup

# 4. Create the dev database, apply migrations
scripts/bootstrap_db.sh
make migrate

# 5. Run the API (health probe only in Phase 1)
make dev        # http://localhost:8000/docs
```

## Docker (full stack)

```bash
cp .env.example .env
docker compose up -d --build
# backend runs migrations on start, then serves http://localhost:8000
```

## Quality gate

```bash
make check        # lint + format-check + typecheck + tests
make test         # pytest with coverage
```

## Key design principles

- **Clean architecture.** Domain → application → infrastructure → api. Inner
  layers never import outer layers; infrastructure implements the *ports*
  (interfaces) the application declares (SOLID D/I).
- **No fabricated predictions.** The default engine (`unavailable`) refuses to
  score. A real engine is registered via the `RecommendationEngine` port and
  selected with `ML_RECOMMENDATION_ENGINE`. Predictions can never be invented.
- **Explainability by construction.** Every recommendation carries an
  auditable trail of reasons, strategy, and engine provenance.
- **Automated ETL.** A pluggable `Source → Transformer → Validator → Loader`
  pipeline ingests MCC/state cut-off releases idempotently.
- **Everything environment-driven.** Configuration lives in
  `backend/app/core/config.py`, overridable via `.env`.

## Feature flags

Provider-backed feature flag infrastructure (pure infrastructure, no
prediction/business logic): flags toggle the **Rule**, **ML**, and **LLM**
engines and per-feature **experimental** rollouts. Three toggle sources —
environment variables, the database, and `config/flags.yaml` — are resolved
by declared precedence, and an **introspection** service lists every flag
with its resolved value, winning source, priority, and per-source overrides.

See [feature_flags/README.md](feature_flags/README.md) for usage and the full
architectural rationale.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — every architectural decision and rationale
- [Data model](docs/data-model.md) — schema, enums, indexing
- [ETL](etl/README.md) — pipeline configuration and usage
- [Roadmap](docs/ARCHITECTURE.md#roadmap) — Phase 2+ scope
