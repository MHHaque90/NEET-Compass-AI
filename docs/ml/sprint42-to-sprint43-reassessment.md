# Sprint 4.2 → Sprint 4.3 Reassessment

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 4.3 — Evidence Acquisition & Modelling Readiness Reassessment

---

## 1. Sprint 4.2 Baseline (Pre-Reassessment)

| Metric | Sprint 4.2 Value |
|--------|-----------------|
| MCC 2025 | READY |
| Verified modelling-ready years | 1 |
| Historical artifacts newly verified in Sprint 4.2 | 0 |
| Target readiness | NO_TARGET_READY |
| Temporal validation | BLOCKED |
| Training | TRAINING_BLOCKED |
| Production model | NOT_READY |

### Sprint 4.2 Key Findings (from `sprint_4_2_findings` in config)
- MCC 2021-2024: Still AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403), no manual retrieval executed
- Maharashtra/Karnataka/UP 2021-2025: Archive access NOT VERIFIED, zero repository evidence
- UP category/quota mappings: Remain PLACEHOLDERS — NOT_READY even if data obtained
- MCC contract v1.1.0 compatibility for 2021-2024: UNKNOWN without examining actual source documents
- State contract v1.0.0: Fixture-based only — real historical format UNKNOWN
- Target readiness: NO_TARGET_READY (insufficient historical coverage, 1 year only)
- Temporal validation: BLOCKED (1 verified year, need ≥3)
- Training status: TRAINING_BLOCKED (temporal blocked + no target)
- No status changes in registry — all changes require actual evidence

---

## 2. Sprint 4.3 Observations

### 2.1 Repository Baseline Audit (Phase 1)
- Tag `v1.0.0-sprint4.2-historical-expansion` verified present
- HEAD and origin/main at commit `6d8f1f6` (Sprint 4.2 certification)
- No tracked changes since Sprint 4.2
- `config/modelling_readiness.yaml` matches Sprint 4.2 state exactly
- All modelling framework components intact (readiness, temporal, target, training guard, provenance, PII, contract gates)

### 2.2 Automated Source Access Reassessment (Phase 4)
**MCC Archive (`https://mcc.nic.in/archive-ug/`)** — Re-verified 2026-08-31:

```
URL: https://mcc.nic.in/
  probe: None
  download: {'ok': False, 'rejected_by_server': True, 'status': 403, 'reason': 'Forbidden'}

URL: https://mcc.nic.in/archive-ug/
  probe: None
  download: {'ok': False, 'rejected_by_server': True, 'status': 403, 'reason': 'Forbidden'}
```

**Result**: HTTP 403 block persists. Automated downloads remain blocked by bot protection. Archive document census could not be performed due to blocked download.

**Maharashtra/Karnataka/UP Archives**: Not re-verified in this environment (network access to state portals not attempted). Status remains NOT_VERIFIED per config.

### 2.3 Human Ingestion Framework Verification (Phase 5)
- Framework at `etl/contracts/historical/human_ingestion.py` verified functional
- Accepts local artifact path, source URL, authority, year, dataset type, round, retrieval timestamp, optional SHA-256
- Runs full pipeline: ArtifactIntegrity → PIIGate → ContractGate → ProvenanceGate
- Returns `IngestionResult` with classification — does NOT modify registry
- Does NOT bypass readiness gates
- Tested with synthetic fixture — correctly classifies and documents blocking reasons

**No defects found** — framework works as designed. No fix required.

### 2.4 Target Readiness Reassessment (Phase 6)
- `TargetEngine.get_first_modelling_target()` returns `NO_TARGET_READY`
- All 5 candidate targets remain `NO_TARGET_READY`:
  - `closing_rank`: CONDITIONALLY_ACCEPTABLE but blocked by <3 verified years
  - `opening_rank`: CONDITIONALLY_ACCEPTABLE but blocked by <3 verified years + not in canonical
  - `admission_probability`: REJECTED (fundamentally unavailable — no applicant pool, PII)
  - `seat_allocation`: REJECTED (fundamentally unavailable — no preferences, PII)
  - `vacancy_after_round`: REJECTED (no vacancy canonical model)
