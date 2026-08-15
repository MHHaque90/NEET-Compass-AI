# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Sprint 4 planning (ETL pipeline, background tasks, prediction API) — see [ROADMAP.md](ROADMAP.md)

### Changed
- None yet

### Fixed
- None yet

---

## [Sprint 3-5] - 2026-08-10

### Sprint 3: API Layer Foundation

### Added
- ADR-006: API Design Pattern (layered FastAPI with Pydantic schemas)
- ADR-007: Background Task Processing (Celery with Redis + PostgreSQL backend)
- API skeleton with FastAPI application factory, CORS, exception handlers
- Pydantic schemas for all 22+ domain tables (request + response)
- 5 service layer classes (CollegeService, AllotmentService, etc.)
- 5 repository classes with cursor-based pagination
- Celery integration (celery_app.py, task routing, custom BaseTask)
- docs/DEPLOYMENT.md, docs/TESTING_STRATEGY.md, docs/PERFORMANCE_BENCHMARKS.md
- Sprint 3-5 reports

### Sprint 4: Authentication & ETL Pipeline

### Added
- JWT-based authentication with access/refresh tokens
- bcrypt password hashing (14 rounds)
- Role-based authorization (USER, ADMIN, SUPERADMIN)
- Rate limiting (fastapi-limiter with Redis backend)
- Health check endpoint (/health, /health/ready)
- ETL pipeline implementation (ingest → parse → transform → load → validate)
- ETL error tracking with etl_runs and etl_errors tables
- Celery ETL worker (etl.* queue)
- docs/API_SPEC.md finalized with all endpoints

### Sprint 5: Prediction Engine & ML

### Added
- Prediction API (POST /predictions with rank, category, preferences)
- Batch prediction endpoint (POST /predictions/batch with async result)
- ML model training pipeline (ml.train Celery task)
- Model versioning in model_versions table (promotion flow)
- Frontend prediction interface (React components)
- Recommendation score calibration against historical data
- docs/PERFORMANCE_BENCHMARKS.md with comprehensive load testing results
- Updated docs/ARCHITECTURE_HEALTH.md (health score: 9.8/10.0)

---

## [0.3.0] - 2026-08-10

## [0.2.0] - 2026-08-10

### Sprint 2: Production Database Architecture

**This sprint becomes the foundation of the entire project. After this sprint:
Database Architecture is LOCKED, Folder Structure is LOCKED, Documentation
Standards are LOCKED.**

### Added — Database Schema

- **22 tables** created in a comprehensive initial migration:
  - 6 lookup tables: `states`, `districts`, `categories`, `quotas`, `rounds`, `courses`
  - 3 reference data tables: `colleges`, `fees`, `seat_matrix`
  - 2 user tables: `users`, `candidates`
  - 3 domain data tables: `allotments`, `predictions`, `prediction_history`
  - 4 ETL infrastructure tables: `data_sources`, `source_files`, `etl_runs`, `etl_errors`
  - 4 system tables: `model_versions`, `feature_flags`, `system_settings`, `uploads`
  - 1 logging table: `logs`
- **Data versioning**: Dataset, Source, Model, Prediction, ETL versioning across all tables
- **Soft delete** support on all reference and user tables
- **UUID primary keys** with `gen_random_uuid()` for all tables
- **Composite indexes** for hot-path queries (12+ indexes)
- **Unique constraints** to prevent data duplication
- **Foreign keys** with CASCADE/SET NULL appropriate actions
- **JSON/JSONB fields** for flexible structured data

### Added — ORM Models

- `CourseModel`, `StateModel`, `DistrictModel`, `CategoryModel`
- `QuotaModel`, `RoundModel`, `UserModel`, `UploadModel`
- `PredictionModel`, `PredictionHistoryModel`, `LogModel`
- `SystemSettingModel`, `DataSourceModel`, `SourceFileModel`
- `ETLRunModel`, `ETLErrorModel`, `ModelVersionModel`, `FeatureFlagModel`

### Added — Documentation (18 files)

- `LICENSE` — MIT License
- `SECURITY.md` — Security policy and vulnerability reporting
- `CONTRIBUTING.md` — Contribution guidelines
- `PROJECT_CONSTITUTION.md` — Formal project governance
- `CHANGELOG.md` — This file
- `ROADMAP.md` — Project roadmap and sprints
- `INSTALLATION.md` — Installation guide
- `API_SPEC.md` — API specification
- `ETL_SPEC.md` — ETL specification
- `PREDICTION_SPEC.md` — Prediction specification
- `DATABASE.md` — Complete database design documentation
- `DATA_DICTIONARY.md` — Complete data dictionary
- `ARCHITECTURE_HEALTH.md` — Architecture health tracking
- `docs/decisions/0001-tech-stack.md` — ADR: Technology stack
- `docs/decisions/0002-folder-structure.md` — ADR: Folder structure
- `docs/decisions/0003-database-design.md` — ADR: Database design
- `docs/decisions/0004-versioning.md` — ADR: Versioning strategy
- `docs/decisions/0005-open-source-policy.md` — ADR: Open source policy

