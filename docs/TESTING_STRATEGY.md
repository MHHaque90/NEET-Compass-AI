# Testing Strategy

> See `pyproject.toml` for pytest configuration. Run `pytest --co -q` to
> list all test IDs.

---

## Test Pyramid

```
   156 tests
  ┌─────────────────────────────────────┐
  │  Integration Tests  (pytest)  45 % │
  │  Real Postgres via pytest-postgresql│
  │  Full-stack: API → DB → Assertions │
  └─────────────────────────────────────┘
  ┌─────────────────────────────────────┐
  │  Unit Tests  (pytest)  50 %         │
  │  Pure Python, no I/O                │
  │  Fast feedback (<1s per test)       │
  └─────────────────────────────────────┘
  ┌─────────────────────────────────────┐
  │  Contract Tests  (schemathesis) 5% │
  │  Property-based testing of API      │
  │  Fuzzes endpoints for edge cases    │
  └─────────────────────────────────────┘
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

Pure functions and classes with no I/O. Use pytest fixtures and
`unittest.mock` for mocking.

| File | Coverage |
|---|---|
| `test_database_models.py` | Model creation, field defaults, relationship loading |
| `test_domain_enums.py` | Enum value coverage, serialization |
| `test_utils.py` | Utility functions (pagination, checksums, etc.) |

**Run:** `pytest tests/unit/ -q`

### Integration Tests (`tests/integration/`)

Real PostgreSQL database (via `pytest-postgresql`) and real Redis.

| File | Coverage |
|---|---|
| `test_database_constraints.py` | Unique constraints, FK enforcement |
| `test_migration.py` | Alembic migration up/down, table counts |
| `test_api_prediction.py` | Prediction endpoint happy/edge paths |
| `test_api_auth.py` | Login, register, token refresh, logout |
| `test_api_colleges.py` | Filtering, pagination, detail endpoint |
| `test_celery_etl.py` | ETL task execution, error handling |
| `test_celery_ml.py` | Model training task lifecycle |

**Run:** `pytest tests/integration/ -q`

### Contract Tests (`tests/contract/`)

Schema-based property testing using `schemathesis` against the OpenAPI spec.

| File | Coverage |
|---|---|
| `test_api_contract.py` | Fuzz-testing all endpoints with random inputs |

**Run:** `pytest tests/contract/ -q`

---

## Test Configuration

### Fixtures

Shared fixtures live in `tests/conftest.py`:

- `session` — SQLAlchemy async session with transaction rollback after each test.
- `pg_engine` — PostgreSQL async engine, created per-test for isolation.
- `client` — FastAPI `TestClient` with mocked auth tokens.
- `db_session` — Synchronous SQLAlchemy session for Celery tests.

### Test Data Factory

A `TestDataFactory` class generates valid model instances with randomized
but valid data (using `faker`), reducing boilerplate in tests.

```python
@pytest.fixture()
def college_factory():
    def _create(**kwargs):
        return CollegeModel(**TestDataFactory.college(**kwargs))
    return _create
```

### Mocking Strategy

- **External APIs:** All HTTP calls to external services (MCC, state APIs)
  are mocked using `respx` or `responses`.
- **Email/SMS:** Mocked via `unittest.mock.patch`.
- **Redis:** `fakeredis` for unit tests; real Redis for integration tests.

---

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/tests.yml`):

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:16, ... }
      redis: { image: redis:7-alpine, ... }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -q --cov
      - run: pytest tests/integration/ -q
      - run: pytest tests/contract/ -q
      - run: mypy backend/app/
      - run: ruff check backend/ tests/
      - run: python -m pytest --cov-fail-under=85
      - run: ruff format --check backend/ tests/
```

Quality gates:
- Coverage >= 85% (unit + integration combined).
- `ruff` linting passes.
- `mypy` type checking passes.
- `ruff format` check passes.

---

## Local Development

### Prerequisites
- Python 3.11+
- Docker (for PostgreSQL and Redis)
- Pre-commit hooks installed: `pre-commit install`

### Running Tests Locally

```bash
# Start dependencies
docker compose up -d postgres redis

# Run all unit + integration tests
pytest

# Run only unit tests (fast)
pytest tests/unit/

# Run with coverage
pytest --cov=backend/app --cov-report=term-missing

# Run specific test file
pytest tests/integration/test_api_prediction.py -v

# Run with parallel workers
pytest -n auto

# Lint + format
pre-commit run --all-files
```

---

## Writing New Tests

1. **Unit test:** Add to `tests/unit/test_<module>.py`.
2. **Integration test:** Add to `tests/integration/test_<feature>.py`.
3. **Contract test:** Add cases to `tests/contract/test_api_contract.py`.

### Best Practices

- Use descriptive test names: `test_get_college_returns_fee_when_...`
  not `test_college_2`.
- Arrange-Act-Assert pattern for readability.
- Prefer explicit assertions over `assert x == 42`; use
  `assert response.json() == CollegeSchema(...)` or
  `assert response.status_code == HTTP_200_OK`.
- Database tests must not share state; use `rollback` or `truncate`.
- Integration tests should test through the API layer, not the
  repository layer directly (except for ETL tests).

---

## Test Coverage Targets

| Layer | Target | Current |
|---|---|---|
| Domain models | 100% | 100% |
| Repositories | 95% | 95% |
| Services | 90% | 88% |
| API endpoints | 95% | 92% |
| ETL tasks | 85% | 85% |
| Overall | 85% | 87% |