- Leakage audit unchanged: 3 targets REJECTED, 3 CONDITIONALLY_ACCEPTABLE with temporal split

### 2.5 Temporal Validation Reassessment (Phase 7)
- `TemporalReadinessGate.validate()` with current registry: **BLOCKED**
- Verified years: MCC [2025] only → count = 1
- Minimum required: 3
- `TemporalSplitter.get_current_status()`: `BLOCKED_INSUFFICIENT_YEARS`
- Config `get_temporal_validation_status()`: "BLOCKED"

### 2.6 Training Safety Check (Phase 12)
- `TrainingGuard` correctly blocks with `TRAINING_BLOCKED`
- Block reasons: `TEMPORAL_VALIDATION_BLOCKED`, `INSUFFICIENT_VERIFIED_YEARS`, `TARGET_NOT_READY`, `NO_TARGET_DEFINED`
- No model training code executed
- No prediction endpoints enabled
- No TrainingGuard bypass
- No temporal/target gate bypass
- No synthetic historical training data generated

---

## 3. Evidence Comparison Summary

| Dataset/Year | Sprint 4.2 Status | Sprint 4.3 Status | Evidence Basis |
|--------------|-------------------|-------------------|----------------|
| MCC 2025 seat_matrix | READY | READY | Contract v1.1.0, adapter, validator, provenance, 15/15 gates |
| MCC 2025 allotments | READY | READY | Contract v1.1.0, adapter, validator, provenance, 15/15 gates |
| MCC 2021-2024 (all) | NOT_VERIFIED / NOT_READY | NOT_VERIFIED / NOT_READY | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403 confirmed 2026-08-31) |
| Maharashtra 2021-2025 | NOT_VERIFIED | NOT_VERIFIED | Archive NOT VERIFIED per config, zero repo evidence |
| Karnataka 2021-2025 | NOT_VERIFIED | NOT_VERIFIED | Archive NOT VERIFIED per config, zero repo evidence |
| UP 2021-2025 | NOT_VERIFIED | NOT_VERIFIED | Archive NOT VERIFIED per config, zero repo evidence |
| UP 2026 | NOT_READY (placeholder mappings) | NOT_READY (placeholder mappings) | Category/quota mappings explicitly PLACEHOLDER |
| Maharashtra/Karnataka 2026 | READY_WITH_LIMITATIONS (fixture) | READY_WITH_LIMITATIONS (fixture) | Fixture-only, no live download verified |

**No status changes — evidence unchanged.**

---

## 4. Dataset-by-Dataset Status Matrix

### MCC (Medical Counselling Committee)
| Year | Dataset | Round | Verification | Readiness | Contract | Provenance | Notes |
|------|---------|-------|--------------|-----------|----------|------------|-------|
| 2025 | seat_matrix | Round 1 | VERIFIED | READY | v1.1.0 ✅ | COMPLETE | |
| 2025 | allotments | Round 3 | VERIFIED | READY | v1.1.0 ✅ | COMPLETE | |
| 2024 | seat_matrix | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2024 | allotments | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2023 | seat_matrix | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2023 | allotments | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2022 | seat_matrix | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2022 | allotments | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2021 | seat_matrix | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |
| 2021 | allotments | All | NOT_VERIFIED | NOT_READY | NONE | INCOMPLETE | HTTP 403 block |

### Maharashtra (MAHA CET Cell)
| Year | Dataset | Verification | Readiness | Notes |
|------|---------|--------------|-----------|-------|
| 2026 | seat_matrix | VERIFIED | READY_WITH_LIMITATIONS | Fixture-only |
| 2026 | allotments | VERIFIED | READY_WITH_LIMITATIONS | Fixture-only |
| 2021-2025 | seat_matrix/allotments | NOT_VERIFIED | NOT_READY | Archive NOT VERIFIED |

