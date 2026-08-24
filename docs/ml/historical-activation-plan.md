# Historical Data Activation Plan — Sprint 4.1

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 4.1 — Historical Data Activation & Modelling-Readiness Advancement

---

## 1. Purpose

This document provides an evidence-first plan to activate the modelling foundation built in Sprint 4.0 by promoting legitimate historical artifacts through the existing verification pipeline. It answers the required questions from the sprint mandate.

---

## 2. Currently Verified Historical Years

Based on `config/modelling_readiness.yaml` (Sprint 3.9 / 4.0 registry) and repository evidence (contracts, adapters, validators, provenance, fixtures, tests):

| Authority | Dataset | Year | Round | Readiness | Evidence |
|-----------|---------|------|-------|-----------|----------|
| MCC | seat_matrix | 2025 | Round 1 | **READY** | Contract v1.1.0, adapter, validator, provenance, 15/15 quality gates |
| MCC | allotments | 2025 | Round 3 | **READY** | Contract v1.1.0, adapter, validator, provenance, 15/15 quality gates |

**Total modelling-ready years**: **1** (MCC 2025 only, two datasets)

All other authority/year combinations in the registry are `NOT_READY` with lifecycle stage `DISCOVERED` and evidence status `NOT_VERIFIED` or `AUTOMATED_DOWNLOAD_BLOCKED`.

---

## 3. Potentially Obtainable Years

Based on `config/data_sources.yaml` and historical research docs, the following years are documented as existing on official portals but have **zero repository evidence**:

| Authority | Years | Dataset Types | Portal Status | Retrieval Status |
|-----------|-------|---------------|---------------|------------------|
| MCC | 2021, 2022, 2023, 2024 | seat_matrix, allotments, vacancy, bulletin | Archive page HTTP 200 | **AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403)** |
| Maharashtra | 2021-2025 | seat_matrix, allotments | Archive NOT VERIFIED | NOT_VERIFIED |
| Karnataka | 2021-2025 | seat_matrix, allotments | Archive NOT VERIFIED | NOT_VERIFIED |
| Uttar Pradesh | 2021-2025 | seat_matrix, allotments | Archive NOT VERIFIED | NOT_VERIFIED (mappings are PLACEHOLDERS) |

**Critical**: MCC 2021-2024 are the highest priority because:
- MCC 2025 is already verified and contract v1.1.0 exists
- Archive page verified with documents listed
- Format compatibility is UNKNOWN without examining actual source documents

---

## 4. Sources with Access Limitations

| Source | Limitation | Evidence |
|--------|------------|----------|
| MCC Archive (`https://mcc.nic.in/archive-ug/`) | **HTTP 403 on automated downloads** (bot protection) | Sprint 3.1A live verification (2026-08-12) captured in `data/raw/evidence/2026-08-12/mcc_live_evidence.json` |
| Maharashtra (`https://cetcell.mahacet.org/`) | Archive access NOT VERIFIED | `data_sources.yaml`: "archive NOT VERIFIED" |
| Karnataka (`https://cetonline.karnataka.gov.in/kea/`) | Archive access NOT VERIFIED | `data_sources.yaml`: "archive NOT VERIFIED" |
| Uttar Pradesh (`https://upneet.gov.in/`) | Archive access NOT VERIFIED; category/quota mappings are PLACEHOLDERS | `data_sources.yaml`: "archive NOT VERIFIED"; `modelling_readiness.yaml`: "Category/quota mappings explicitly PLACEHOLDER" |

**No access-control bypass is permitted**. The acquisition guide (Sprint 3.9) explicitly prohibits Selenium, CAPTCHA solving, proxy rotation, header spoofing, or any circumvention.

---

## 5. Artifacts Needed for Each Year

For each historical year to become modelling-ready, the following artifacts must be obtained and verified:

### MCC (Priority 1)
- Seat Matrix (Round 1) — PDF or CSV
- Allotment Results (Round 3) — CSV or PDF
- Retrieval: Manual browser download (automated blocked)
- Required per year: 2 artifacts minimum

### Maharashtra (Priority 2)
- Seat Matrix (Round 1) — format UNKNOWN
- Allotment Results (Round 1) — format UNKNOWN
- Contract v1.0.0 exists for 2026 fixture; historical format unconfirmed

