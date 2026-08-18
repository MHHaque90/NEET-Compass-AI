# Uttar Pradesh Historical Data Research — Sprint 3.7

## Phase 3/6: Uttar Pradesh (UPMU/DME UP) Source Research + Mapping Verification

---

### Uttar Pradesh Official Sources (from config/data_sources.yaml)

| Source ID | Authority | Official URL | Verification Status |
|-----------|-----------|--------------|---------------------|
| `mcc_state_uttar_pradesh` | Directorate of Medical Education, UP | https://upneet.gov.in/ | VERIFIED (portal exists) |
| (alt) | DME UP | https://bqnmc.up.gov.in/ | VERIFIED (official UP medical counselling site) |

**Scope**: STATE_QUOTA
**Courses**: MBBS+BDS
**Year Support (config)**: "2026 (portal active); archive NOT VERIFIED"
**Format**: HTML

---

### Repository Evidence

| Year | Contract | Adapter | Fixture | Real Download | Tests |
|------|----------|---------|---------|---------------|-------|
| 2026 | ✅ v1.0.0 | ✅ | ✅ seatmatrix_up_r1_2026.csv | ❌ NO | ✅ Unit + conformance |
| 2025 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2024 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2023 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2022 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2021 | ❌ | ❌ | ❌ | ❌ NO | ❌ |

**Status**: Only 2026 seat matrix fixture exists. Archive NOT VERIFIED per config.

---

### CRITICAL: Current UP Mappings are PLACEHOLDERS (Phase 6)

**File**: `etl/contracts/sources/uttar_pradesh/mappings.py`

**Explicit Documentation in Code**:
> "MUST be verified against actual UP source data"

**Current Placeholder Category Map**:
```python
SEAT_MATRIX_CATEGORY_BASE = {
    "GM": "gn",
    "SC": "sc",
    "ST": "st",
    "BC": "bc",
    "EW": "ew",
}
# No PwD suffix handling defined
```

**Current Placeholder Quota Map**:
```python
SEAT_MATRIX_QUOTA_MAP = {
    "AI": "ai",
    "SO": "so",
}
# No "mm" (management) quota defined
```

**Validation Rules Use Only**: gn, bc, ew, sc, st (NO *_pwd categories)

---

### Mapping Verification Requirements

For UP to become modelling-ready, EACH mapping must have source evidence:

| Mapping Type | Current Placeholder | Required Evidence |
|--------------|---------------------|-------------------|
| **Category: GM** | "gn" | Official UP document showing "GM" → General |
| **Category: GN** | (not mapped) | Check if "GN" also used |
| **Category: SC** | "sc" | Official document |
| **Category: ST** | "st" | Official document |
| **Category: BC** | "bc" | Official document — check if OBC subcategorization |
| **Category: OBC** | (not mapped) | Check if separate from BC |
| **Category: EW/EWS** | "ew" | Official document |
| **Category: PwD/PH** | (not mapped) | Suffix handling (_pwd) |
| **Quota: AI** | "ai" | All India Quota |
| **Quota: SO** | "so" | State Quota / Open |
| **Quota: MNG/MM** | (not mapped) | Management quota? |
| **Quota: GOV** | (not mapped) | Government quota? |

**Without verified mappings**: UP data CANNOT be modelling-ready even if downloaded.

---

### Format Compatibility Assessment (Phase 5)

**Current Parser Assumption**: CSV format (stdlib-only UTF-8-sig parser)

**Unknown for All Years (including 2026)**:
- Actual source format (CSV / HTML table / PDF)
- Column headers and ordering
- Category codes used (GM/SC/ST/BC/EW vs GN/SC/ST/OBC/EWS)
- Quota codes used
- Round naming convention
- Institute naming convention

**Risk**: 2026 fixture may not match real UP source format at all.

---

### UP Research Summary

| Item | Status | Evidence |
|------|--------|----------|
| Portal accessible | ✅ VERIFIED | Config confirms (upneet.gov.in, bqnmc.up.gov.in) |
| Historical archive accessible | ❌ NOT_VERIFIED | Config: "archive NOT VERIFIED" |
| 2021-2025 documents available | ❌ NOT_VERIFIED | Zero repository evidence |
| 2026 fixtures | ✅ PARTIALLY_VERIFIED | Seat matrix fixture exists, no real download |
| **Category mappings** | ❌ **PLACEHOLDER** | Explicitly documented as unverified |
| **Quota mappings** | ❌ **PLACEHOLDER** | Explicitly documented as unverified |
| Contract compatibility | UNKNOWN | No source documents examined |
| Format consistency | UNKNOWN | No samples |

**Conclusion**: UP has ZERO verified historical modelling data AND mappings are explicitly placeholders. **Cannot be modelling-ready until mappings verified against real source data.**