### Karnataka (KEA)
| Year | Dataset | Verification | Readiness | Notes |
|------|---------|--------------|-----------|-------|
| 2026 | seat_matrix | VERIFIED | READY_WITH_LIMITATIONS | Fixture-only |
| 2026 | allotments | VERIFIED | READY_WITH_LIMITATIONS | Fixture-only (no fixture) |
| 2021-2025 | seat_matrix/allotments | NOT_VERIFIED | NOT_READY | Archive NOT VERIFIED |

### Uttar Pradesh (UPMU/DME UP)
| Year | Dataset | Verification | Readiness | Notes |
|------|---------|--------------|-----------|-------|
| 2026 | seat_matrix | VERIFIED | NOT_READY | Placeholder mappings |
| 2026 | allotments | VERIFIED | NOT_READY | Placeholder mappings, no fixture |
| 2021-2025 | seat_matrix/allotments | NOT_VERIFIED | NOT_READY | Archive NOT VERIFIED, mappings PLACEHOLDER |

---

## 5. Source Access Blockers Documented

| Source | Blocker Type | Evidence | Resolution Path |
|--------|--------------|----------|-----------------|
| MCC 2021-2024 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | Live probe 2026-08-31: 403 Forbidden | Manual browser retrieval documented but not executed |
| Maharashtra 2021-2025 | NOT_VERIFIED (archive access) | config/data_sources.yaml: "archive NOT VERIFIED" | Live verification of archive page required |
| Karnataka 2021-2025 | NOT_VERIFIED (archive access) | config/data_sources.yaml: "archive NOT VERIFIED" | Live verification of archive page required |
| UP 2021-2025 | NOT_VERIFIED (archive access) | config/data_sources.yaml: "archive NOT VERIFIED" | Live verification + mapping validation required |
| UP 2021-2026 | PLACEHOLDER mappings | modelling_readiness.yaml: "explicitly PLACEHOLDER" | Verify against real UP source data |

---

## 6. Target Readiness Reassessment Result

**NO_TARGET_READY** — No change from Sprint 4.2.

Justification unchanged:
1. Insufficient historical coverage: only 1 verified year (MCC 2025)
2. No state historical allotment data in repository
3. Single year cannot support temporal train/validate/test split
4. Opening rank not in canonical model
5. No applicant pool data (never published, PII protected)
6. UP mappings remain PLACEHOLDERS
7. No new evidence acquired in Sprint 4.3

---

## 7. Temporal Validation Reassessment Result

**BLOCKED** — No change from Sprint 4.2.

- Verified modelling-ready years: 1 (MCC 2025)
- Minimum required: 3
- Chronologically ordered: Yes
- Can split train/validate/test: No
- Gap years: N/A (only 1 year)

---

## 8. Training State Reassessment Result

**TRAINING_BLOCKED** — No change from Sprint 4.2.

All TrainingGuard checks fail:
- Temporal validation: BLOCKED
- Insufficient verified years: 1 < 3
- Target readiness: NO_TARGET_READY
- No target defined: NO_TARGET_DEFINED

---

## 9. Tests Summary

| Test Suite | Tests | Result |
|------------|-------|--------|
| Sprint 4.3 New Tests | 38 | ✅ PASSED |
| Sprint 4.0-4.2 Modelling Tests | 238 | ✅ PASSED |
| Sprint 4.1 Readiness Tests | 136 | ✅ PASSED |
| Sprint 4.2 Target Validation Tests | 33 | ✅ PASSED |
| Sprint 3.8 Historical Tests | 46 | ✅ PASSED |
| Sprint 3.9 Tests | 11 | ✅ PASSED |
| Sprint 3.6 ETL Tests | 43 | ✅ PASSED |
| MCC Source Tests | 59 | ✅ PASSED |
| Maharashtra Source Tests | 27 | ✅ PASSED |
| Karnataka Source Tests | 27 | ✅ PASSED |
| Contract Base Tests | 61 | ✅ PASSED |
| **TOTAL** | **719** | **✅ ALL PASSED** |

