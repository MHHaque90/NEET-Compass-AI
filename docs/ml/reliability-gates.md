# Model Reliability Gates — Sprint 3.6

## Phase 12: Future Model Lifecycle and Production Gates

This document defines the mandatory lifecycle gates for any future ML model. A model must earn the right to be called "production-ready."

---

### Model Lifecycle Stages

```
RESEARCH_ONLY
    ↓
MODEL_CANDIDATE
    ↓
RELIABILITY_REVIEW
    ↓
PRODUCTION_READY
```

**No stage skipping. No exceptions.**

---

### Stage 1: RESEARCH_ONLY

**Entry**: Any experiment, notebook, prototype.

**Requirements**:
- [ ] Code in version control
- [ ] Trained on READY/READY_WITH_LIMITATIONS data only
- [ ] Temporal validation strategy followed (Phase 6)
- [ ] Leakage audit passed (Phase 5)
- [ ] Metrics computed per Phase 8

**Artifacts**: Model weights, training logs, metric reports

**Cannot**: Be served to users, used in API, mentioned in user-facing docs

---

### Stage 2: MODEL_CANDIDATE

**Entry**: Research model that beats baselines and passes initial review.

**Requirements** (ALL mandatory):
- [ ] **Out-of-time evaluation**: Tested on held-out future year (Phase 6)
- [ ] **Baseline comparison**: Beats best baseline on primary metric with p < 0.05
- [ ] **Calibration**: ECE < 0.05 (if probabilities produced)
- [ ] **Robustness testing**: Performance stable across subgroups (n≥30)
- [ ] **Temporal leakage audit**: Automated check passes
- [ ] **Sufficient data coverage**: Training data covers ≥80% of prediction subgroups
- [ ] **Acceptable missingness**: <5% missing features in test set
- [ ] **Reproducibility**: Fixed seed → identical metrics; dataset_version logged
- [ ] **Documented limitations**: Explicit failure modes, abstention triggers
- [ ] **Explainability**: Feature importance / SHAP / coefficients documented
- [ ] **Provenance**: Full trace to dataset_version, model_version, code_version
- [ ] **Model/version traceability**: MLflow or equivalent tracking (model_id, params, metrics)

**Artifacts**: Signed model card, evaluation report, leakage audit log

**Cannot**: Be served to users without RELIABILITY_REVIEW approval

---

### Stage 3: RELIABILITY_REVIEW

**Entry**: MODEL_CANDIDATE submitted for independent review.

**Review Panel**: At minimum 2 engineers not involved in model development.

**Review Checklist**:
- [ ] All MODEL_CANDIDATE requirements verified
- [ ] Leakage audit independently reproduced
- [ ] Baseline comparison independently reproduced
- [ ] Subgroup analysis reviewed for fairness/safety
- [ ] Abstention policy (Phase 9) implemented and tested
- [ ] Calibration plots reviewed
- [ ] Failure modes documented and acceptable
- [ ] Monitoring plan defined (drift detection, performance tracking)
- [ ] Rollback plan defined
- [ ] Security review (no PII in model, no data leakage)

**Decision**: PASS → PRODUCTION_READY | FAIL → Back to MODEL_CANDIDATE with blocking issues

**Artifacts**: Review report, signed approval, monitoring config

---

### Stage 4: PRODUCTION_READY

**Entry**: Passed RELIABILITY_REVIEW.

**Requirements**:
- [ ] Model registered in model registry with version
- [ ] Serving infrastructure deployed (API, batch, etc.)
- [ ] Monitoring active (drift, performance, latency)
- [ ] Alerting configured (performance degradation, data drift)
- [ ] Documentation updated (user-facing)
- [ ] Rollback tested

**Can**: Be served to users

**Ongoing**: Continuous monitoring, periodic re-evaluation

---

### Minimum Evidence Checklist (for RELIABILITY_REVIEW)

| Evidence | Required | Verification |
|----------|----------|--------------|
| Out-of-time test metrics | ✅ | Independent reproduction |
| Baseline comparison (with p-value) | ✅ | Independent reproduction |
| Calibration (ECE, reliability diagram) | ✅ if probabilities | Visual + numeric |
| Subgroup metrics (n≥30) | ✅ | Table in report |
| Leakage audit log | ✅ | Automated check output |
| Data coverage report | ✅ | % subgroups covered |
| Missingness report | ✅ | % missing per feature |
| Reproducibility proof | ✅ | Fixed seed = same metrics |
| Limitations document | ✅ | Written and reviewed |
| Explainability artifacts | ✅ | SHAP/coeffs + narrative |
| Provenance trace | ✅ | dataset_version → model |
| Model card | ✅ | Standardized template |

---

### Thresholds: Not Arbitrary

**No fixed accuracy thresholds** (e.g., "MAE < 5000"). Thresholds are:
- **Relative**: Must beat best baseline
- **Calibration**: ECE < 0.05 (industry standard)
- **Coverage**: Prediction interval coverage within 5% of nominal
- **Subgroup**: No subgroup with n≥30 has >2x overall MAE
- **Abstention**: Abstention rate reported and justified

**If baselines are weak, model must still beat them.** A model that only ties baselines adds no value.

---

### Model Card Template (Mandatory for MODEL_CANDIDATE)

```
# Model Card: <name> v<version>

## Model Details
- Model Type: <e.g., GradientBoostingRegressor>
- Target: <e.g., closing_rank>
- Training Dataset: <dataset_version>
- Training Date: <UTC ISO>
- Code Version: <git commit>
- Authors: <names>

## Intended Use
- Primary: <e.g., Predict MCC Round 1 closing ranks for 2026>
- Out of Scope: <e.g., State counselling, Round 2+, individual admission>

## Training Data
- Authorities: <list>
- Years: <list>
- Rounds: <list>
- Sample Size: <n>
- Features: <list with versions>

## Evaluation
- Temporal Split: <train years> → <val year> → <test year>
- Primary Metric: <e.g., MAE = XXXX>
- Baseline Comparison: <baseline_name> MAE=YYYY, p=ZZZZ
- Subgroup Performance: <table>
- Calibration: <ECE=XXXX, plot=path>
- Leakage Audit: PASS/FAIL <log_path>

## Limitations
- <Explicit list of known failure modes>
- <Abstention triggers>
- <Data gaps>

## Ethical Considerations
- PII: None in model
- Fairness: <subgroup analysis summary>
- Transparency: <explainability summary>

## Monitoring
- Drift Detection: <method>
- Performance Tracking: <metric + threshold>
- Retraining Trigger: <condition>

## Approval
- Reliability Review: <date> <reviewers>
- Production Ready: <date> <approver>
```

---

### Enforcement

- **CI/CD pipeline enforces stages**: Cannot deploy without model card + review approval
- **Model registry requires**: dataset_version, model_version, code_version, metrics
- **Serving infrastructure checks**: Model must be PRODUCTION_READY stage
- **Monitoring alerts**: Automatic retraining trigger on drift

---

### Current Applicability

**As of Sprint 3.6: NO MODEL EXISTS.** This document specifies the gates for FUTURE models. The gates are defined NOW so there's no ambiguity later.