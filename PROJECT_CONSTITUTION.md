# Project Constitution

## 1. Mission

Build the world's first fully open-source, self-hostable, AI-powered,
Explainable Admission Intelligence Platform for NEET Counselling.

## 2. Vision

To democratize access to quality medical education information by providing
every NEET aspirant — regardless of their economic background — with
transparent, explainable, and trustworthy college recommendations based on
historical data and AI-powered analysis.

## 3. Core Values

| Value | Description |
|-------|-------------|
| Free | Completely free to use, modify, and distribute |
| Open Source | All code under MIT License |
| Self Hostable | Runs on commodity hardware, no cloud dependency |
| Explainable | Every prediction includes full explanation |
| Modular | Components are replaceable without breaking the system |
| Automated | CI/CD, testing, linting, and formatting automated |
| Versioned | All data, models, and code versioned for reproducibility |
| Inclusive | Accessible to all NEET aspirants regardless of background |

## 4. Coding Standards

### Style Guide
- Formatter: Black (line length 100)
- Linter: Ruff (comprehensive ruleset)
- Type Checker: Mypy strict mode
- Naming: PEP 8 compliant

### Code Quality Standards
- Type hints required on all functions and methods
- Docstrings required on all public modules, classes, and methods
- SOLID principles enforced
- Clean Architecture layers
- Repository Pattern for data access
- Dependency Injection via composition root
- No TODO comments
- No placeholder code

### Commit Standards
- Conventional Commits format
- DCO (Developer Certificate of Origin) sign-off required
- Small, focused commits

### PR Standards
- Description of changes
- Testing approach
- Breaking changes noted
- One approval required (two for schema changes)

## 5. Architecture Principles

### 5.1 Layer Isolation
- Domain layer: Zero external dependencies (only stdlib + Pydantic)
- Application layer: Depends on domain only
- Infrastructure layer: Implements domain ports
- API layer: Depends on application services

### 5.2 No Vendor Lock-in
- All tools are FOSS
- No paid APIs
- Self-hostable on commodity hardware
- Database is PostgreSQL (standard SQL)
- ML engine is pluggable

### 5.3 Explainability by Construction
- Every recommendation carries reasons, strategy, and engine provenance
- Full audit trail in predictions, prediction_history, logs
- No black-box predictions — every decision is traceable

### 5.4 Data Versioning
- Every prediction is reproducible from a specific dataset + model
- Versioning tracked on: data_sources, source_files, etl_runs, model_versions, predictions

### 5.5 Idempotency
- ETL operations use ON CONFLICT DO NOTHING
- Re-running ETL does not create duplicates
- Re-running migrations is safe

## 6. Review Process

### Code Review
1. Author opens PR with DCO sign-off
2. CI runs: ruff, black, mypy, pytest
3. At least 1 reviewer approves
4. Schema changes require 2 approvals
5. Merge via squash

### Architecture Review
1. New architecture decisions require an ADR
2. ADR reviewed by architecture committee (Lead Architect + 2 maintainers)
3. Vote: simple majority to accept
4. ADR merged to main before implementation

### Security Review
1. All new dependencies reviewed for security posture
2. Secrets scanning in CI
3. Dependencies checked for CVEs
4. Security-sensitive changes require security review

## 7. Sprint Workflow

### Sprint Structure
- Duration: 1 week (Monday-Friday)
- Planning: Monday (90 minutes)
- Standup: Async (team updates in project board)
- Review: Friday (demo + retrospective)
- Retrospective: Friday (1 hour)

### Quality Gates (per sprint)
- Ruff lint: 0 errors
- Black format: 100%
- Mypy strict: 0 errors
- Pytest: all tests pass
- Coverage: meets thresholds (80% domain/core, 60% tests)

### Definition of Done
A feature/change is complete when:
1. Code is written with type hints and docstrings
2. Tests are written and passing
3. Lint passes (ruff)
4. Format is correct (black)
5. Types are validated (mypy strict)
6. Documentation is updated
7. ADR created (if architectural decision)
8. Sprint report updated
9. Git commit with DCO sign-off
10. Architecture health score updated

## 8. Branch Strategy

- **main** — protected, production-ready
- **feature/** — feature development (short-lived, max 3 days)
- **hotfix/** — urgent production fixes
- **release/** — release preparation

Rules:
- Never commit directly to main
- PRs must pass CI before merge
- DCO sign-off required on all commits
- Squash and merge only

## 9. Version Strategy

- Semantic Versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes (schema, API)
- MINOR: New features, non-breaking
- PATCH: Bug fixes, non-breaking
- Pre-release tags: 0.x.y (project is pre-1.0)
- Tags created at end of each sprint

## 10. Backlog Policy

### Product Backlog
- Prioritized by impact x effort
- User stories follow: "As a [role], I want [feature] so that [benefit]"
- Technical debt items labeled and prioritized alongside features

### Technical Debt
- Addressed in every sprint (minimum 10% capacity)
- Logged in sprint reports
- Tracked in ARCHITECTURE_HEALTH.md
- Must have associated ADR if architectural

### Sprint Backlog
- Committed on Monday during planning
- Can be adjusted during the week if scope changes
- Reviewed and completed by Friday

## 11. Roadmap Policy

- Roadmap updated each sprint
- Phase boundaries are firm; dates are estimates
- Community input welcomed via GitHub Discussions
- Roadmap lives in ROADMAP.md

## 12. Improvement Policy

- Retrospectives every Friday
- Architecture health reviewed each sprint
- Metrics tracked: test coverage, lint errors, mypy errors, architecture debt
- Continuous improvement is part of every sprint plan