*Note: ETL conformance tests have 4 pre-existing failures unrelated to Sprint 4.3 (documented in Sprint 4.1/4.2).*

---

## 10. Quality Gates

| Check | Scope | Result |
|-------|-------|--------|
| ruff check | `tests/unit/modelling/test_sprint43_reassessment.py` | ✅ PASS |
| ruff format --check | `tests/unit/modelling/test_sprint43_reassessment.py` | ✅ PASS |
| mypy | `tests/unit/modelling/test_sprint43_reassessment.py` (changed scope) | ✅ PASS (0 new errors; 58 pre-existing) |
| git diff --check | All changed files | ✅ PASS |

---

## 11. Security Scan

| Check | Result |
|-------|--------|
| Secrets/API keys/passwords/tokens | ✅ NONE FOUND |
| PII in code | ✅ NONE FOUND |
| Database dumps | ✅ NONE FOUND |
| Model artifacts | ✅ NONE FOUND |
| Raw restricted datasets | ✅ NONE FOUND |
| `.env`, `.venv`, `__pycache__`, `*.pyc` | ✅ NONE COMMITTED |

---

## 12. Migration Status

| Migration | Status |
|-----------|--------|
| `backend/alembic/versions/0001_initial_schema.py` | ✅ UNTOUCHED |
| `backend/alembic/versions/0002_create_historical_cutoffs.py` | ✅ UNTOUCHED |
| New migrations created | ❌ NO |

---

## 13. Scope Verification

| Criterion | Result |
|-----------|--------|
| No fabricated historical data | ✅ CONFIRMED |
| No synthetic years added to registry | ✅ CONFIRMED |
| No PII committed | ✅ CONFIRMED |
| No secrets committed | ✅ CONFIRMED |
| No migration changes | ✅ CONFIRMED |
| No database redesign | ✅ CONFIRMED |
| No model training | ✅ CONFIRMED |
| No prediction implementation | ✅ CONFIRMED |
| No TrainingGuard bypass | ✅ CONFIRMED |
| No temporal validation bypass | ✅ CONFIRMED |
| No target readiness bypass | ✅ CONFIRMED |
| No access-control bypass | ✅ CONFIRMED |
| Provenance requirements preserved | ✅ CONFIRMED |
| Contract requirements preserved | ✅ CONFIRMED |
| Existing ETL architecture preserved | ✅ CONFIRMED |
| Existing modelling architecture preserved | ✅ CONFIRMED |
| New tests pass | ✅ CONFIRMED (38/38) |
| Regression tests pass | ✅ CONFIRMED (681 existing) |
| Ruff passes | ✅ CONFIRMED |
| Format passes | ✅ CONFIRMED |
| Mypy passes (changed scope) | ✅ CONFIRMED (0 new errors) |
| Documentation complete | ✅ CONFIRMED |

---

## 14. Final Certification

### Sprint 4.3 — CERTIFIED COMPLETE

**Objective Achieved**: Evidence-based reassessment of historical data and target readiness blockers completed.

**Evidence Determination**: No new historical artifacts verified. All blockers documented in Sprint 4.2 persist with confirmed evidence.

**Status Changes**: NONE — "No status changes — evidence unchanged."

**Final State**:
- MCC 2025 = READY (2 datasets)
- Verified modelling-ready years = 1
- Target readiness = NO_TARGET_READY
- Temporal validation = BLOCKED
- Training = TRAINING_BLOCKED
- Production model = NOT_READY

**Reliability Principle Upheld**:
- SOURCE TRUTH > DATA VOLUME
- RELIABILITY > MODEL AVAILABILITY
- TEMPORAL VALIDATION BEFORE TRAINING
- NO EVIDENCE = NO PROMOTION

---

*End of Sprint 4.2 → Sprint 4.3 Reassessment*