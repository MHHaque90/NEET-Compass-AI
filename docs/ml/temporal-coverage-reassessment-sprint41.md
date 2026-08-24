# Temporal Coverage Reassessment — Sprint 4.1

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 4.1 — Historical Data Activation & Modelling-Readiness Advancement

---

## 1. Purpose

Reassess temporal validation readiness using the existing `TemporalReadinessGate` from `etl/contracts/historical/temporal_gate.py` against the current `config/modelling_readiness.yaml` registry.

---

## 2. Framework Constants

From `etl/contracts/historical/temporal_gate.py`:

```python
MINIMUM_VERIFIED_YEARS: int = 3
PREFERRED_VERIFIED_YEARS: int = 4
```

The gate requires:
- Minimum 3 verified modelling-ready years across all authorities
- Years must be chronologically ordered
- Must support forward-chaining train/validation/test split

---

## 3. Current Modelling-Ready Years (From Registry)

Using `modelling.config.modelling_readiness.get_modelling_ready_years()`:

| Authority | Verified Modelling-Ready Years |
|-----------|-------------------------------|
| MCC | [2025] |
| Maharashtra | [] |
| Karnataka | [] |
| Uttar Pradesh | [] |

**Total verified years**: 1 (2025 only)

---

## 4. Temporal Readiness Gate Result

```
=== TEMPORAL READINESS RESULT ===
Passed: False
Verified years: (2025,)
Verified count: 1
Minimum required: 3
Has gaps: False
Gap years: ()
Chronologically ordered: True
Can split train/val/test: False
Temporal validation status: BLOCKED
```

---

## 5. Analysis

### Verified Years
- Only MCC 2025 is modelling-ready (both seat_matrix R1 and allotments R3)
- Maharashtra 2026, Karnataka 2026, UP 2026 are `READY_WITH_LIMITATIONS` (fixture-only, no real data)
- All historical years (2021-2024) are `NOT_READY` with `evidence_status: NOT_VERIFIED` or `AUTOMATED_DOWNLOAD_BLOCKED`

### Chronological Continuity
- Single year (2025) — trivially ordered, no gaps possible
- Cannot assess continuity without ≥2 years

### Train/Validation/Test Split Candidates
- **Impossible** with 1 year
- Minimum required: 3 years (e.g., train: 2021-2023, validate: 2024, test: 2025)
- Preferred: 4+ years for rolling validation

### Cross-Authority Validation
- Only MCC has verified data
- Cannot stratify by authority

---

## 6. Comparison with Sprint 4.0 Baseline

| Metric | Sprint 4.0 (Certified) | Sprint 4.1 (Reassessed) | Change |
|--------|------------------------|-------------------------|--------|
| Verified modelling-ready years | 1 | 1 | No change |
| Temporal validation status | BLOCKED | BLOCKED | No change |
| Minimum years met | No (1 < 3) | No (1 < 3) | No change |
| Consecutive years | 1 | 1 | No change |

**No improvement in temporal coverage** — no new historical artifacts were verified during Sprint 4.1.

---

## 7. Requirements to Unblock Temporal Validation

To achieve `TemporalValidationStatus.READY`, the registry must contain:

**Option A: MCC Only**
- MCC 2023, 2024, 2025 all READY (3 consecutive years)

**Option B: MCC + One State**
- MCC 2024, 2025 + Maharashtra 2024 (3 years across authorities)
- Requires state historical data ingestion

**Option C: Multiple States**
- MCC 2025 + Maharashtra 2025 + Karnataka 2025 (3 authorities, same year)
- Not ideal — prefers temporal spread over cross-sectional

**Preferred**: ≥4 consecutive MCC years (2022-2025) + at least one state's historical years

---

## 8. Honest Assessment

**Temporal Validation Status: BLOCKED**

The gate correctly returns `BLOCKED` because:
- Verified count (1) < Minimum required (3)
- Cannot create forward-chaining train/validate/test split
- No chronological depth for temporal leakage detection

**This is the correct, evidence-based result.** The minimum requirement is NOT changed to unlock training. The framework honestly reports insufficient data.

---

## 9. Next Steps (Conditional)

If MCC 2021-2024 artifacts are obtained and verified:
1. Update `modelling_readiness.yaml` with new READY entries
2. Re-run `TemporalReadinessGate.validate(modelling_ready_years)`
3. If passed: temporal validation = READY
4. Proceed to target evaluation (Phase 7)

**Until then**: `TEMPORAL_VALIDATION_BLOCKED` remains the correct status.

---

*End of Temporal Coverage Reassessment — Sprint 4.1*