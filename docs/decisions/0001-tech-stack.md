# ADR-001: Technology Stack

- **Status:** Accepted (Sprint 1)
- **Date:** 2026-08-08
- **Deciders:** Lead Architect, Backend Team
- **Category:** Technology

## Context

NEET Compass AI requires a technology stack that ensures:

1. **Fully open-source** — no paid software, no proprietary SDKs, no cloud lock-in
2. **Self-hostable** — runs on commodity hardware, no cloud dependency
3. **Versioned and modular** — clean architecture, easy to swap components
4. **Production database** — PostgreSQL for relational integrity and analytics
5. **Explainable predictions** — full audit trail of every decision
6. **Automated** — CI/CD, testing, linting, formatting

The team evaluated multiple stacks and needed consensus on the final selection.

## Decision

We choose the following technology stack:

### Core Runtime
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.12 | Mature ecosystem, type hints, async support, strong data libraries |
| Web Framework | FastAPI | Native async, OpenAPI generation, dependency injection, automatic validation |
| ASGI Server | Uvicorn[standard] | Production-grade ASGI server with standard extras |

### Data Layer
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Database | PostgreSQL 16 | ACID, UUIDs, JSONB, mature ecosystem, open source |
| ORM | SQLAlchemy 2.x | Mature, flexible, clean architecture support, Alembic integration |
| Migrations | Alembic | Industry standard for SQLAlchemy migrations |
| Driver | psycopg[binary] | Official PostgreSQL adapter for Python |

### Data Processing
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Data Processing | pandas | Industry standard for data manipulation |
| Numerical Computing | numpy | Foundation for pandas and ML libraries |
| Configuration | PyYAML | YAML parsing for pipeline configs |

### Validation & Configuration
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Validation | Pydantic v2 | Fast, type-safe validation, FastAPI native |
| Configuration | pydantic-settings | Environment-driven config with validation |
| Environment | python-dotenv | .env file support |

### ML & Analytics
| Component | Choice | Rationale |
|-----------|--------|-----------|
| ML Framework | TBD (seam ready) | Default: unavailable engine; pluggable architecture |

### Testing
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Test Runner | pytest | Industry standard, fixtures, plugins |
| Coverage | pytest-cov | Coverage reporting |

### Code Quality
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Linter | ruff | Fast, single-tool replacement for flake8, isort, etc. |
| Formatter | black | Opinionated, widely adopted formatter |
| Type Checker | mypy | Static type checking with Pydantic plugin |
| Pre-commit | pre-commit | Git hooks for quality gates |

### DevOps
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Containerization | Docker | Standard container format |
| Orchestration | Docker Compose | Local development, simple deploys |
| Build Automation | Makefile | Simple, portable, no extra dependencies |

### Logging
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Structured Logging | python-json-logger | JSON log output for parsing |

## Consequences

### Positive
- All tools are free and open-source
- Strong type safety through Pydantic and mypy
- Clean separation between domain, application, and infrastructure
- Alembic migrations integrated with the SQLAlchemy model metadata
- FastAPI provides automatic OpenAPI documentation
- Testing framework is comprehensive and fast

### Negative
- Python GIL limits CPU-bound parallelism (mitigated by PostgreSQL for heavy lifting)
- Native Python is slower than compiled languages for pure compute (ML is delegated to the model engine seam)

### Neutral
- The ML framework is intentionally deferred — a pluggable port allows any future framework
- python-dotenv is only for local development; production uses real environment variables

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [ADR-002: Folder Structure](0002-folder-structure.md)
- [ADR-003: Database Design](0003-database-design.md)