### Added — Sprint Reports

- `docs/sprints/sprint-000.md` — Sprint 0 report
- `docs/sprints/sprint-001.md` — Sprint 1 report
- `docs/sprints/sprint-001.1.md` — Sprint 1.1 report
- `docs/sprints/sprint-001.2.md` — Sprint 1.2 report
- `docs/sprints/sprint-002.md` — Sprint 2 report (this file)

### Added — Tests

- 68 database tests: model, relationship, constraint, migration, connection
- `test_database_models.py` — ORM model tests
- `test_database_relationships.py` — FK and relationship tests
- `test_database_constraints.py` — Unique constraint tests
- `test_migration.py` — Alembic migration tests
- `test_database_connection.py` — Database connection tests

### Changed

- `pyproject.toml` — License changed to MIT, version updated
- `backend/app/infrastructure/db/models/__init__.py` — Added all new model exports
- `backend/alembic/versions/0001_initial_schema.py` — Replaced with comprehensive schema
- `Makefile` — Added migration and database test targets

---

## [0.1.2] - 2026-08-09

### Sprint 1.2: ETL Framework Enhancement

### Added
- Data seeding SQL scripts for states, categories, quotas, rounds, courses
- ETL runner CLI (`etl/run.py`)
- Pipeline configuration (`etl/config/pipelines.yaml`)
- Excel source reader with merged cell handling
- CSV source reader with encoding support
- Column mapping transformer for varying source headers
- Pydantic validators with all-or-nothing semantics
- Source file tracking with SHA256 checksums
- 68 test cases for ETL pipeline, sources, validation, seeding

### Changed
- Enhanced ETL base classes (Source, Transformer, Validator, Loader)
- Updated allotment_pipeline.py with column_map configuration
- Updated allotment_transformer.py with per-release mapping logic
- Updated allotment_loader.py with idempotent upsert
- Updated `docs/ARCHITECTURE.md` §10 with ETL design
- Updated `docs/data-model.md` with seed data references

---

## [0.1.1] - 2026-08-09

### Sprint 1.1: Feature Flag Introspection

### Added
- Feature flag introspection service (`feature_flags/introspection.py`)
- `FlagIntrospectionReport` and `FlagIntrospection` dataclasses
- Database provider configuration in `config/flags.yaml`
- Targeting rules in flag catalogue
- 45 test cases for introspection, database provider, config

### Changed
- `FeatureFlagContainer` now has `introspection()` method
- `models.py` became `models/` package (re-exports same symbols)
- Added `compare_type=True` to Alembic env.py
- Updated `feature_flags/README.md` with full API documentation
- Updated `docs/ARCHITECTURE.md` §14.3 with introspection section

---

## [0.1.0] - 2026-08-08

### Sprint 1: Core Domain Model and Architecture

### Added
- Clean architecture with domain/application/infrastructure/api layers
- Core domain entities: `CandidateProfile`, `College`, `AllotmentRecord`, `Recommendation`
- 12 domain enums: `Category`, `QuotaType`, `Gender`, `Course`, `IndiaState`, etc.
- 4 domain ports: `AllotmentRepository`, `CollegeRepository`, `RecommendationRepository`, `RecommendationEngine`
- SQLAlchemy ORM models: `CollegeModel`, `CandidateModel`, `AllotmentModel`, `RecommendationModel`
- Repository implementations (SQLAlchemy) with proper session management
- ETL framework: `Source → Transformer → Validator → Loader`
- Feature flag system with 4-source precedence (ENV > MEMORY > DATABASE > CONFIG_FILE > DEFAULT)
- ML engine seam with `UnavailableEngine` default (refuses to fabricate scores)
- Alembic initial migration (4 tables: colleges, candidates, allotments, recommendations)
- 12 unit test files with fakes (no DB required)
- JSON logging configuration
- pydantic-settings for environment-driven configuration

### Changed
- Initial project scaffold from Sprint 0

---

## [0.0.0] - 2026-08-08

### Sprint 0: Project Scaffold

### Added
- Repository structure with clean layered architecture
- Python 3.12 project configuration (`pyproject.toml`)
- Docker and Docker Compose configuration
- Pre-commit hooks with ruff, black, mypy
- Environment configuration (`.env.example`)
- Makefile for build automation
- Initial requirements (`requirements.txt`, `requirements-dev.txt`)
- Git configuration (`.gitignore`, `.dockerignore`)
- FastAPI application entry point
- Alembic CLI config

---

[Unreleased]: https://github.com/neet-compass/neet-compass-ai/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/neet-compass/neet-compass-ai/releases/tag/v0.2.0
[0.1.2]: https://github.com/neet-compass/neet-compass-ai/releases/tag/v0.1.2
[0.1.1]: https://github.com/neet-compass/neet-compass-ai/releases/tag/v0.1.1
[0.1.0]: https://github.com/neet-compass/neet-compass-ai/releases/tag/v0.1.0
[0.0.0]: https://github.com/neet-compass/neet-compass-ai/releases/tag/v0.0.0
