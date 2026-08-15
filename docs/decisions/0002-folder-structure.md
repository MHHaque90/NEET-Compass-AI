# ADR-002: Folder Structure

- **Status:** Accepted (Sprint 1)
- **Date:** 2026-08-08
- **Deciders:** Lead Architect, Backend Team
- **Category:** Architecture

## Context

The project requires a clear, maintainable folder structure that enforces
clean architecture, separates concerns, and guides developers to the right
place for each kind of code. The structure must support:

1. **Clean Architecture** — domain independence from infrastructure
2. **Modular growth** — easy to add new engines, sources, pipelines
3. **Testability** — clear boundaries between unit and integration tests
4. **Infrastructure as code** — Docker, migrations, CI/CD
5. **Documentation** — centralized, versioned, and discoverable
6. **Open source conventions** — LICENSE, README, CONTRIBUTING, etc.

Multiple structure approaches were considered:

- **Flat layout** — all files in a single package, simple but doesn't scale
- **Domain-driven layout** — organized by domain feature, good for small apps
- **Clean architecture layered layout** — separates by architectural layer
- **Hybrid layout** — combines layer + module organization

## Decision

We adopt a **hybrid layered + module layout** that prioritizes clean
architecture boundaries while grouping related functionality:

```
neet-compass-ai/                    # Repository root
├── backend/                        # Backend service
│   ├── app/                        # Application code
│   │   ├── core/                   # Infrastructure: config, logging, DB
│   │   ├── domain/                 # Pure business logic (entities, ports, enums)
│   │   ├── application/            # Use cases + DI composition root
│   │   ├── infrastructure/         # Adapters (DB, ETL, ML)
│   │   │   ├── db/                 # SQLAlchemy models + repositories
│   │   │   ├── etl/                # ETL pipeline framework
│   │   │   └── ml/                 # ML engine seams
│   │   └── api/                    # FastAPI routes (v1, v2, ...)
│   ├── alembic/                    # Database migrations
│   │   ├── versions/               # Migration scripts
│   │   └── env.py                  # Migration environment
│   ├── tests/                      # Backend tests
│   │   ├── unit/                   # Unit tests (no DB)
│   │   └── integration/            # Integration tests (real DB)
│   ├── Dockerfile                  # Backend container
│   └── alembic.ini                 # Alembic CLI config
├── feature_flags/                  # Feature flag engine
│   ├── models/                     # Flag definitions
│   ├── providers/                  # Value sources (env, memory, db, file)
│   └── tests/                      # Flag system tests
├── services/                       # Capability gates (rule, ML, LLM, experimental)
├── config/                         # Flag catalogue and deploy configs
├── docker/                         # Docker-specific configuration
├── data/                           # Data directories (git-ignored)
│   ├── raw/                        # Raw source files
│   ├── processed/                  # Cleaned/normalized data
│   ├── exports/                    # Output exports
│   └── cache/                      # Cache directory
├── etl/                            # ETL CLI runner and pipeline configs
├── scripts/                        # Bootstrap and maintenance scripts
├── docs/                           # Documentation
│   ├── decisions/                  # Architecture Decision Records
│   ├── sprints/                    # Sprint reports
│   ├── ARCHITECTURE.md             # Architecture overview
│   ├── DATABASE.md                 # Database design
│   └── ...                         # Other docs
├── requirements.txt                # Runtime dependencies
├── requirements-dev.txt            # Development dependencies
├── pyproject.toml                  # Tooling config (ruff, black, pytest, mypy)
├── docker-compose.yml              # Service orchestration
├── Makefile                        # Build automation
├── .env.example                    # Environment template
├── .gitignore                      # Ignore patterns
├── .dockerignore                   # Docker ignore
├── .pre-commit-config.yaml         # Pre-commit hooks
├── README.md                       # Project overview
├── LICENSE                         # MIT License
├── SECURITY.md                     # Security policy
├── CONTRIBUTING.md                 # Contribution guidelines
├── CHANGELOG.md                    # Change log
├── ROADMAP.md                      # Project roadmap
├── INSTALLATION.md                 # Installation guide
├── CODE_OF_CONDUCT.md              # Code of conduct
├── PROJECT_CONSTITUTION.md         # Formal project constitution
├── API_SPEC.md                     # API specification
├── ETL_SPEC.md                     # ETL specification
├── PREDICTION_SPEC.md              # Prediction specification
├── DATA_DICTIONARY.md              # Data dictionary
├── ARCHITECTURE_HEALTH.md          # Architecture health tracking
└── ARCHITECTURE.md                 # Main architecture document
```

### Layer Isolation Rules

1. **`backend/app/core/`** — No imports from any other app subpackage except infrastructure adapters it wires
2. **`backend/app/domain/`** — Zero external imports. Only stdlib + Pydantic. Never imports application, infrastructure, or api.
3. **`backend/app/application/`** — Imports domain only. Imports concrete infrastructure via dependency injection in the container.
4. **`backend/app/infrastructure/`** — Imports domain (to implement ports) and core. Never imports application or api.
5. **`backend/app/api/`** — Imports application services and core. Never imports domain entities directly.

### File Naming Conventions

- Models: `<entity>.py` (snake_case, singular)
- Repositories: `sqlalchemy_<entity>_repository.py`
- Services: `<entity>_service.py`
- Tests: `test_<module>.py`
- Migrations: `<revision_id>_<description>.py`

### Documentation Conventions

- All ADRs use MADR (Markdown Architectural Decision Records) format
- Sprint reports follow a standardized template
- All docs have a single source of truth per topic

## Consequences

### Positive
- Clear separation of concerns enforces clean architecture boundaries
- Developers know exactly where to put new code
- Testing boundaries are explicit (unit vs integration)
- Easy to replace components (swap SQLAlchemy repo, swap ETL source)
- Documentation is centralized and discoverable

### Negative
- Deeper directory nesting means more path typing
- Some duplication between domain enums and infrastructure model enums
- The `data/` directory uses significant disk space (git-ignored, but still)

### Neutral
- The `frontend/` directory is intentionally a placeholder
- The `etl/` directory is separate from `backend/app/infrastructure/etl/` to allow CLI usage
- The `scripts/` directory is for bootstrap only; complex scripts go in `backend/`

## References

- [ADR-001: Technology Stack](0001-tech-stack.md)
- [ADR-003: Database Design](0003-database-design.md)
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
