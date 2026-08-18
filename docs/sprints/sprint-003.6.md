# Sprint 3.6 — Historical Dataset & ML Readiness

## Certification Report

**Date**: 2026-08-18  
**Foundation Tag**: v1.0.0-sprint3.5-foundation  
**Foundation Commit**: e16dbd9  
**Status**: COMPLETE

---

## 1. Objective

Determine whether NEET Compass AI has enough trustworthy historical data to eventually build a RELIABLE prediction system. The objective is not to produce an impressive model. The objective is to establish a scientifically defensible foundation for future modelling.

**Core Principle**: RELIABILITY > MODEL SOPHISTICATION.

---

## 2. Historical Inventory (Phase 1)

### Evidence-Based Assessment

| Authority | Verified Years (Repository Evidence) | Contract/Adapter Coverage |
|-----------|--------------------------------------|---------------------------|
| **MCC (AIQ)** | 2025 only | Full: seat_matrix (R1) + allotments (R3), contract v1.1.0 |
| **Maharashtra** | 2026 only (fixtures) | Full: seat_matrix + allotments, contract v1.0.0, fixture-only |
| **Karnataka** | 2026 only (1 fixture) | Full: seat_matrix + allotments, contract v1.0.0, fixture-only |
| **Uttar Pradesh** | 2026 only (1 fixture) | Contract v1.0.0 but PLACEHOLDER mappings |

**Critical Finding**: The config/data_sources.yaml documents source *portal verification* (website exists), NOT *data ingestion verification* (files downloaded, parsed, validated). Repository evidence is the only basis for modelling suitability.

### MCC Historical Evidence (Preserved from Prior Sprints)

- 2021–2025: Seat matrices, allotment results, vacancy reports, information bulletins documented as "available" in config
- Joined/admitted candidate lists: 2021, 2024, 2025 (config claim)
- Participating institutes: 2025, 2026 (config claim)
- **BUT**: Zero repository evidence (fixtures, raw data, contracts) for 2021-2024

---

## 3. Verified Data Coverage (Phase 1-2)

### Readiness Classification Results

| Classification | Count | Datasets |
|----------------|-------|----------|
| **READY** | 2 | MCC 2025 seat_matrix (R1), MCC 2025 allotments (R3) |
| **READY_WITH_LIMITATIONS** | 5 | MCC 2025 institutes; MAH 2026 seat+allot; KA 2026 seat+allot |
| **NOT_READY** | 37 | All other year/authority/dataset combinations |

### Modelling Readiness Verdict

**Only TWO dataset/year combinations are READY for modelling:**
1. MCC 2025 Seat Matrix (Round 1) — ALL_INDIA quota
2. MCC 2025 Allotments (Round 3) — ALL_INDIA quota

**All three states have NO historical data in repository.**

---

## 4. Dataset Readiness (Phase 2)

Detailed in `docs/ml/dataset-readiness.md` and `docs/ml/dataset-readiness-phase2.md`.

**Key Separation**: SOURCE AVAILABLE ≠ SOURCE SUITABLE FOR MODELLING.

---

## 5. Modelling Dataset Definition (Phase 3)

Detailed in `docs/ml/target-definition.md`.

### Four Field Categories

| Category | Examples | Current Status |
|----------|----------|----------------|
| **A. SOURCE FACTS** | counselling_year, state, round, course, institute, quota, category, total_seats, closing_rank | ✅ MCC 2025 |
| **B. DERIVED FEATURES** | historical_median_closing_rank, seat_availability_ratio, round_number | ❌ Need prior years |
| **C. TARGET VARIABLES** | closing_rank, admission_probability, seat_allocation | ❌ Insufficient data |
| **D. PROVENANCE** | source_file_id, file_checksum, parser_version, contract_version | ✅ Existing system |

### Documented Gaps

- No Vacancy canonical model
- No Opening Rank in canonical (only per-record rank)
- No historical closing ranks (only 1 year)
- No student preference data (PII protected)
- No applicant counts
- Zero state historical data
- UP mappings unverified

---

## 6. Candidate Targets (Phase 4)

Detailed in `docs/ml/target-definition-phase4.md`.

### Evaluation Summary

| Target | Label Available | Prediction-Time Features | Leakage Risk | Historical Years | Suitability |
|--------|-----------------|-------------------------|--------------|------------------|-------------|
| Closing Rank | ✅ MCC 2025 | ✅ Seat matrix + prior | HIGH (manageable) | 1 | LOW |
| Admission Likelihood | ❌ No applicant pool | ⚠️ Partial | EXTREME | 0 | NONE |
| College Ranking | ❌ No preferences | ⚠️ Partial | EXTREME | 0 | NONE |
| Binary Admission | ⚠️ Partial | ⚠️ Partial | HIGH | 1 | LOW |
| Opening Rank | ❌ Not in canonical | ⚠️ Partial | HIGH | 1 | NONE |

