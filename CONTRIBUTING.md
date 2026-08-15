# Contributing to NEET Compass AI

First and foremost — **thank you** for taking the time to contribute!

This document outlines the process for contributing to NEET Compass AI.
Following these guidelines ensures a high-quality, maintainable codebase.

## Developer Certificate of Origin (DCO)

By contributing to this project, you agree that your contributions are made
under the **Developer Certificate of Origin (DCO)**. You must sign-off on
every commit by adding a `Signed-off-by` line to your commit message:

```
commit abc1234
Author: Your Name <you@example.com>
Date:   Mon Aug 10 12:00:00 2026 +0000

    fix: resolve null pointer in recommendation service

    Signed-off-by: Your Name <you@example.com>
```

The sign-off line must use your **real name** and the email address
associated with your commits. This certifies that you have the right to
submit the contribution under the MIT License.

**DCO Sign-off is mandatory for all commits.** Pulls without sign-off will
be rejected by CI.

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Make (or equivalent build tool)

### Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/neet-compass/neet-compass-ai.git
cd neet-compass-ai

# 2. Set up environment
cp .env.example .env
# Edit .env with your local settings

# 3. Start the database
make db-up

# 4. Set up the virtual environment
make setup

# 5. Apply migrations
make migrate
```

## Development Workflow

### Branch Strategy

We use **Trunk-Based Development** with short-lived feature branches:

```
main (protected)
├── feature/JIRA-123-add-states-table
├── feature/JIRA-456-improve-indexing
└── hotfix/JIRA-789-fix-bug-in-etl
```

**Rules:**
- Branch name format: `type/JIRA-N-description` (e.g., `feature/ENG-42-add-districts`)
- Keep branches short-lived (max 3 days)
- Rebase onto `main` daily
- Delete branches after merge

### Commit Messages

We follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code refactoring (no behavior change)
- `perf` — Performance improvement
- `test` — Test additions/updates
- `docs` — Documentation changes
- `chore` — Build/CI/tooling changes
- `ci` — CI configuration changes
- `style` — Formatting/linting changes

**Examples:**
```
feat(database): add states and districts tables

Implement lookup tables for Indian states and union territories.
Includes seed data for all 28 states and 8 UTs.

Fixes: ENG-112
```

```
fix(etl): handle missing column in MCC cut-off releases

Closes: ENG-87
```

### Pull Request Process

1. **Open a PR** from your feature branch to `main`
2. **Fill the template** — describe what you changed and why
3. **Pass all CI checks** — ruff, black, mypy, pytest
4. **Get one approval** from a maintainer (two for schema changes)
5. **DCO sign-off** required on all commits
6. **Merge** — PR is squash-merged by maintainer

### PR Template

```markdown
## Description
<!-- Describe what this PR does -->

## Changes
<!-- List of changes -->

## Testing
<!-- How was this tested? -->

## Related Issues
<!-- Link to issues: Fixes #123 -->
```

## Code Standards

### Style

- **Black** for formatting (line length 100)
- **Ruff** for linting (see pyproject.toml for rules)
- **Mypy strict** for type checking
- **PEP 8** compliance enforced via tooling

### Architecture

- **Clean Architecture** — Domain → Application → Infrastructure → API
- **Repository Pattern** — Data access via repository interfaces
- **Dependency Injection** — Services receive dependencies via constructor
- **Single Responsibility** — One reason to change per class
- **No circular imports** between modules

### Type Hints

All Python code must use type hints:
- All function parameters and return types annotated
- `from __future__ import annotations` in all files
- `Mapped[str]` for SQLAlchemy model fields
- `StrEnum` for domain enums

### Docstrings

- All public modules, classes, and methods must have docstrings
- Use Google-style docstring format
- Include parameter types and descriptions

### Testing

- **Unit tests** — domain logic and use cases (no DB)
- **Integration tests** — database, HTTP, ETL pipelines (real DB)
- **Coverage gate** — 80% for domain/core; 60% for tests
- **Test names** — descriptive, e.g., `test_candidate_profile_validates_category`
- **Fixtures** — use pytest fixtures, no hardcoded data in tests

### Database

- Every table must have: PK, FK (where appropriate), indexes, constraints
- Every table must have: created_at, updated_at
- Soft delete support where appropriate (deleted_at)
- Unique constraints for idempotency
- Document every relationship

## Architecture Review Process

### When to Submit an ADR

- Any architectural decision that affects multiple components
- New technology choices
- Schema design changes
- API design decisions
- Breaking changes to existing interfaces

### ADR Format

Use the MADR (Markdown Architectural Decision Records) format. See
`docs/decisions/` for examples.

### Review Process

1. **Submit draft ADR** as a PR
2. **Architecture review meeting** scheduled within 48 hours
3. **Feedback incorporated** into the ADR
4. **Voting** — simple majority of maintainers
5. **Accepted/Rejected/Supended** status set
6. **ADR merged** to main

## Sprint Review Process

### Weekly Sprints

- Sprints are 1 week long (Mon-Fri)
- Sprint planning on Monday
- Daily standups (async — update sprint board)
- Sprint review on Friday
- Sprint retrospective on Friday

### Quality Gates

Every sprint must pass:
- Ruff lint: 0 errors
- Black format: 100%
- Mypy strict: 0 errors
- Pytest: all tests pass
- Coverage: meets thresholds

### Sprint Deliverables

- Code committed and merged
- Tests written and passing
- Documentation updated
- Sprint report completed
- ADR (if applicable)

## Getting Help

- **GitHub Discussions** — for questions and community support
- **GitHub Issues** — for bug reports and feature requests
- **Slack/Discord** — for real-time discussion (link in README)

## Code of Conduct

By participating in this project, you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Recognition

Contributors are listed in the [AUTHORS](AUTHORS) file. Sponsors are
acknowledged in [SPONSORS](SPONSORS.md).

---

Thank you for contributing to NEET Compass AI!