### Karnataka (Priority 3)
- Seat Matrix (Round 1) — format UNKNOWN
- Allotment Results (Round 1) — format UNKNOWN
- Contract v1.0.0 exists for 2026 fixture; historical format unconfirmed

### Uttar Pradesh (Priority 4)
- Seat Matrix (Round 1) — format UNKNOWN
- Allotment Results (Round 1) — format UNKNOWN
- **Critical blocker**: Category/quota mappings are PLACEHOLDERS — must be verified against real UP source data before any UP dataset can reach READY

---

## 6. Evidence Required Before a Year Can Become READY

Per `docs/ml/historical-evidence-lifecycle.md` and `docs/ml/historical-acquisition-guide.md`, a year progresses through these **mandatory stages with evidence at each transition**:

```
DISCOVERED
  ↓ (source verified: URL returns HTTP 200)
SOURCE_VERIFIED
  ↓ (artifact manually downloaded via browser)
RETRIEVED
  ↓ (SHA-256 computed and recorded)
HASHED
  ↓ (column headers/schema documented)
FORMAT_INSPECTED
  ↓ (PII blocklist applied — CLEAR)
PII_SCREENED
  ↓ (contract compatibility classified: COMPATIBLE or COMPATIBLE_WITH_LIMITATIONS)
CONTRACT_CHECKED
  ↓ (parsed through adapter, canonical records produced)
PARSED
  ↓ (all 15 Sprint 3.6 quality gates executed)
VALIDATED
  ↓ (all 10 provenance fields present)
PROVENANCE_COMPLETE
  ↓ (re-ingestion produces identical results)
IDEMPOTENCY_VERIFIED
  ↓ (temporal readiness: ≥3 verified years total)
QUALITY_GATES_PASSED
  ↓
MODELLING_READY
```

**Blocking states** (require manual resolution, cannot skip):
- `BLOCKED_AUTOMATED_DOWNLOAD` — HTTP 403, manual retrieval required
- `BLOCKED_FORMAT_INCOMPATIBLE` — new contract version needed
- `BLOCKED_PII_DETECTED` — cannot enter modelling boundary
- `BLOCKED_CONTRACT_INCOMPATIBLE` — explicit adapter/contract decision needed
- `BLOCKED_PROVENANCE_INCOMPLETE` — missing required fields
- `BLOCKED_QUALITY_GATES_FAILED` — fix data quality issues

**Promotion rules** (from `etl/contracts/historical/promotion.py`):
- `NOT_VERIFIED → VERIFIED → VALIDATED → READY_WITH_LIMITATIONS → READY`
- **Forbidden**: `NOT_VERIFIED → READY` (direct jump)
- **Forbidden**: `READY_WITH_LIMITATIONS → READY` (silent upgrade without resolving limitations)

---

## 7. Minimum Coverage Required for Temporal Validation

Per `modelling/splits/engine.py` and `etl/contracts/historical/temporal_gate.py`:

- **Minimum verified years**: 3 (constant `MINIMUM_VERIFIED_YEARS = 3`)
- **Preferred verified years**: 4 (constant `PREFERRED_VERIFIED_YEARS = 4`)
- Years must be chronologically ordered
- Must support forward-chaining train/validate/test split:
  - Train: oldest years
  - Validate: middle year
  - Test: newest year (held out)

**Current state**: 1 verified year (MCC 2025) → **TEMPORAL_VALIDATION_BLOCKED**

To unblock: Need **at least 2 more verified modelling-ready years** (from MCC 2021-2024 and/or state data), making 3+ total.

---

## 8. What Prevents Training Today

Per `modelling/training/guard.py` — the TrainingGuard refuses when ANY of these checks fail:

| Check | Current Status | Block Reason |
|-------|----------------|--------------|
| Temporal validation | 1 verified year (< 3) | `TEMPORAL_VALIDATION_BLOCKED` |
| Insufficient verified years | Total = 1 | `INSUFFICIENT_VERIFIED_YEARS` |
| Target readiness | `NO_TARGET_READY` | `TARGET_NOT_READY` |
| Leakage checks | N/A (no data) | N/A |
| Data quality gates | N/A (no data) | N/A |
| Provenance completeness | N/A (no data) | N/A |
| No target defined | `NO_TARGET_READY` | `NO_TARGET_DEFINED` |

