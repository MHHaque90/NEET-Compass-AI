# Modelling Coverage Reassessment — Sprint 3.7

## Phase 10: Post-Audit Modelling Coverage Analysis

---

### Sprint 3.6 Baseline (Before Sprint 3.7)

| Metric | Value |
|--------|-------|
| Verified modelling-ready datasets | 2 (MCC 2025 seat_matrix + allotments) |
| Verified years (MCC) | 1 (2025) |
| Verified years (Maharashtra) | 0 |
| Verified years (Karnataka) | 0 |
| Verified years (UP) | 0 |
| **Total verified years across all sources** | **1** |
| Temporal validation possible | ❌ NO (need ≥4) |
| Baselines computable | ❌ NO (need ≥2 prior years) |
| **Target readiness** | **NO TARGET READY** |

---

### Sprint 3.7 Target (After Historical Audit)

**Goal**: Convert config-claimed availability into repository-verified evidence.

**Minimum for temporal validation**: 4 verified years per source (train 3, validate 1, test 1)
**Preferred**: 5+ verified years

---

### Coverage Scenarios Post-Sprint 3.7

#### Scenario A: MCC 2021-2024 Successfully Verified (Best Case)

| Source | Verified Years | Total |
|--------|----------------|-------|
| MCC | 2021, 2022, 2023, 2024, 2025 | **5** |
| Maharashtra | 0 | 0 |
| Karnataka | 0 | 0 |
| UP | 0 | 0 |
| **Total** | | **5** |

**Result**: 
- Temporal validation: ✅ POSSIBLE (MCC only)
- Baselines: ✅ COMPUTABLE (MCC)
- First target (closing_rank): ✅ SUPPORTED (MCC)
- **But**: Single-source only — no cross-state validation

#### Scenario B: MCC 2021-2024 + One State Verified (Good Case)

| Source | Verified Years | Total |
|--------|----------------|-------|
| MCC | 5 | 5 |
| Maharashtra | 2022, 2023, 2024, 2025 | 4 |
| Karnataka | 0 | 0 |
| UP | 0 | 0 |
| **Total** | | **9** |

**Result**:
- Temporal validation: ✅ POSSIBLE (multi-source)
- Cross-state validation: ✅ POSSIBLE
- Target readiness: ✅ SUPPORTED

#### Scenario C: Only MCC 2024 Verified (Minimal Progress)

| Source | Verified Years | Total |
|--------|----------------|-------|
| MCC | 2024, 2025 | 2 |
| Maharashtra | 0 | 0 |
| Karnataka | 0 | 0 |
| UP | 0 | 0 |
| **Total** | | **2** |

**Result**: 
- Temporal validation: ❌ STILL IMPOSSIBLE (need ≥4)
- Baselines: ⚠️ PARTIAL (only 1 prior year for 2025)
- Target readiness: ❌ NO TARGET READY

#### Scenario D: No New Verification (Status Quo)

| Source | Verified Years | Total |
|--------|----------------|-------|
| MCC | 2025 | 1 |
| **Total** | | **1** |

**Result**: Same as Sprint 3.6 — NO TARGET READY

---

### Minimum Viable Coverage for First Target

Per Sprint 3.6 `temporal-validation.md`:

> "Minimum 3 years needed (train/validate/test), preferably 5+"

**For closing_rank forecasting (first target candidate)**:
- Need: ≥4 verified years with seat_matrix + allotments
- Need: ≥2 authorities for cross-validation (preferred)
- Need: Verified UP mappings (if UP included)

**Current gap**: 3-4 more verified years needed minimum.

---

### Reassessment Decision Matrix

| Verified Years Added | Temporal Validation | Baselines | First Target | Recommendation |
|---------------------|---------------------|-----------|--------------|----------------|
| 0 (status quo) | ❌ | ❌ | ❌ | Continue Sprint 3.7 |
| 1-2 (MCC only) | ❌ | ⚠️ | ❌ | Continue Sprint 3.7 |
| 3-4 (MCC only) | ✅ | ✅ | ✅ (MCC only) | Proceed to Sprint 3.8 for MCC-only model |
| 4+ multi-source | ✅ | ✅ | ✅ | Proceed to Sprint 3.8 |

---

### Sprint 3.7 Success Condition

> "We now have objectively verified historical data sufficient to satisfy, or clearly demonstrate the remaining gap against, the Sprint 3.6 modelling readiness requirements."

**If ≥3 MCC historical years verified**: Document readiness for MCC-only temporal validation.
**If <3 MCC historical years verified**: Document exact remaining gap (e.g., "2 more MCC years needed").

**Never lower the standard** to declare success.