# Target Readiness Investigation — Sprint 4.1

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 4.1 — Historical Data Activation & Modelling-Readiness Advancement

---

## 1. Purpose

This document investigates whether the currently verified counselling data can support a defensible modelling target, per the mandate in Sprint 4.1 Phase 7. It reviews the existing target definition documents and assesses candidate targets against actual available fields.

---

## 2. Documents Reviewed

- `docs/ml/target-definition.md` (Sprint 3.6 Phase 3) — Canonical Modelling Dataset Definition
- `docs/ml/target-definition-phase4.md` (Sprint 3.6 Phase 4) — Target Analysis and First Modelling Target Selection
- `docs/ml/modelling-coverage-reassessment.md` (Sprint 3.7) — Modelling Coverage Reassessment

---

## 3. Current Verified Data Inventory (Repository Evidence)

| Authority | Dataset | Year | Round | Records | Contract |
|-----------|---------|------|-------|---------|----------|
| MCC | seat_matrix | 2025 | Round 1 | ~8,000+ (via fixture/test) | v1.1.0 |
| MCC | allotments | 2025 | Round 3 | ~10,000+ (via fixture/test) | v1.1.0 |

**Total verified modelling-ready datasets**: 2 (both MCC 2025)

All other authority/year combinations have `NOT_READY` status with `evidence_status: NOT_VERIFIED` or `AUTOMATED_DOWNLOAD_BLOCKED`.

---

## 4. Candidate Targets Re-Evaluation

Per `target-definition-phase4.md`, five candidate targets were evaluated. Re-assessment with Sprint 4.1 evidence:

### 4.1 Closing Rank Forecasting

| Aspect | Sprint 3.6 Assessment | Sprint 4.1 Re-assessment |
|--------|----------------------|--------------------------|
| Exact Definition | Last rank admitted per college×course×quota×category×round×year | Unchanged |
| Required Data | Allotment records with rank, aggregated to closing rank | MCC 2025 allotments only |
| Label Availability | ✅ MCC 2025: computable from allotment rank | ✅ Same (1 year only) |
| Prediction-Time Available | ✅ College, course, quota, category, round, year known | Unchanged |
| Leakage Risk | HIGH (manageable with temporal split) | Unchanged |
| **Historical Coverage** | ❌ ONLY MCC 2025 available | ❌ **STILL ONLY 1 YEAR** |
| Suitability | LOW | **LOW (unchanged)** |

**Verdict**: Insufficient historical coverage. Need ≥3 verified years for temporal validation.

### 4.2 Opening Rank Forecasting

| Aspect | Sprint 3.6 Assessment | Sprint 4.1 Re-assessment |
|--------|----------------------|--------------------------|
| Exact Definition | First rank admitted per college×course×quota×category×round×year | Unchanged |
| Required Data | Allotment records with rank, aggregated to opening rank | MCC 2025 allotments only |
| Label Availability | ❌ NOT in canonical model (only per-record rank) | ❌ **STILL NOT IN CANONICAL** |
| Historical Coverage | ❌ Only MCC 2025 | ❌ **STILL ONLY 1 YEAR** |
| Suitability | NONE | **NONE (unchanged)** |

**Verdict**: Cannot compute opening rank from current canonical model. Even if added, only 1 year.

### 4.3 Admission Probability

| Aspect | Sprint 3.6 Assessment | Sprint 4.1 Re-assessment |
|--------|----------------------|--------------------------|
| Exact Definition | P(admitted \| student_rank, college, course, quota, category, round) | Unchanged |
| Required Data | Allotments + student rank distribution + preferences | Unavailable |
| Label Availability | ❌ NO applicant pool data (never published) | ❌ **FUNDAMENTALLY UNAVAILABLE** |
| Leakage Risk | EXTREME | Unchanged |
| Suitability | NOT SUITABLE | **NOT SUITABLE (unchanged)** |

**Verdict**: Fundamentally unidentifiable without applicant pool data (never published) and student preferences (PII).

### 4.4 Seat Allocation (Multi-class)

| Aspect | Sprint 3.6 Assessment | Sprint 4.1 Re-assessment |
|--------|----------------------|--------------------------|
| Required Data | Allotments + student preferences | Unavailable |
| Label Availability | ❌ NO preference data (PII) | ❌ **FUNDAMENTALLY UNAVAILABLE** |
| Suitability | NOT SUITABLE | **NOT SUITABLE (unchanged)** |

**Verdict**: PII constraints prevent collecting preference data. No training data possible.

### 4.5 Binary Admission (Any Seat)

