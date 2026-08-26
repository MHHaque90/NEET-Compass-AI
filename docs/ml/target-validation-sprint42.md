# Target Validation — Sprint 4.2

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 4.2 — Historical Dataset Expansion & Target Validation

---

## 1. Purpose

This document investigates candidate targets supported by actual available data, performs a leakage audit, and classifies target readiness with evidence-backed deterministic criteria.

---

## 2. Documents Reviewed

- `docs/ml/target-definition.md` (Sprint 3.6 Phase 3) — Canonical Modelling Dataset Definition
- `docs/ml/target-definition-phase4.md` (Sprint 3.6 Phase 4) — Target Analysis and First Modelling Target Selection
- `docs/ml/target-readiness-investigation-sprint41.md` (Sprint 4.1) — Target Readiness Investigation
- `modelling/targets/engine.py` — TargetEngine implementation

---

## 3. Current Verified Data Inventory (Repository Evidence)

| Authority | Dataset | Year | Round | Contract | Adapter | Validator | Provenance | Quality Gates |
|-----------|---------|------|-------|----------|---------|-----------|------------|---------------|
| MCC | seat_matrix | 2025 | Round 1 | v1.1.0 | ✅ | ✅ | ✅ | 15/15 |
| MCC | allotments | 2025 | Round 3 | v1.1.0 | ✅ | ✅ | ✅ | 15/15 |

**Total verified modelling-ready datasets**: 2 (both MCC 2025)
**Total verified modelling-ready years**: 1 (2025 only)

All other authority/year combinations have `NOT_READY` status with `evidence_status: NOT_VERIFIED` or `AUTOMATED_DOWNLOAD_BLOCKED`.

---

## 4. Candidate Targets Investigation

### 4.1 Closing Rank Forecasting

| Aspect | Detail |
|--------|--------|
| **1. Exact Definition** | Predict the closing rank (last admitted rank) for a given college × course × quota × category × round × year |
| **2. Source Fields** | `allotment_rank`, `counselling_year`, `institute_code`, `course`, `quota`, `category`, `round` |
| **3. Historical Availability** | MCC 2025 allotments only (1 year). Aggregated closing rank per group computable via `MAX(allotment_rank)` per college/course/quota/category/round/year |
| **4. Prediction Timestamp** | Before round commencement (e.g., before Round 1 for Round 1 prediction) |
| **5. Information Available at Prediction Time** | College, course, quota, category, round, year, seat matrix (total_seats), prior years' closing ranks (if historical data exists) |
| **6. Information Unavailable at Prediction Time** | Current round allotment ranks, current round competition, applicant preferences |
| **7. Label Generation Rule** | `MAX(allotment_rank)` per college/course/quota/category/round/year |
| **8. Missing Data Behaviour** | NULL if no allotments for group |
| **9. Leakage Risk** | HIGH — Using Round 3 data to predict Round 1 leaks future seat availability. Must only use rounds < prediction round, years < prediction year. |
| **10. Provenance** | Source: Allotment canonical records. Aggregation: MAX per group. Version: v1 |
| **11. Minimum Historical Requirements** | ≥3 verified years for temporal validation (train/validate/test) |
| **12. Validation Requirements** | Temporal split: train on oldest years, validate on middle, test on newest. No future information in features. |
| **13. Failure Conditions** | <3 verified years → NO_TARGET_READY. Leakage detected → REJECTED. |

### 4.2 Opening Rank Forecasting

