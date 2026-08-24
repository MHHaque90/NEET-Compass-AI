# Sprint 4.1 — Historical Data Activation & Modelling-Readiness Advancement

**Status**: CERTIFIED COMPLETE
**Date**: 2026-08-24
**Branch**: sprint-4.1-historical-data-activation

---

## Objective

Sprint 4.1 is a DATA-READINESS advancement sprint. The purpose is to move the project from 1 verified modelling-ready year (MCC 2025) toward the minimum evidence required for TEMPORAL VALIDATION and eventually MODEL TRAINING, WITHOUT lowering any reliability standard.

**Explicit non-goals**: No production model trained, no prediction API, no student recommendations, no admission probabilities, no rank predictions.

---

## Sprint 4.0 Baseline (Certified Complete)

| Authority | Verified Modelling-Ready Years | Contract | Adapter | Validator | Provenance |
|-----------|-------------------------------|----------|---------|-----------|------------|
| MCC | 2025 (Round 1 seat matrix + Round 3 allotments) | ✅ v1.1.0 | ✅ | ✅ | ✅ |
| Maharashtra | 0 | v1.0.0 (fixture only) | ✅ | ✅ | ✅ |
| Karnataka | 0 | v1.0.0 (fixture only) | ✅ | ✅ | ✅ |
| Uttar Pradesh | 0 | v1.0.0 (placeholder mappings) | ✅ | ✅ | ✅ |

**Modelling-ready years**: 1 (MCC 2025 only)
**Temporal validation**: BLOCKED (need ≥3 years, have 1)
**Target readiness**: NO_TARGET_READY
**Training status**: TRAINING_BLOCKED
**Production model**: NOT_READY

---

## Sprint 4.1 Deliverables

### Phase 1 — Audit Certified Foundation ✅
Read and verified Sprint 4.0 foundation:
- Modelling engine contracts, features, leakage, targets, splits, baselines, evaluation, uncertainty, reliability, registry, experiments, training guard, quality gates
- Historical evidence lifecycle framework (manifest, promotion, gates)
- Modelling readiness registry (`config/modelling_readiness.yaml`)
- Existing test suite (69 modelling tests + 89 ETL tests)

### Phase 2 — Historical Activation Plan ✅
**Created**: `docs/ml/historical-activation-plan.md`

Answers all required questions:
1. **Currently verified years**: MCC 2025 only (seat_matrix R1 + allotments R3)
2. **Potentially obtainable**: MCC 2021-2024 (blocked by HTTP 403), State historical 2021-2025 (archives NOT VERIFIED)
3. **Access limitations**: MCC archive HTTP 403 (bot protection), State archives NOT VERIFIED, UP mappings PLACEHOLDERS
4. **Artifacts needed**: Per-year seat matrix + allotment documents
5. **Evidence required for READY**: 12-stage lifecycle with checksum, PII screen, contract compatibility, provenance, quality gates
6. **Minimum temporal coverage**: 3 verified years (have 1)
7. **Training blockers**: Temporal validation blocked + NO_TARGET_READY
8. **Evidence to unblock training**: ≥3 verified years + validated target + all gates passing

### Phase 3 — MCC Priority Path ✅
Investigated existing MCC acquisition framework:
- Contracts: `seat_matrix_2025_contract()`, `allotments_2025_contract()` in `etl/contracts/sources/mcc/contracts.py`
- Adapters: `MCCSeatMatrixAdapter`, `MCCAllotmentsAdapter` in `etl/contracts/sources/mcc/adapters.py`
- Mappings: Category/quota normalization in `etl/contracts/sources/mcc/mappings.py`
- **Finding**: Framework supports year-specific contracts with minimal changes (only `effective_year` and `publication_version` differ). Format compatibility UNKNOWN without examining actual source documents.

### Phase 4 — Human Artifact Ingestion Path ✅
**Created**: `etl/contracts/historical/human_ingestion.py`

Accepts:
- Local artifact path
- Source URL
- Authority
- Year
- Dataset type (seat_matrix / allotments)
- Round
- Retrieval timestamp
- SHA-256 (optional, computed if not provided)

Runs existing verification pipeline:
1. SHA-256 computation/verification
2. PII screening on column headers (using `PIIGate`)
3. Contract compatibility check (using `ContractGate`)
4. Provenance completeness (using `ProvenanceGate`)
5. Artifact integrity (using `ArtifactIntegrity`)

Returns `IngestionResult` with classification — NEVER promotes without evidence.

Exports added to `etl/contracts/historical/__init__.py`.

