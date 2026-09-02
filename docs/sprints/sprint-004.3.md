# Sprint 4.3 — Evidence Acquisition & Modelling Readiness Reassessment

**Status**: CERTIFIED COMPLETE
**Date**: 2026-08-31
**Branch**: main
**Base Commit**: 6d8f1f6 (Sprint 4.2 certification)

---

## Objective

Sprint 4.3 is an **evidence reassessment sprint**. Its purpose is to determine whether repository/source evidence has changed since Sprint 4.2 certification, and whether any historical dataset or target readiness status can be legitimately updated.

**Explicit non-goals**: No model training, no prediction implementation, no production model, no status changes without evidence, no gate bypass.

---

## Baseline State (Sprint 4.2 Certified)

| Metric | Value |
|--------|-------|
| MCC 2025 | READY (2 datasets: seat_matrix R1, allotments R3) |
| Verified modelling-ready years | 1 (MCC 2025 only) |
| Historical artifacts newly verified in Sprint 4.2 | 0 |
| Target readiness | NO_TARGET_READY |
| Temporal validation | BLOCKED |
| Training | TRAINING_BLOCKED |
| Production model | NOT_READY |

---

## Scope

**Read-only audit** of:
- Sprint 4.2 release artifacts and tag
- `config/modelling_readiness.yaml` registry
- Historical evidence lifecycle framework
- Human ingestion framework
- Target validation engine
- Temporal validation gate
- Training guard

**Evidence re-verification** of:
- MCC 2021-2024 automated download accessibility
- State archive accessibility (Maharashtra/Karnataka/UP)
- UP category/quota mapping verification status
- Contract compatibility for historical years

**No modifications** to:
- Database schema/migrations
- Core modelling architecture
- ETL architecture
- Verification gates

---

## Repository Audit

### Sprint 4.2 Release Verification
- Tag `v1.0.0-sprint4.2-historical-expansion` exists
- Commit `6d8f1f6` ("feat: complete Sprint 4.2 historical dataset expansion & target validation")
- HEAD = origin/main = Sprint 4.2 commit
- No uncommitted tracked changes

### Modelling Readiness Registry (`config/modelling_readiness.yaml`)
- Version 2, 70 dataset entries
- Summary: 2 READY, 5 READY_WITH_LIMITATIONS, 63 NOT_READY
- `modelling_ready_years`: MCC [2025], Maharashtra [], Karnataka [], Uttar_Pradesh []
- `first_modelling_target`: NO_TARGET_READY
- `minimum_years_for_temporal_validation`: 3
- `current_max_consecutive_years`: 1
- `sprint_4_2_findings` documented (no new artifacts verified)

---

## Historical Evidence Audit

### MCC (Medical Counselling Committee) — All India Quota

| Year | Dataset | Sprint 4.2 | Sprint 4.3 | Evidence |
|------|---------|------------|------------|----------|
| 2025 | seat_matrix R1 | READY | READY | Contract v1.1.0, 15/15 gates, provenance complete |
| 2025 | allotments R3 | READY | READY | Contract v1.1.0, 15/15 gates, provenance complete |
| 2024 | seat_matrix | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block confirmed 2026-08-31 |
| 2024 | allotments | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block confirmed 2026-08-31 |
| 2023 | seat_matrix | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block |
| 2023 | allotments | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block |
| 2022 | seat_matrix | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block |
| 2022 | allotments | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block |
| 2021 | seat_matrix | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block |
| 2021 | allotments | NOT_VERIFIED | NOT_VERIFIED | HTTP 403 block |

**Automated Download Re-verification (2026-08-31)**:
```
https://mcc.nic.in/         → 403 Forbidden
https://mcc.nic.in/archive-ug/ → 403 Forbidden
```
Bot protection persists. No manual retrieval executed.

### Maharashtra (MAHA CET Cell) — State Quota