| Aspect | Detail |
|--------|--------|
| **1. Exact Definition** | Predict the opening rank (first admitted rank) for a given college × course × quota × category × round × year |
| **2. Source Fields** | `allotment_rank`, `counselling_year`, `institute_code`, `course`, `quota`, `category`, `round` |
| **3. Historical Availability** | ❌ NOT in canonical model. Allotment has single rank per record (not opening/closing). Would need `MIN(allotment_rank)` aggregation. MCC 2025 only (1 year). |
| **4. Prediction Timestamp** | Before round commencement |
| **5. Information Available at Prediction Time** | Same as closing rank |
| **6. Information Unavailable at Prediction Time** | Same as closing rank |
| **7. Label Generation Rule** | `MIN(allotment_rank)` per college/course/quota/category/round/year |
| **8. Missing Data Behaviour** | NULL if no allotments for group |
| **9. Leakage Risk** | HIGH — Same as closing rank |
| **10. Provenance** | Source: Allotment canonical records. Aggregation: MIN per group. Version: v1 |
| **11. Minimum Historical Requirements** | ≥3 verified years + opening rank in canonical model |
| **12. Validation Requirements** | Same as closing rank |
| **13. Failure Conditions** | Opening rank not in canonical model. <3 verified years → NO_TARGET_READY. |

### 4.3 Admission Probability

| Aspect | Detail |
|--------|--------|
| **1. Exact Definition** | P(admitted \| student_rank, college, course, quota, category, round) |
| **2. Source Fields** | Allotment records + student rank distribution + preference data |
| **3. Historical Availability** | ❌ NO applicant pool data (never published). ❌ NO student preference data (PII protected). |
| **4. Prediction Timestamp** | Before round commencement |
| **5. Information Available at Prediction Time** | Student rank, category, quota, college, course, round, seat matrix |
| **6. Information Unavailable at Prediction Time** | Applicant pool size, student preferences, competition intensity |
| **7. Label Generation Rule** | Cannot be computed without applicant pool and preferences |
| **8. Missing Data Behaviour** | N/A — Target not computable |
| **9. Leakage Risk** | EXTREME — Requires applicant pool and preferences (fundamentally unavailable) |
| **10. Provenance** | Not available. Fundamentally unidentifiable. |
| **11. Minimum Historical Requirements** | Applicant pool data (never published) + preference data (PII) |
| **12. Validation Requirements** | Impossible without denominator data |
| **13. Failure Conditions** | NO applicant pool data ever published. NO preference data (PII). REJECTED. |

### 4.4 Seat Allocation (Multi-class)

| Aspect | Detail |
|--------|--------|
| **1. Exact Definition** | Which college/course/quota/category a student gets |
| **2. Source Fields** | Allotment records + student preferences |
| **3. Historical Availability** | ❌ NO student preference data (PII protected). |
| **4. Prediction Timestamp** | Before round commencement |
| **5. Information Available at Prediction Time** | Student rank, category, quota, stated preferences (at prediction time) |
| **6. Information Unavailable at Prediction Time** | Historical preferences, other students' preferences |
| **7. Label Generation Rule** | Cannot be computed without student preferences |
| **8. Missing Data Behaviour** | N/A — Target not computable |
| **9. Leakage Risk** | EXTREME — Uses final allotment; preference data unavailable |
| **10. Provenance** | Not available. PII constraints prevent collecting preference data. |
| **11. Minimum Historical Requirements** | Historical preference data (PII - not available) |
| **12. Validation Requirements** | Impossible |
| **13. Failure Conditions** | PII constraints. REJECTED. |

### 4.5 Binary Admission (Any Seat)

| Aspect | Detail |
|--------|--------|
| **1. Exact Definition** | Binary: Given student rank, category, quota, round — will they get ANY seat in the system? |
| **2. Source Fields** | Allotment records showing which ranks got seats, seat matrix |
| **3. Historical Availability** | ⚠️ PARTIAL — MCC 2025 only. Can see which (rank, category, quota, round) combinations received seats. |
| **4. Prediction Timestamp** | Before round commencement |
| **5. Information Available at Prediction Time** | Student rank, category, quota, round, total seats from seat matrix |
| **6. Information Unavailable at Prediction Time** | How many higher-ranked applicants will choose those seats, preference heterogeneity |
| **7. Label Generation Rule** | Binary: 1 if rank ≤ max admitted rank for category/quota/round, else 0 |
| **8. Missing Data Behaviour** | NULL if no seat matrix or allotment data |
| **9. Leakage Risk** | HIGH — Using final allotment status leaks seat competition info |
| **10. Provenance** | Source: Allotment canonical records + SeatMatrix. Version: v1 |
| **11. Minimum Historical Requirements** | ≥3 verified years |
| **12. Validation Requirements** | Temporal split with no future info |
| **13. Failure Conditions** | <3 verified years. Limited actionability for counselling. |