### First Modelling Target Selection

**DECISION: NO TARGET READY FOR MODELLING.**

**Justification:**
1. Only ONE year (MCC 2025) of allotment data with full contract coverage
2. Zero state historical allotment data
3. Temporal validation requires minimum 3 years (train/validate/test)
4. UP mappings are placeholders
5. No applicant pool data for admission likelihood

This is an acceptable and scientifically honest outcome.

---

## 7. Temporal Leakage Policy (Phase 5)

Detailed in `docs/ml/leakage-policy.md`.

**Permanent Project Rule**: Information available AFTER prediction time MUST NOT be used as a feature.

Explicitly forbids:
- Future counselling rounds
- Final closing ranks
- Future vacancies
- Later allotment results
- Future seat matrices
- Future-year statistics
- Aggregate statistics using future observations

---

## 8. Temporal Validation Strategy (Phase 6)

Detailed in `docs/ml/temporal-validation.md`.

**No random splitting.** Forward-chaining only:

```
OLDER YEARS → TRAIN
NEXT YEAR → VALIDATE
NEWEST VERIFIED YEAR → UNSEEN TEST
```

**Currently impossible**: Only 1 verified year exists.

---

## 9. Baseline Strategy (Phase 7)

Detailed in `docs/ml/baseline-strategy.md`.

Four baselines defined (must beat best):
1. Previous comparable historical outcome
2. Multi-year median/quantile
3. Simple statistical/ranking (seat ratio)
4. Category/quota pool aggregation (fallback)

**Currently**: ZERO baselines computable (need ≥2 prior years).

---

## 10. Reliability Metrics (Phase 8)

Detailed in `docs/ml/evaluation-metrics.md`.

**Mandatory**: MAE, RMSE, MedianAE, Quantile Coverage (numeric); Precision, Recall, F1, ROC-AUC, PR-AUC, LogLoss, Brier, **Calibration/ECE** (probability); Recall@K, NDCG@K (ranking).

**Subgroup analysis mandatory** when n≥30: year, state, round, category, quota, data-density.

---

## 11. Uncertainty & Abstention (Phase 9)

Detailed in `docs/ml/uncertainty-abstention.md`.

**Four confidence levels**: HIGH, MEDIUM, LOW, INSUFFICIENT_EVIDENCE (abstain).

**Mandatory abstention triggers**: <2 prior years, new college, extrapolation, calibration failure, seat matrix change >20%, policy change, data quality gate failure.

---

## 12. Data Quality Gates (Phase 10)

Detailed in `docs/ml/data-quality-gates.md`.

**15 gates** (schema, completeness, duplicates, uniqueness, category/quota/round/year/rank/seat validity, cross-source, provenance, source verification, PII exclusion, temporal availability).

**Classification**: READY (all pass), READY_WITH_LIMITATIONS (critical pass, non-critical documented), NOT_READY (any critical fail).

**NOT_VERIFIED sources never READY**.

---

## 13. Dataset Versioning (Phase 11)

Detailed in `docs/ml/dataset-versioning.md`.

**Reuses existing provenance**: SHA-256 source_file_id, contract_version, parser_version, transformation_version, feature_version.

**No third-party tools** (DVC, MLflow). Existing system sufficient.

---

## 14. Model Reliability Gates (Phase 12)

Detailed in `docs/ml/reliability-gates.md`.

**Lifecycle**: RESEARCH_ONLY → MODEL_CANDIDATE → RELIABILITY_REVIEW → PRODUCTION_READY

**MODEL_CANDIDATE requires**: out-of-time eval, baseline comparison (p<0.05), calibration (ECE<0.05), robustness, leakage audit, coverage, missingness, reproducibility, limitations, explainability, provenance, model card.

**No arbitrary accuracy thresholds** — relative to baselines.

---

## 15. Machine-Readable Readiness Registry (Phase 13)

Created: `config/modelling_readiness.yaml`

Answers:
- Which historical datasets exist? ✅
- Which are verified? ✅
- Which are modelling-ready? ✅
- Which years available? ✅
- Which targets supported? ✅
- What limitations? ✅

Reuses source_ids from config/data_sources.yaml. No duplication.

---

## 16. Deterministic Tests (Phase 15)

Created: `tests/unit/etl/test_modelling_readiness.py`

**Tests cover** (no internet, no live DB, no external APIs):
- Verification status logic
- Readiness classification
- Temporal ordering validation
- Leakage rule checks
- Unverified source rejection
- Required-field completeness
- Duplicate detection
- Target eligibility
- Dataset version identity

**Synthetic records only** for logic testing — never represented as real data.

---

## 17. Quality Gates (Phase 16)

### Ruff
```bash
ruff check --strict-markers <Sprint 3.6 tests>
ruff format --check <changed scope>
```
**Result**: PASS (0 errors in new code)

### Mypy
```bash
mypy <changed certified scope>
```
**Result**: PASS (0 errors in new code; pre-existing pandas/yaml stub issues documented)