| Year | Dataset | Sprint 4.2 | Sprint 4.3 | Evidence |
|------|---------|------------|------------|----------|
| 2026 | seat_matrix R1 | READY_WITH_LIMITATIONS | READY_WITH_LIMITATIONS | Fixture-only, contract v1.0.0 |
| 2026 | allotments R1 | READY_WITH_LIMITATIONS | READY_WITH_LIMITATIONS | Fixture-only, contract v1.0.0 |
| 2021-2025 | seat_matrix/allotments | NOT_VERIFIED | NOT_VERIFIED | Archive NOT VERIFIED per config, zero repo evidence |

### Karnataka (KEA) — State Quota

| Year | Dataset | Sprint 4.2 | Sprint 4.3 | Evidence |
|------|---------|------------|------------|----------|
| 2026 | seat_matrix R1 | READY_WITH_LIMITATIONS | READY_WITH_LIMITATIONS | Fixture-only, contract v1.0.0 |
| 2026 | allotments R1 | READY_WITH_LIMITATIONS | READY_WITH_LIMITATIONS | Fixture-only, contract v1.0.0 |
| 2021-2025 | seat_matrix/allotments | NOT_VERIFIED | NOT_VERIFIED | Archive NOT VERIFIED per config, zero repo evidence |

### Uttar Pradesh (UPMU/DME UP) — State Quota

| Year | Dataset | Sprint 4.2 | Sprint 4.3 | Evidence |
|------|---------|------------|------------|----------|
| 2026 | seat_matrix R1 | NOT_READY | NOT_READY | Contract v1.0.0 but placeholder mappings (Gate 5/6 fail) |
| 2026 | allotments R1 | NOT_READY | NOT_READY | Contract v1.0.0 but placeholder mappings, no fixture |
| 2021-2025 | seat_matrix/allotments | NOT_VERIFIED | NOT_VERIFIED | Archive NOT VERIFIED per config, zero repo evidence, mappings PLACEHOLDER |

**Critical UP Blocker**: Category/quota mappings explicitly documented as PLACEHOLDERS in `etl/contracts/sources/uttar_pradesh/mappings.py`. Gate 5 (category validity) and Gate 6 (quota validity) would fail on real data.

---

## Human Ingestion Framework Verification

**Component**: `etl/contracts/historical/human_ingestion.py`

**Verified Capabilities**:
- Accepts legitimate artifacts (local path, source URL, authority, year, dataset, round, timestamp, SHA-256)
- Runs: ArtifactIntegrity (SHA-256) → PIIGate (column screening) → ContractGate (compatibility) → ProvenanceGate (10 fields)
- Returns `IngestionResult` with full classification — **does not modify registry**
- Fails closed on missing evidence (integrity, PII, provenance, contract)
- No bypass of readiness gates
- No redesign required — framework functions as designed

**Test**: Synthetic fixture processed correctly, classified with appropriate blocking reasons.

---

## Target Readiness Reassessment

**Engine**: `modelling/targets/engine.py` → `TargetEngine`

**Results**:
- `get_first_modelling_target()` → `NO_TARGET_READY`
- All 5 targets: `closing_rank`, `opening_rank`, `admission_probability`, `seat_allocation`, `vacancy_after_round` → `NO_TARGET_READY`

**Leakage Audit (unchanged)**:
| Target | Classification | Reason |
|--------|----------------|--------|
| closing_rank | CONDITIONALLY_ACCEPTABLE | HIGH risk, manageable with temporal split |
| opening_rank | CONDITIONALLY_ACCEPTABLE | HIGH risk, manageable with temporal split |
| admission_probability | REJECTED | EXTREME risk — applicant pool never published, PII |
| seat_allocation | REJECTED | EXTREME risk — preferences PII, never available |
| vacancy_after_round | REJECTED | HIGH risk — no vacancy canonical model |

**Blocking Condition**: Only 1 verified year (need ≥3 for temporal validation). No target can be READY.

---

## Temporal Validation Reassessment

**Gate**: `etl/contracts/historical/temporal_gate.py` → `TemporalReadinessGate`
**Engine**: `modelling/splits/engine.py` → `TemporalSplitter`

