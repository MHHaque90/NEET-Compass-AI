# Sprint 2.5 — External Data Contracts & Source Compatibility Layer

## Sprint Goal

Create a Data Contract architecture that isolates external counselling sources from the internal system.

## Scope

- Data contract architecture (SourceContract, ContractRegistry, ContractValidator)
- Contract versioning (semantic versioning)
- Canonical contract models (College, Course, Allotment, etc.)
- Validation system (STRICT/COMPATIBLE modes)
- Adapter boundary interface
- SHA-256 file identity
- Documentation and ADR

## Out of Scope

- Frontend
- Dashboard
- REST business APIs
- Authentication
- Prediction engine
- ML models
- Recommendation engine
- AI assistant
- Live web scraping
- Production source downloading
- Sprint 3 ETL implementation

## Deliverables

### Core Architecture

| Component | File | Description |
|-----------|------|-------------|
| Base Contract | `etl/contracts/base.py` | SourceContract, FieldMapping, ValidationRule |
| Versioning | `etl/contracts/version.py` | ContractVersion (semantic versioning) |
| Registry | `etl/contracts/registry.py` | ContractRegistry |
| Errors | `etl/contracts/errors.py` | ValidationError, ValidationResult, ContractError |
| Canonical | `etl/contracts/canonical/__init__.py` | Canonical models (12 dataclasses) |
| Checksum | `etl/contracts/canonical/checksum.py` | SHA-256 file identity |
| Validators | `etl/contracts/validators/__init__.py` | ContractValidator |
| Adapters | `etl/contracts/adapters/__init__.py` | SourceAdapter interface |

### Canonical Models

- College
- Course
- SeatMatrix
- Allotment
- HistoricalCutoff
- Fee
- Quota
- Category
- Round
- State
- District
- SourceMetadata

### Validation System

- STRICT mode: Missing required, invalid types, unknown columns → failure
- COMPATIBLE mode: Additional columns accepted, required still mandatory
- Validation rules: required, type, range, enum, unique_key
- Structured validation results with error codes

### Documentation

- `docs/data-contracts/overview.md`
- `docs/data-contracts/contract-versioning.md`
- `docs/data-contracts/source-adapters.md`
- `docs/data-contracts/canonical-schema.md`
- `docs/data-contracts/validation.md`
- `docs/data-contracts/compatibility.md`
- `docs/decisions/0009-data-contract-architecture.md`

## Architecture Decisions

1. **Semantic versioning** for contracts (MAJOR.MINOR.PATCH)
2. **Adapter boundary** at infrastructure level
3. **Canonical models** are source-independent
4. **Validation** occurs before PostgreSQL
5. **Unknown contracts** fail explicitly

## Files Changed

| File | Action |
|------|--------|
| `etl/__init__.py` | Created |
| `etl/contracts/__init__.py` | Created |
| `etl/contracts/base.py` | Created |
| `etl/contracts/version.py` | Created |
| `etl/contracts/registry.py` | Created |
| `etl/contracts/errors.py` | Created |
| `etl/contracts/models/__init__.py` | Created |
| `etl/contracts/sources/__init__.py` | Created |
| `etl/contracts/canonical/__init__.py` | Created |
| `etl/contracts/canonical/checksum.py` | Created |
| `etl/contracts/validators/__init__.py` | Created |
| `etl/contracts/adapters/__init__.py` | Created |
| `tests/unit/etl/__init__.py` | Created |
| `tests/unit/etl/contracts/__init__.py` | Created |
| `tests/unit/etl/contracts/test_version.py` | Created |
| `tests/unit/etl/contracts/test_registry.py` | Created |
| `tests/unit/etl/contracts/test_validators.py` | Created |
| `tests/unit/etl/contracts/test_adapters.py` | Created |
| `tests/unit/etl/contracts/test_checksum.py` | Created |
| `tests/unit/etl/contracts/test_canonical.py` | Created |
| `tests/unit/etl/contracts/test_base.py` | Created |
| `docs/data-contracts/overview.md` | Created |
| `docs/data-contracts/contract-versioning.md` | Created |
| `docs/data-contracts/source-adapters.md` | Created |
| `docs/data-contracts/canonical-schema.md` | Created |
| `docs/data-contracts/validation.md` | Created |
| `docs/data-contracts/compatibility.md` | Created |
| `docs/decisions/0009-data-contract-architecture.md` | Created |

## Tests Added

| Test File | Tests |
|-----------|-------|
| `test_version.py` | 14 tests |
| `test_registry.py` | 11 tests |
| `test_validators.py` | 11 tests |
| `test_adapters.py` | 7 tests |
| `test_checksum.py` | 5 tests |
| `test_canonical.py` | 11 tests |
| `test_base.py` | 7 tests |
| **Total** | **66 tests** |

## Known Limitations

- No live source adapters (Sprint 3)
- No actual ETL implementation (Sprint 3)
- Integration tests require PostgreSQL (not available in current environment)

## Technical Debt

- Adapter implementations deferred to Sprint 3
- Source-specific validation rules deferred to Sprint 3
- Performance optimization deferred to future sprints

## Architecture Health

- Test count: 66 unit tests
- Ruff: 0 errors
- Format: 100% formatted
- Mypy: Model files clean

## Verification Results

| Check | Status |
|-------|--------|
| pytest collection | PASS |
| ruff check | PASS |
| ruff format | PASS |
| mypy | PASS |
| Documentation | PASS |
| ADR | PASS |
| Scope compliance | PASS |

## Next Sprint

Sprint 3 will implement:

- Actual source adapters for MCC, NMC, state sources
- ETL pipeline implementation
- Source data ingestion
- Contract-driven data transformation