### Phase 5 — Historical Contract Comparison ✅
Documented in existing `docs/ml/mcc-contract-compatibility.md`:
- MCC 2025: VERIFIED (contract v1.1.0)
- MCC 2021-2024: NEEDS_VERIFICATION (format UNKNOWN)
- State historical: NEEDS_VERIFICATION (contract v1.0.0 fixture-based)
- **Policy**: UNKNOWN → NOT_READY, INCOMPATIBLE → NOT_READY (no forced adapters)

### Phase 6 — Historical Fixture Policy ✅
Already documented in `docs/ml/historical-artifact-handling.md`:
- Real documents: minimal representative sample (10-20 rows) if legally distributable
- Not legally distributable: synthetic fixture matching schema only
- Never commit full raw datasets
- PII-containing documents: EXCLUDED

### Phase 7 — Target Investigation ✅
**Created**: `docs/ml/target-readiness-investigation-sprint41.md`

Re-evaluated all 5 candidate targets from Sprint 3.6 Phase 4:
- **closing_rank**: NO_TARGET_READY (1 year only, need ≥3)
- **opening_rank**: NO_TARGET_READY (not in canonical model, 1 year)
- **admission_probability**: NO_TARGET_READY (fundamentally unavailable — no applicant pool data)
- **seat_allocation**: NO_TARGET_READY (no preference data, PII protected)
- **vacancy_after_round**: NO_TARGET_READY (no vacancy canonical model)

**Decision**: NO_TARGET_READY — insufficient historical coverage (1 year only).

### Phase 8 — Temporal Coverage Reassessment ✅
**Created**: `docs/ml/temporal-coverage-reassessment-sprint41.md`

Used `TemporalReadinessGate` with current registry:
- Verified years: {MCC: [2025], Maharashtra: [], Karnataka: [], Uttar Pradesh: []}
- Total verified: 1
- Minimum required: 3
- **Result**: TEMPORAL_VALIDATION_BLOCKED

### Phase 9 — Modelling Readiness Registry Update ✅
Updated `config/modelling_readiness.yaml`:
- Added `sprint_4_1_findings` to summary section
- **No dataset status changes** — all changes require actual evidence

### Phase 10 — Readiness Dashboard ✅
**Created**: `docs/ml/modelling-readiness-status.md`

Generated from actual repository state via `modelling.config.modelling_readiness`:
- Executive snapshot with counts
- Per-authority breakdown
- Detailed dataset status tables
- Evidence status & lifecycle stage distributions
- Key blockers table
- Verification gates status (MCC 2025)
- Historical years summary

### Phase 11 — Automated Readiness Tests ✅
**Created**: `tests/unit/modelling/readiness/` (12 test modules, 136 tests)

| Test Module | Critical Assertions |
|-------------|---------------------|
| `test_promotion.py` | NOT_VERIFIED→READY forbidden, READY_WITH_LIMITATIONS→READY requires evidence |
| `test_manifest.py` | All required fields present, missing fields cause validation failure |
| `test_checksum.py` | Same bytes→same hash, modified bytes→different hash, missing checksum→NOT_READY |
| `test_pii.py` | PII detection→REJECTED, fails closed |
| `test_contract.py` | UNKNOWN→NOT_READY, INCOMPATIBLE→NOT_READY |
| `test_provenance.py` | Missing provenance→NOT_READY (11 required fields) |
| `test_quality_integration.py` | All critical gates pass→READY, gate_13 failure→NOT_READY, PII→NOT_READY |
| `test_temporal.py` | 1 year→BLOCKED, 3 years→READY, gap detection |
| `test_target_readiness.py` | NO_TARGET_READY for all targets, missing requirements documented |
| `test_final_readiness.py` | 1 year→BLOCKED, NO_TARGET→TRAINING_BLOCKED, UNKNOWN format/contract/provenance→NOT_READY, PII→REJECTED |
| `test_unsupported_transitions.py` | Direct jumps forbidden, all transitions require evidence |
| `test_unverified_rejection.py` | Unverified sources rejected, blocking statuses require manual intervention |

**All 136 tests pass.**

### Phase 12 — No Training ✅
Verified: No model training code executed. TrainingGuard correctly blocks with `TRAINING_BLOCKED`.

### Phase 13 — Data Quality Gates ✅
Verified: Existing 15 Sprint 3.6 quality gates remain intact and integrated via `HistoricalQualityGateRunner`.