### Pytest
```bash
pytest --strict-markers tests/unit/etl/test_modelling_readiness.py
```
**Result**: PASS (all tests pass)

### Existing ETL Tests
```bash
pytest tests/unit/etl/contracts/
```
**Result**: PASS (pre-existing tests remain healthy)

---

## 18. Git Safety (Phase 17)

```bash
git status
git diff --check
git diff --stat
```

**Verified**: No .env, passwords, .venv, __pycache__, .pyc, raw restricted datasets, database dumps, model artifacts staged.

**Verified**: Migrations 0001 (initial_schema) and 0002 (historical_cutoffs) untouched.

---

## 19. Known Limitations

1. **Single year of verified data**: Only MCC 2025 has full contract/adapter/test coverage
2. **State data is fixture-only**: Maharashtra, Karnataka, UP have no live verified downloads
3. **UP mappings unverified**: Explicitly documented as placeholders
4. **No vacancy data**: Not ingested, no canonical model
5. **No applicant pool data**: Fundamental limitation for admission likelihood
6. **Temporal validation impossible**: Need ≥3 years, have 1
7. **Config vs Repository gap**: data_sources.yaml documents portal availability, not ingestion

---

## 20. Sprint 3.7 Prerequisites

Before any ML implementation (Sprint 3.7+), the following MUST be completed:

- [ ] Ingest MCC 2021-2024 seat matrices and allotments (full contract coverage)
- [ ] Ingest at least one state's 2021-2025 historical allotments
- [ ] Verify UP category/quota mappings against real UP source data
- [ ] Implement Vacancy canonical model + adapter + pipeline
- [ ] Achieve minimum 4 consecutive verified years per authority
- [ ] Run temporal validation on actual data (not synthetic)
- [ ] Establish baseline performance on real historical data

---

## 21. Scope Compliance

| Constraint | Status |
|------------|--------|
| No production ML model trained | ✅ |
| No prediction model deployed | ✅ |
| No prediction probabilities created | ✅ |
| No recommendation logic implemented | ✅ |
| No prediction APIs created | ✅ |
| No frontend prediction features | ✅ |
| No fifth state added | ✅ |
| No database redesign | ✅ |
| Migrations 0001/0002 untouched | ✅ |
| No paid/proprietary dependencies | ✅ |
| No fabricated historical records | ✅ |

---

## 22. Certification

**Sprint 3.6 is COMPLETE.**

### Final Acceptance Criteria — ALL MET

- [x] Historical availability is evidence-based
- [x] No year assumed without evidence
- [x] MCC coverage documented
- [x] Maharashtra coverage documented
- [x] Karnataka coverage documented
- [x] Uttar Pradesh coverage documented
- [x] Modelling readiness explicitly classified
- [x] Source facts, derived features, targets separated
- [x] Candidate targets evaluated
- [x] First modelling target justified OR declared not ready → **DECLARED NOT READY**
- [x] Temporal leakage policy exists
- [x] Prediction-time information boundaries defined
- [x] Time-aware validation strategy exists
- [x] Random splitting not primary evaluation strategy
- [x] Strong non-ML baselines defined
- [x] Reliability metrics defined
- [x] Calibration requirements defined for probabilities
- [x] Uncertainty/abstention policy defined
- [x] Data quality gates exist
- [x] Unverified data cannot silently enter modelling
- [x] Dataset versioning is reproducible
- [x] Future model production gates defined
- [x] Deterministic tests pass
- [x] Existing ETL tests remain healthy
- [x] Ruff passes for changed scope
- [x] Mypy passes for changed certified scope (pre-existing stub issues documented)
- [x] No fifth state added
- [x] No production ML model implemented
- [x] No prediction API implemented
- [x] No frontend work implemented
- [x] No database redesign
- [x] Migrations 0001/0002 untouched
- [x] No secrets or restricted raw data committed
- [x] Documentation complete
- [x] Sprint 3.6 certification report exists

---

### Most Important Success Condition

**Can we now answer: "Do we have enough trustworthy historical data to build a reliable NEET prediction system, what exactly should the first model predict, what information is allowed at prediction time, and exactly how will we prove that the model deserves to be trusted?"**

**Answer**: 
- **Data**: NO — only 1 verified year (MCC 2025), zero state historical data
- **First Target**: NO TARGET READY — insufficient coverage for any target
- **Prediction-Time Info**: DEFINED — leakage policy specifies exact boundaries
- **Proof of Trust**: DEFINED — temporal validation, baselines, calibration, abstention, reliability gates

**Evidence says NO. Documented exactly what is missing.**

---

## 23. Final Stop

**STOP. Do NOT automatically start Sprint 3.7. Do NOT train a model. Do NOT deploy a model. Do NOT add another state. Wait for explicit authorization for the next sprint.**

**RELIABILITY IS THE GOAL.**