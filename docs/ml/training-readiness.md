# Training Readiness Reference — Sprint 4.0

## Current Status

| Component | Status |
|-----------|--------|
| Verified modelling-ready years | 1 (MCC 2025) |
| Temporal validation | BLOCKED (need ≥3) |
| Target readiness | NO_TARGET_READY |
| Training | TRAINING_BLOCKED |
| Production model | NOT_READY |

---

## Training Block Reasons

The `TrainingGuard` refuses to execute when ANY condition fails:

| Block Reason | Current State | Resolution |
|--------------|---------------|------------|
| `TEMPORAL_VALIDATION_BLOCKED` | ✅ BLOCKED | Need ≥3 verified years |
| `INSUFFICIENT_VERIFIED_YEARS` | ✅ 1 year | Ingest MCC 2021-2024 + 1 state |
| `TARGET_NOT_READY` | ✅ NO_TARGET_READY | Validate closing_rank target |
| `LEAKAGE_CHECKS_FAILED` | Would check | Fix any leakage violations |
| `DATA_QUALITY_GATES_FAILED` | Would check | Fix quality gate failures |
| `PROVENANCE_INCOMPLETE` | Would check | Ensure full provenance |
| `NO_TARGET_DEFINED` | ✅ NO_TARGET_READY | Define valid target |

---

## Requirements to Unblock

### Minimum for Temporal Validation
- **3 verified modelling-ready years** across authorities
- Currently: MCC 2025 only (1 year)
- Need: MCC 2021-2024 + at least 1 state (Maharashtra/Karnataka/UP)

### Target Validation (closing_rank)
Per `target-definition-phase4.md`:
- [ ] MCC 2021-2024 allotments ingested and validated
- [ ] At least 1 state's historical allotments ingested
- [ ] Minimum 4 years for temporal validation (train/val/test)
- [ ] Closing rank aggregation in canonical model
- [ ] Verified UP category/quota mappings (if UP included)

### Data Quality
All 13 modelling quality gates must pass:
1. No duplicate records
2. Required fields complete
3. Valid category/quota/year/round
4. Provenance complete
5. No PII
6. No future information
7. Compatible contracts
8. Valid rank (1-900000)
9. Valid seat count (0-5000)
10. Source verified

---

## Training Guard Usage

```python
from modelling.training.guard import get_training_guard, TrainingBlockReason

guard = get_training_guard()

result = guard.check_training_allowed(
    dataset_version=dataset_version,
    leakage_result=leakage_result,
    quality_gate_result=quality_gate_result,
    target_name="closing_rank",
)

if result.allowed:
    # Training would execute (future sprint)
    pass
else:
    print(f"TRAINING BLOCKED: {result.block_reasons}")
    for reason in result.block_reasons:
        print(f"  - {reason.value}")
```

**NO "force training" option exists.**

---

## Model Lifecycle Stages

```
RESEARCH_ONLY (current)
    ↓
MODEL_CANDIDATE
    - Out-of-time evaluation on held-out year
    - Beats best baseline (p < 0.05)
    - Calibration ECE < 0.05
    - Subgroup stability
    - Leakage audit passes
    - Reproducibility verified
    - Documented limitations
    - Explainability artifacts
    - Full provenance
    - Model traceability
    ↓
RELIABILITY_REVIEW
    - Independent review (2+ engineers)
    - Leakage audit reproduced
    - Baseline comparison reproduced
    - Subgroup analysis reviewed
    - Abstention policy tested
    - Calibration plots reviewed
    - Failure modes documented
    - Monitoring plan defined
    - Rollback plan defined
    - Security review
    ↓
PRODUCTION_READY
    - Model registered
    - Serving deployed
    - Monitoring active
    - Alerting configured
    - Documentation updated
    - Rollback tested
```

**Current achievable**: `RESEARCH_ONLY` only.

---

## Target Readiness Details

| Target | Readiness | Reason |
|--------|-----------|--------|
| `closing_rank` | NO_TARGET_READY | Only MCC 2025, need ≥3 years |
| `opening_rank` | NO_TARGET_READY | Not in canonical + insufficient data |
| `admission_probability` | NO_TARGET_READY | No applicant pool (never published), PII |
| `seat_allocation` | NO_TARGET_READY | No preferences (PII), no historical data |
| `vacancy_after_round` | NO_TARGET_READY | No vacancy canonical model |

---

## Data Requirements Summary

| Requirement | Current | Needed |
|-------------|---------|--------|
| MCC historical allotments | 2025 only | 2021-2024 |
| State historical allotments | 0 | ≥1 state (2021-2025) |
| Minimum years for temporal val | 1 | ≥3 |
| Target definition | NO_TARGET_READY | Validated closing_rank |
| UP mappings | PLACEHOLDER | Verified |

---

## Verification Checklist

Before attempting training:
- [ ] `python -m pytest tests/unit/modelling/` passes
- [ ] `config/modelling_readiness.yaml` shows ≥3 verified years
- [ ] `get_target_readiness()` returns `"READY"`
- [ ] `get_temporal_validation_status()` returns `"READY"`
- [ ] `LeakageChecker.check_dataset()` returns `passed=True`
- [ ] `ModellingQualityGates.run_gates()` returns `overall_passed=True`
- [ ] `TrainingGuard.check_training_allowed()` returns `allowed=True`

---

## Expected Timeline

| Milestone | Condition |
|-----------|-----------|
| Temporal validation READY | ≥3 verified consecutive years |
| Target READY | MCC 2021-2024 + 1 state ingested, target validated |
| MODEL_CANDIDATE | Beats baseline, passes reliability gates |
| RELIABILITY_REVIEW | Independent review passed |
| PRODUCTION_READY | All gates + monitoring + rollback tested |

---

## Contact

For questions about training readiness, refer to:
- `modelling/training/guard.py` — TrainingGuard implementation
- `modelling/splits/engine.py` — TemporalSplitter logic
- `modelling/targets/engine.py` — TargetEngine readiness
- `config/modelling_readiness.yaml` — Current readiness data
- `docs/ml/target-definition-phase4.md` — Target analysis