### 4.6 Vacancy After Round

| Aspect | Detail |
|--------|--------|
| **1. Exact Definition** | Seats remaining after each round |
| **2. Source Fields** | Vacancy reports, seat matrix, allotments |
| **3. Historical Availability** | ❌ NO vacancy canonical model. No vacancy data ingested. |
| **4. Prediction Timestamp** | After round completion |
| **5. Information Available at Prediction Time** | Prior rounds' vacancy, seat matrix, allotments |
| **6. Information Unavailable at Prediction Time** | Current round vacancy (that's the target) |
| **7. Label Generation Rule** | Vacancy report data per college/course/quota/category/round |
| **8. Missing Data Behaviour** | NULL if no vacancy report |
| **9. Leakage Risk** | HIGH — Uses vacancy data from same round |
| **10. Provenance** | Not available. No vacancy canonical model exists. |
| **11. Minimum Historical Requirements** | Vacancy canonical model + ingestion + ≥3 years |
| **12. Validation Requirements** | Vacancy model implementation first |
| **13. Failure Conditions** | No vacancy canonical model. REJECTED. |

---

## 5. Target Leakage Audit

### 5.1 Leakage Classification Rules

Per `modelling/targets/engine.py` and `modelling/leakage/checker.py`:

- **FUTURE TARGET INFORMATION → REJECTED**
- **UNKNOWN TARGET TEMPORALITY → REJECTED**
- **MISSING PROVENANCE → NOT_READY**
- **INVALID TARGET → NO_TARGET_READY**

### 5.2 Leakage Analysis per Target

| Target | Leakage Classification | Audit Result |
|--------|------------------------|--------------|
| closing_rank | HIGH_RISK — Must only use rounds < prediction round, years < prediction year | **CONDITIONALLY ACCEPTABLE** if temporal split enforced. Features must only use data from years < target year. |
| opening_rank | HIGH_RISK — Same as closing rank | **CONDITIONALLY ACCEPTABLE** if opening rank added to canonical and temporal split enforced. |
| admission_probability | EXTREME_RISK — Requires applicant pool and preferences (fundamentally unavailable) | **REJECTED** — Future target information (applicant pool) never available. |
| seat_allocation | EXTREME_RISK — Uses final allotment + preferences (PII) | **REJECTED** — Future target information (preferences) never available. |
| binary_admission | HIGH_RISK — Uses final allotment status | **CONDITIONALLY ACCEPTABLE** if temporal split enforced. Limited actionability. |
| vacancy_after_round | HIGH_RISK — Uses vacancy data from same round | **REJECTED** — No vacancy canonical model. Unknown temporality. |

### 5.3 Critical Leakage Findings

1. **All computable targets (closing_rank, opening_rank, binary_admission) have HIGH leakage risk** that is only manageable with strict temporal splits (train on years < test year, validate on middle year).

2. **Admission probability and seat allocation are FUNDAMENTALLY REJECTED** because they require data that is never published (applicant pool) or is PII-protected (preferences).

3. **Vacancy target is REJECTED** because no vacancy canonical model exists, making temporal availability UNKNOWN.

4. **Temporal availability for closing_rank**: Labels become available AFTER round completion. For prediction BEFORE round, labels from prior years are available. This is valid IF temporal split uses only prior years.

---

## 6. Target Readiness Classification

### 6.1 Classification Criteria (Deterministic, Evidence-Backed)

| Classification | Criteria |
|----------------|----------|
| **READY** | Target definition complete, source fields available in ≥3 verified years, label generation rule executable, temporal availability confirmed, leakage risk manageable, provenance complete, all validation requirements met |
| **READY_WITH_LIMITATIONS** | Target definition complete, source fields available in <3 verified years OR minor limitations documented, temporal availability confirmed, leakage risk manageable, provenance complete |
| **NOT_READY** | Target definition incomplete, source fields unavailable, temporal availability UNKNOWN, leakage risk UNMANAGEABLE, provenance incomplete |
| **NO_TARGET_READY** | No candidate target meets READY or READY_WITH_LIMITATIONS criteria |

### 6.2 Classification Results

| Target | Classification | Evidence |
|--------|----------------|----------|
| closing_rank | **NO_TARGET_READY** | Only 1 verified year (MCC 2025). Need ≥3 for temporal validation. Leakage risk HIGH but manageable. |
| opening_rank | **NO_TARGET_READY** | Not in canonical model. Only 1 verified year. |
| admission_probability | **NO_TARGET_READY** | Fundamentally unidentifiable. No applicant pool data ever. PII constraints. |
| seat_allocation | **NO_TARGET_READY** | Fundamentally unidentifiable. No preference data (PII). |
| binary_admission | **NO_TARGET_READY** | Only 1 verified year. Limited actionability. |
| vacancy_after_round | **NO_TARGET_READY** | No vacancy canonical model. Unknown temporality. |

### 6.3 Decision

**TARGET STATUS: NO_TARGET_READY**

**Justification**:
1. **Insufficient Historical Coverage**: Only ONE year (MCC 2025) of allotment data exists with full contract/adapter/validation coverage. Temporal validation requires minimum 3 years.
2. **No State Historical Data**: Maharashtra, Karnataka, UP have ZERO historical allotment data in repository.
3. **Single Year Cannot Support Temporal Validation**: Train/validate/test split impossible with 1 year.
4. **Opening Rank Aggregation Gap**: Not in canonical model (would need derived feature, but still only 1 year).
5. **No Applicant Pool Data**: Admission likelihood targets require denominator (applicants), never published, PII protected.
6. **UP Mappings Unverified**: Category/quota mappings explicitly documented as placeholders.
7. **No New Evidence**: Sprint 4.2 did not obtain any new historical artifacts.

**This is an acceptable and scientifically honest outcome.** The evidence says we do NOT have enough trustworthy historical data to build a reliable NEET prediction target. The repository architecture is ready (Sprint 4.0 certified). The DATA is NOT.

---

## 7. Conditions Required Before Any Target Can Be READY

To enable a target (most viable: `closing_rank`), ALL of the following must be satisfied with actual repository evidence:

1. **MCC 2021-2024 allotments** ingested and validated (contract v1.1.0 compatible or new version)
2. **At least one state's historical allotments** (Maharashtra/Karnataka/UP) ingested and validated
3. **Minimum 4 years of data** for temporal validation (e.g., 2021-2024 train, 2025 validate, 2026 test)
4. **UP category/quota mappings** verified against real UP source data (if UP data used)
5. **Leakage checks pass** — no future information in features
6. **All 15 data quality gates pass** for the combined dataset
7. **Provenance complete** — all 10 fields for every source file
8. **Target explicitly defined** — not `NO_TARGET_READY`

**No single artifact unblocks a target.** It requires a coherent body of verified historical evidence meeting all gates simultaneously.

---

## 8. Next Steps (Conditional)

If MCC 2021-2024 allotments are ingested and validated, and at least one state's historical allotments are ingested:

1. Re-run target evaluation with actual available fields
2. Verify label generation rules against real aggregated data
3. Assess leakage risk with actual temporal boundaries
4. Update `target-definition-phase4.md` with evidence-based readiness
5. Update `modelling_readiness.yaml` summary `first_modelling_target` field

**Until then**: `NO_TARGET_READY` remains the correct, evidence-based status.

---

*End of Target Validation — Sprint 4.2*