| Aspect | Sprint 3.6 Assessment | Sprint 4.1 Re-assessment |
|--------|----------------------|--------------------------|
| Exact Definition | Binary: will student get ANY seat in system? | Unchanged |
| Label Availability | ⚠️ PARTIAL (MCC 2025 only) | ⚠️ **STILL 1 YEAR ONLY** |
| Leakage Risk | HIGH | Unchanged |
| Suitability | LOW | **LOW (unchanged)** |

**Verdict**: Single year insufficient. Limited actionability for counselling.

### 4.6 Vacancy After Round

| Aspect | Sprint 3.6 Assessment | Sprint 4.1 Re-assessment |
|--------|----------------------|--------------------------|
| Required Data | Vacancy reports | No vacancy canonical model |
| Label Availability | ❌ NO vacancy canonical model | ❌ **STILL NO CANONICAL MODEL** |
| Suitability | NONE | **NONE (unchanged)** |

---

## 5. Target Readiness Matrix (Current Evidence)

| Target | Label Available | Prediction-Time Features | Leakage Risk | Historical Years | Readiness |
|--------|-----------------|-------------------------|--------------|------------------|-----------|
| closing_rank | ✅ MCC 2025 | ✅ Seat matrix + prior years | HIGH (manageable) | **1** | **NO_TARGET_READY** |
| opening_rank | ❌ Not in canonical | ⚠️ Partial | HIGH | 1 | NO_TARGET_READY |
| admission_probability | ❌ No applicant pool | ❌ No | EXTREME | 0 | NO_TARGET_READY |
| seat_allocation | ❌ No preferences | ❌ No | EXTREME | 0 | NO_TARGET_READY |
| binary_admission | ⚠️ Partial (MCC 2025) | ⚠️ Partial | HIGH | 1 | NO_TARGET_READY |
| vacancy_after_round | ❌ No vacancy model | ❌ No | HIGH | 0 | NO_TARGET_READY |

---

## 6. What Would Be Needed to Enable a Target

Per `target-definition-phase4.md` Table (What Would Be Needed to Enable Modelling), re-evaluated:

| Requirement | Sprint 3.6 State | Sprint 4.1 State | Status |
|-------------|------------------|------------------|--------|
| MCC Historical Allotments | 2025 only | **2025 only** | ❌ **UNCHANGED** |
| State Historical Allotments | NONE | **NONE** | ❌ **UNCHANGED** |
| Minimum Years for Temporal Val | 1 | **1** | ❌ **UNCHANGED** |
| Verified UP Mappings | Placeholder | **Placeholder** | ❌ **UNCHANGED** |
| Vacancy Data | None | **None** | ❌ **UNCHANGED** |
| Opening Rank | Not in canonical | **Not in canonical** | ❌ **UNCHANGED** |

**No progress on any requirement** since Sprint 3.6. The data simply does not exist in the repository.

---

## 7. Decision

**TARGET STATUS: NO_TARGET_READY**

**Justification**:
1. **Insufficient Historical Coverage**: Only ONE year (MCC 2025) of allotment data exists with full contract/adapter/validation coverage. Temporal validation requires minimum 3 years.
2. **No State Historical Data**: Maharashtra, Karnataka, UP have ZERO historical allotment data in repository.
3. **Single Year Cannot Support Temporal Validation**: Train/validate/test split impossible with 1 year.
4. **Closing Rank Aggregation Gap**: While MCC 2025 allotments have per-record ranks, aggregated closing ranks per group are not in canonical model (would need derived feature, but still only 1 year).
5. **No Applicant Pool Data**: Admission likelihood targets require denominator (applicants), never published, PII protected.
6. **UP Mappings Unverified**: Category/quota mappings explicitly documented as placeholders.
6. **No New Evidence**: Sprint 4.1 did not obtain any new historical artifacts.

**This is an acceptable and scientifically honest outcome.** The evidence says we do NOT have enough trustworthy historical data to build a reliable NEET prediction target. The repository architecture is ready (Sprint 4.0 certified). The DATA is NOT.

---

## 8. Next Steps (If Evidence Changes)

If MCC 2021-2024 allotments are ingested and validated, and at least one state's historical allotments are ingested:

1. Re-run target evaluation with actual available fields
2. Verify label generation rules against real aggregated data
3. Assess leakage risk with actual temporal boundaries
4. Update `target-definition-phase4.md` with evidence-based readiness
5. Update `modelling_readiness.yaml` summary `first_modelling_target` field

**Until then**: `NO_TARGET_READY` remains the correct, evidence-based status.

---

*End of Target Readiness Investigation — Sprint 4.1*