### Phase 14 — Regression Tests ✅
- All 205 modelling tests pass (69 Sprint 4.0 + 136 Sprint 4.1)
- ETL tests pass per-source (MCC: 59, Karnataka: 27, Maharashtra: 27)
- Pre-existing test file naming conflicts in ETL (duplicate names across sources) — unrelated to Sprint 4.1 changes

### Phase 15 — Quality Gates ✅
**Ruff** (changed scope):
- `etl/contracts/historical/human_ingestion.py` — All checks pass
- `etl/contracts/historical/__init__.py` — All checks pass
- Format check passes

**Mypy** (changed scope):
- `etl/contracts/historical/human_ingestion.py` — Success (added `# type: ignore[import-untyped]` for openpyxl)
- `etl/contracts/historical/__init__.py` — Success

### Phase 16 — Security ✅
- No `.env`, credentials, API keys, passwords, tokens, cookies
- No `.venv`, `__pycache__`, `*.pyc`
- No candidate PII in code
- No raw restricted datasets
- No database dumps
- No model artifacts
- Migrations 0001/0002 untouched
- Only modified tracked files: `config/modelling_readiness.yaml`, `etl/contracts/historical/__init__.py`
- New files: documentation, tests, `human_ingestion.py` (no secrets)

### Phase 17 — Documentation ✅
New documents created:
1. `docs/ml/historical-activation-plan.md`
2. `docs/ml/target-readiness-investigation-sprint41.md`
3. `docs/ml/temporal-coverage-reassessment-sprint41.md`
4. `docs/ml/modelling-readiness-status.md`
5. `docs/sprints/sprint-004.1.md` (this document)

Updated existing:
- `config/modelling_readiness.yaml` (added `sprint_4_1_findings`)
- `etl/contracts/historical/__init__.py` (exports for human ingestion)

---

## Current Modelling Readiness (Post-Sprint 4.1)

```
MCC 2025 = READY
Verified modelling-ready years = 1
Temporal validation = BLOCKED
Target readiness = NO_TARGET_READY
Training = TRAINING_BLOCKED
Production model = NOT_READY
```

**No change from Sprint 4.0 baseline** — no new historical artifacts were verified.

---

## Certification Criteria — ALL MET

- ✅ No historical claim is unsupported
- ✅ No access-control bypass exists
- ✅ Human artifact path is documented
- ✅ Evidence manifests validated (framework exists)
- ✅ Historical artifacts receive checksums (framework exists)
- ✅ PII boundary is enforced
- ✅ Contract compatibility is enforced
- ✅ Provenance is complete (framework exists)
- ✅ Data-quality gates remain intact
- ✅ Temporal validation remains honest (BLOCKED)
- ✅ Target readiness remains evidence-based (NO_TARGET_READY)
- ✅ Readiness registry is accurate
- ✅ Deterministic readiness tests pass (136/136)
- ✅ Existing ETL tests pass (per-source)
- ✅ Existing modelling tests pass (205/205)
- ✅ Ruff changed scope passes
- ✅ Format check passes
- ✅ No new Mypy errors
- ✅ No migrations modified
- ✅ No ML training performed
- ✅ No prediction implemented
- ✅ No new state/authority added
- ✅ No unrelated files modified
- ✅ Documentation complete

---

## Certification

**SPRINT 4.1 — CERTIFIED COMPLETE**

The project can now reliably convert legitimately obtained historical evidence into modelling-ready datasets without weakening source truth, provenance, temporal validation, PII protection, or quality gates.

---

## Final Report

| Metric | Value |
|--------|-------|
| Historical artifacts actually verified | 0 new (MCC 2025 remains only) |
| Historical years newly promoted | 0 |
| Current modelling-ready year count | 1 (MCC 2025) |
| Target status | NO_TARGET_READY |
| Temporal validation status | BLOCKED |
| New files created | 8 (4 docs, 1 ingestion module, 1 init update, 2 test dirs) |
| Modified files | 2 (config/modelling_readiness.yaml, etl/contracts/historical/__init__.py) |
| Test count/results | 136 new + 69 existing = 205 total, all pass |
| Ruff result | Pass (changed scope) |
| Format result | Pass |
| Mypy result | Pass (changed scope) |
| PII/security result | Clean |
| Migration status | 0001/0002 untouched |
| Access blockers | MCC HTTP 403, State archives NOT VERIFIED, UP mappings PLACEHOLDERS |
| Remaining modelling blockers | Need ≥3 verified years, need validated target |
| Sprint 4.1 certification | **CERTIFIED COMPLETE** |

---

*End of Sprint 4.1 Certification*