**Current State**:
```python
verified_years = {MCC: [2025], Maharashtra: [], Karnataka: [], Uttar_Pradesh: []}
total_verified = 1
minimum_required = 3
chronologically_ordered = True
can_split_train_val_test = False
temporal_validation_status = BLOCKED
```

**Thresholds Verified**:
- 1 verified year → BLOCKED ✅
- 2 verified years → BLOCKED ✅
- 3+ verified years → eligible (subject to all other gates) ✅
- Synthetic/fixture years → NOT counted ✅

---

## Readiness Registry Update

**File**: `config/modelling_readiness.yaml`

**Action**: Added `sprint_4_3_findings` to summary section documenting:
- MCC 2021-2024: Still AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403 confirmed 2026-08-31)
- Maharashtra/Karnataka/UP 2021-2025: Archive access NOT VERIFIED, zero repository evidence
- UP category/quota mappings: Remain PLACEHOLDERS — NOT_READY even if data obtained
- Target readiness: NO_TARGET_READY (insufficient historical coverage)
- Temporal validation: BLOCKED (1 verified year, need ≥3)
- Training status: TRAINING_BLOCKED
- **No status changes in registry — all changes require actual evidence**

---

## Tests

### New Sprint 4.3 Tests
**File**: `tests/unit/modelling/test_sprint43_reassessment.py` (38 tests)

**Coverage**:
1. MCC 2025 remains READY ✅
2. Unverified historical evidence cannot become READY ✅
3. Missing provenance fails closed ✅
4. Missing checksum fails per policy ✅
5. Unknown contract compatibility fails closed ✅
6. PII-containing evidence is rejected ✅
7. HTTP-blocked evidence cannot be promoted ✅
8. Target remains NO_TARGET_READY when evidence insufficient ✅
9. Temporal validation blocked below 3 verified years ✅
10. Synthetic years cannot satisfy temporal coverage ✅
11. Training blocked while readiness gates fail ✅
12. Existing Sprint 4.0-4.2 behavior does not regress ✅

### Regression Test Results

| Test Suite | Tests | Result |
|------------|-------|--------|
| Sprint 4.3 New Tests | 38 | ✅ PASSED |
| Sprint 4.0-4.2 Modelling Tests | 238 | ✅ PASSED |
| Sprint 4.1 Readiness Tests | 136 | ✅ PASSED |
| Sprint 4.2 Target Validation Tests | 33 | ✅ PASSED |
| Sprint 3.8 Historical Tests | 46 | ✅ PASSED |
| Sprint 3.9 Framework Tests | 11 | ✅ PASSED |
| Sprint 3.6 ETL Tests | 43 | ✅ PASSED |
| MCC Source Tests | 59 | ✅ PASSED |
| Maharashtra Source Tests | 27 | ✅ PASSED |
| Karnataka Source Tests | 27 | ✅ PASSED |
| Contract Base Tests | 61 | ✅ PASSED |
| **TOTAL** | **719** | **✅ ALL PASSED** |

*Note: ETL conformance tests have 4 pre-existing failures unrelated to Sprint 4.3 (documented in Sprint 4.1/4.2).*

---

## Quality Gates

| Check | Scope | Result |
|-------|-------|--------|
| `ruff check` | `tests/unit/modelling/test_sprint43_reassessment.py` | ✅ PASS |
| `ruff format --check` | `tests/unit/modelling/test_sprint43_reassessment.py` | ✅ PASS |
| `mypy` | `tests/unit/modelling/test_sprint43_reassessment.py` | ✅ PASS (0 new errors; 58 pre-existing) |
| `git diff --check` | All changed files | ✅ PASS |

---

## Security

| Check | Result |
|-------|--------|
| Secrets/API keys/passwords/tokens | ✅ NONE |
| PII in code | ✅ NONE |
| Database dumps | ✅ NONE |
| Model artifacts | ✅ NONE |
| Raw restricted datasets | ✅ NONE |
| `.env`, `.venv`, `__pycache__`, `*.pyc` committed | ✅ NO |

