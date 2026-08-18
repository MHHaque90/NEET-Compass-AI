# Reliability Metrics — Sprint 3.6

## Phase 8: Metrics Appropriate to Future Targets

This document defines the metrics that MUST be reported for any future model. "Accuracy" alone is NEVER sufficient.

---

### Metric Selection by Target Type

#### For Numeric Prediction (Closing Rank, Opening Rank)

| Metric | Formula | Why Required |
|--------|---------|--------------|
| **MAE** | mean(|y_pred - y_true|) | Interpretable, robust to outliers |
| **RMSE** | sqrt(mean((y_pred - y_true)²)) | Penalizes large errors |
| **Median Absolute Error** | median(|y_pred - y_true|) | Robust central tendency |
| **Quantile Coverage** | fraction(y_true in [q_low, q_high]) | For prediction intervals - MUST be ~90% for 90% interval |

**Thresholds**: Not fixed - compared against baselines (Phase 7)

---

#### For Classification / Probability (Admission Likelihood)

| Metric | Formula | Why Required |
|--------|---------|--------------|
| **Precision** | TP / (TP + FP) | Of predicted admits, how many actually admit |
| **Recall** | TP / (TP + FN) | Of actual admits, how many we predicted |
| **F1** | 2 * P * R / (P + R) | Harmonic mean |
| **ROC-AUC** | Area under ROC curve | Ranking quality |
| **PR-AUC** | Area under Precision-Recall curve | Better for imbalanced data |
| **Log Loss** | -mean(y*log(p) + (1-y)*log(1-p)) | Proper scoring rule |
| **Brier Score** | mean((p - y)²) | Proper scoring rule, calibrated |
| **Calibration Error (ECE)** | Σ|acc(bin) - conf(bin)| * P(bin) | **MANDATORY** for probabilities |
| **Calibration Plot** | Reliability diagram | Visual calibration check |

**Calibration is NON-NEGOTIABLE for any probability predictions.** Uncalibrated probabilities are misleading.

---

#### For Ranking (College Recommendation)

| Metric | Formula | Why Required |
|--------|---------|--------------|
| **Recall@K** | fraction(true in top K) | Of true admits, how many in top K |
| **Precision@K** | true in top K / K | Of top K, how many true |
| **NDCG@K** | Normalized DCG | Accounts for rank position |
| **MRR** | Mean Reciprocal Rank | First relevant item position |

---

### Mandatory Subgroup Analysis

When sample size permits (n ≥ 30 per subgroup), report ALL metrics by:

| Subgroup | Rationale |
|----------|-----------|
| **Year** | Temporal stability |
| **State/Authority** | MCC vs Maharashtra vs Karnataka vs UP |
| **Counselling Round** | Round 1, 2, 3, Stray |
| **Category** | gn, bc, ew, sc, st, *_pwd |
| **Quota** | ai, so, mm, du, am |
| **Data-Density** | High-history (≥10 prior obs) vs Low-history |

**If n < 30**: Report "Insufficient data (n=X)" - do NOT report metric.

---

### Reporting Format

Every model evaluation MUST produce a report with:

```
MODEL: <name> v<version>
DATASET: <dataset_version>
TARGET: <target_name>
SPLIT: <temporal_split_spec>

OVERALL METRICS:
  MAE: X.XX
  RMSE: X.XX
  MedAE: X.XX
  ...

SUBGROUP METRICS:
  year=2025: MAE=X.XX (n=XXX)
  year=2024: MAE=X.XX (n=XXX)
  ...
  authority=MCC: MAE=X.XX (n=XXX)
  authority=MAH: MAE=X.XX (n=XXX)
  ...
  round=1: MAE=X.XX (n=XXX)
  round=2: MAE=X.XX (n=XXX)
  ...
  category=gn: MAE=X.XX (n=XXX)
  category=sc: MAE=X.XX (n=XXX)
  ...
  quota=ai: MAE=X.XX (n=XXX)
  quota=so: MAE=X.XX (n=XXX)
  ...

BASELINE COMPARISON:
  Baseline 1 (prev year): MAE=X.XX
  Baseline 2 (multi-year median): MAE=X.XX
  Baseline 3 (seat ratio): MAE=X.XX
  ML Model: MAE=X.XX
  Improvement: X.XX% (p-value=X.XXX)

CALIBRATION (if probability):
  ECE: X.XXXX
  Reliability diagram: [path]

LEAKAGE AUDIT: PASS/FAIL
REPRODUCIBILITY: PASS/FAIL
```

---

### Metric Implementation Requirements

1. **Deterministic**: Same predictions + labels → same metrics
2. **Versioned**: Metric computation code versioned with model
3. **Tested**: Unit tests with known inputs/outputs
4. **No "accuracy" as sole metric**: Must include MAE/RMSE/Calibration as appropriate

---

### Acceptance Thresholds

**No arbitrary accuracy thresholds.** Thresholds are defined as:
- Must beat best baseline on primary metric
- Calibration error < 0.05 (for probabilities)
- Quantile coverage within 5% of nominal (for intervals)
- No subgroup with n≥30 shows >2x worse MAE than overall

Where thresholds are needed, they are **future acceptance criteria to be validated against baseline and use-case requirements**, not arbitrary numbers.