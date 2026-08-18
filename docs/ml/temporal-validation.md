# Temporal Validation Strategy — Sprint 3.6

## Phase 6: Chronological Evaluation Strategy

This document defines the evaluation strategy for future models. Random train/test splitting is NOT the primary evaluation strategy. The evaluation must simulate how the model would perform on a future counselling year it has never seen.

---

### Core Principle

**The final evaluation MUST simulate production: train on past, validate on recent past, test on unseen future.**

Random splitting leaks temporal information and overestimates real-world performance.

---

### Required Historical Data for Validation

Based on Phase 1 inventory, the ONLY verified data with contracts/adapters is:
- MCC 2025: Seat Matrix (Round 1) + Allotments (Round 3)

**This is INSUFFICIENT for any temporal validation.** Minimum 3 years needed (train/validate/test), preferably 5+.

---

### Validation Strategy (When Data Exists)

#### Preferred Structure: Forward-Chaining / Rolling Origin

```
Year T-3, T-2, T-1  →  TRAIN
Year T              →  VALIDATION
Year T+1            →  UNSEEN TEST (held out until final evaluation)
```

Where T = latest verified year.

#### Example (Hypothetical - NOT current reality)

If we had MCC 2021-2025 allotments verified:
```
Train:     2021, 2022, 2023
Validate:  2024
Test:      2025 (held out, used ONCE for final report)
```

#### Rolling Validation (if enough years)

If we had 2021-2026 (6 years):
```
Fold 1: Train 2021-2022 → Val 2023 → Test 2024
Fold 2: Train 2021-2023 → Val 2024 → Test 2025
Fold 3: Train 2021-2024 → Val 2025 → Test 2026
```

Report: Mean and std of test metrics across folds.

---

### Within-Year Validation (Round-Level)

For a given year, rounds are temporally ordered:
```
Round 1 → Round 2 → Round 3 → Stray Vacancy
```

**Within-year validation for round prediction:**
```
Train:     Round 1 data
Validate:  Round 2 data
Test:      Round 3 data (or Stray)
```

But: Round 1 features for predicting Round 2 can use Round 1 allotments (available before Round 2). Round 2 features for predicting Round 3 can use Round 1+2 allotments.

This is round-level forward chaining within a year.

---

### Cross-Authority Validation

If multiple authorities have data:
```
Train:     MCC 2021-2024 + Maharashtra 2021-2024 + Karnataka 2021-2024
Validate:  MCC 2025 + Maharashtra 2025 + Karnataka 2025
Test:      2026 (all authorities)
```

But: Must account for authority-specific patterns. Stratify by authority.

---

### Subgroup Evaluation (Mandatory)

When sample size permits (n ≥ 30 per group), report metrics by:
- **Year** (each test year separately)
- **State/Authority** (MCC vs Maharashtra vs Karnataka vs UP)
- **Counselling Round** (Round 1, 2, 3, Stray)
- **Category** (gn, bc, ew, sc, st, *_pwd)
- **Quota** (ai, so, mm, du, am)
- **Data-Density Group** (colleges with >100 historical records vs <10)

**Do NOT report subgroup metrics when sample size < 30.** Mark as "insufficient data".

---

### Metrics for Validation

Per Phase 8 (Reliability Metrics), the following MUST be reported:

**For numeric targets (closing rank):**
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- Median Absolute Error
- Quantile Coverage (if prediction intervals produced)

**For ranking targets:**
- Recall@K (K=1, 5, 10, 20)
- Precision@K
- NDCG@K
- MRR

**For probability targets:**
- Precision, Recall, F1
- ROC-AUC, PR-AUC
- Log Loss
- Brier Score
- Calibration Error (ECE)

**Calibration is MANDATORY for any probability predictions.**

---

### Current Reality Check

**As of Sprint 3.6, temporal validation CANNOT BE PERFORMED because:**

| Requirement | Status |
|-------------|--------|
| Minimum 3 verified years | ❌ Only 1 year (MCC 2025) |
| Train/Validate/Test split | ❌ Impossible |
| Rolling validation | ❌ Impossible |
| Subgroup by year | ❌ Only 1 year |
| Cross-authority validation | ❌ Only MCC has data |

**The validation strategy is defined for WHEN data exists. Currently, it is a specification for future use.**

---

### Implementation Requirements for Future ML

1. **TemporalSplitter Class**: A scikit-learn compatible splitter that enforces temporal splits
2. **Validation Pipeline**: Automated pipeline that runs forward-chaining validation
3. **Leakage Audit**: Automated check that no test-year data appears in train features
4. **Subgroup Reporter**: Automatic subgroup metric computation with sample size guards
5. **Calibration Plotter**: Reliability diagrams for probability predictions

---

### Acceptance Criteria for Validation

A model passes validation ONLY if:
- [ ] Out-of-time test metrics meet baseline comparison (Phase 7)
- [ ] Calibration error < threshold (for probabilities)
- [ ] No subgroup shows catastrophic failure (with sufficient n)
- [ ] Temporal leakage audit passes
- [ ] Metrics reported per year, per authority, per round, per category
- [ ] Prediction intervals have correct coverage (if applicable)

---

### Summary

**Current State**: Validation strategy defined but CANNOT BE EXECUTED due to insufficient historical data.

**Required to Execute**: Minimum 3 verified years of allotment data per authority (preferably 5+), with at least 2 authorities.

**This is not a blocker for Sprint 3.6 - it's a documented prerequisite for Sprint 3.7+.**