---

## Migration Status

| Migration | Status |
|-----------|--------|
| `backend/alembic/versions/0001_initial_schema.py` | ✅ UNTOUCHED |
| `backend/alembic/versions/0002_create_historical_cutoffs.py` | ✅ UNTOUCHED |
| New migrations | ❌ NONE CREATED |

---

## Training Safety Check

| Check | Result |
|-------|--------|
| Model trained | ❌ NO |
| Prediction implementation | ❌ NO |
| Prediction endpoint enabled | ❌ NO |
| TrainingGuard bypass | ❌ NO |
| Temporal gate bypass | ❌ NO |
| Target gate bypass | ❌ NO |
| Synthetic historical training data | ❌ NO |
| Production model generated | ❌ NO |

**Current State**: `TRAINING_BLOCKED` (as expected)

---

## Documentation

**Created**:
1. `docs/ml/sprint42-to-sprint43-reassessment.md` — Evidence comparison and reassessment detail
2. `docs/sprints/sprint-004.3.md` — This certification report

**Updated**:
1. `config/modelling_readiness.yaml` — Added `sprint_4_3_findings`

---

## Final Certification Gate

| Criterion | Status |
|-----------|--------|
| No fabricated historical data | ✅ |
| No synthetic years | ✅ |
| No PII | ✅ |
| No secrets | ✅ |
| No migration changes | ✅ |
| No database redesign | ✅ |
| No model training | ✅ |
| No prediction implementation | ✅ |
| No TrainingGuard bypass | ✅ |
| No temporal validation bypass | ✅ |
| No target readiness bypass | ✅ |
| No access-control bypass | ✅ |
| Provenance requirements preserved | ✅ |
| Contract requirements preserved | ✅ |
| Existing ETL architecture preserved | ✅ |
| Existing modelling architecture preserved | ✅ |
| New tests pass | ✅ (38/38) |
| Regression tests pass | ✅ (681 existing) |
| Ruff passes | ✅ |
| Format passes | ✅ |
| Mypy passes (changed scope) | ✅ |
| Documentation complete | ✅ |

---

## Certification

**SPRINT 4.3 — CERTIFIED COMPLETE**

### Final State

| Metric | Value |
|--------|-------|
| Historical artifacts newly verified | 0 |
| Modelling-ready years | 1 (MCC 2025) |
| MCC 2025 | READY |
| MCC 2021-2024 | NOT_VERIFIED / AUTOMATED_DOWNLOAD_BLOCKED |
| Maharashtra 2021-2025 | NOT_VERIFIED |
| Karnataka 2021-2025 | NOT_VERIFIED |
| UP 2021-2026 | NOT_READY / NOT_VERIFIED (placeholder mappings) |
| Target readiness | NO_TARGET_READY |
| Temporal validation | BLOCKED |
| Training | TRAINING_BLOCKED |
| Production model | NOT_READY |

### Reliability Principle Upheld

> **SOURCE TRUTH > DATA VOLUME**
>
> **RELIABILITY > MODEL AVAILABILITY**
>
> **TEMPORAL VALIDATION BEFORE TRAINING**
>
> **NO EVIDENCE = NO PROMOTION**

The project honestly documents that no new historical artifacts were verified. The evidence says we do NOT have enough trustworthy historical data to build a reliable NEET prediction target. The repository architecture is ready. The DATA is NOT.

---

## Git Status

```
On branch main
Your branch is up to date with 'origin/main'.

Changed files:
  config/modelling_readiness.yaml          (sprint_4_3_findings added)
  tests/unit/modelling/test_sprint43_reassessment.py  (new)
  docs/ml/sprint42-to-sprint43-reassessment.md  (new)
  docs/sprints/sprint-004.3.md            (new)

No unrelated files modified.
No secrets/PII in diff.
Migrations 0001/0002 untouched.
```

---

*End of Sprint 4.3 Certification*