**Training is correctly blocked** — `TRAINING_BLOCKED` is the expected and honest state.

---

## 9. Exact Evidence That Would Unblock Training

To reach `TRAINING_ALLOWED`, ALL of the following must be satisfied with **actual repository evidence**:

1. **Minimum 3 verified modelling-ready years** across any authorities (chronologically ordered)
   - Example: MCC 2023, 2024, 2025 (all READY with full contract/adapter/provenance)
   
2. **At least one target with `READY` status**
   - Per `target-definition-phase4.md`: Requires MCC 2021-2024 allotments ingested + at least one state's historical allotments + minimum 4 years for temporal validation
   - Most viable candidate: `closing_rank` (labels computable from allotment records)
   
3. **Leakage checks pass** — no future information in features
   
4. **All 15 data quality gates pass** for the combined dataset
   
5. **Provenance complete** — all 10 fields for every source file
   
6. **Target explicitly defined** — not `NO_TARGET_READY`

**No single artifact unblocks training.** It requires a coherent body of verified historical evidence meeting all gates simultaneously.

---

## 10. Activation Sequence (Evidence-First)

### Phase A: MCC 2024 (Single Year, Manual)
1. Human obtains MCC 2024 Round 1 Seat Matrix PDF + Round 3 Allotment CSV from `https://mcc.nic.in/archive-ug/`
2. Records SHA-256, retrieval timestamp, exact URLs, method = "MANUAL_BROWSER"
3. Runs PII screening on column headers
4. Compares format to MCC 2025 contract v1.1.0 → classify COMPATIBLE / COMPATIBLE_WITH_LIMITATIONS / INCOMPATIBLE / UNKNOWN
5. If COMPATIBLE: parse through existing adapters, run 15 quality gates, complete provenance
6. If COMPATIBLE_WITH_LIMITATIONS: document limitations, promote to READY_WITH_LIMITATIONS
7. If INCOMPATIBLE: document exact differences, decide on new contract version (explicit)
8. Update `modelling_readiness.yaml` with evidence-based status

### Phase B: MCC 2023, 2022, 2021 (Repeat)
Same workflow. Each year independently verified.

### Phase C: State Historical Data (If Obtained)
Same workflow, but:
- Contract compatibility against v1.0.0 (fixture-based, may differ from real historical format)
- UP requires verified category/quota mappings (currently PLACEHOLDERS)

### Phase D: Temporal Validation Check
Once ≥3 verified years exist:
- Run `TemporalReadinessGate.validate(modelling_ready_years)`
- If passes: temporal validation = READY
- Else: remains BLOCKED

### Phase E: Target Investigation
Only if temporal validation READY:
- Re-evaluate target-definition-phase4.md candidates against actual available fields
- If evidence supports: update target to READY with documented label generation rule
- Else: remain NO_TARGET_READY

---

## 11. Honest Assessment

**If no additional artifacts can be obtained** (MCC 403 persists, state archives inaccessible, UP mappings unverifiable):
- MCC 2025 remains the **only** modelling-ready year
- Temporal validation remains **BLOCKED**
- Target remains **NO_TARGET_READY**
- Training remains **TRAINING_BLOCKED**
- Production model remains **NOT_READY**

**This is an acceptable Sprint 4.1 outcome.** The sprint succeeds by documenting the truth reliably, not by manufacturing progress.

---

## 12. No Claims Without Evidence

This plan makes **no claims** that:
- MCC 2021-2024 artifacts exist in the repository (they do not)
- Maharashtra/Karnataka/UP historical archives are accessible (NOT VERIFIED)
- UP category/quota mappings are verified (explicitly PLACEHOLDERS)
- Format compatibility is confirmed for any historical year (UNKNOWN)
- Any target can be computed (insufficient coverage)

Every status change in `modelling_readiness.yaml` **must** have traceable repository evidence (manifest, checksum, PII result, contract result, quality gate results, provenance).

---

*End of Historical Activation Plan*