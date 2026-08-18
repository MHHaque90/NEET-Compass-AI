# Karnataka Historical Data Research — Sprint 3.7

## Phase 3: Karnataka (KEA) Source Research

---

### Karnataka Official Source (from config/data_sources.yaml)

| Source ID | Authority | Official URL | Verification Status |
|-----------|-----------|--------------|---------------------|
| `mcc_state_karnataka` | Karnataka Examinations Authority | https://cetonline.karnataka.gov.in/kea/ | VERIFIED (portal exists) |

**Scope**: STATE_QUOTA
**Courses**: MBBS+BDS
**Year Support (config)**: "2026 (portal active); archive NOT VERIFIED"
**Format**: HTML

---

### Repository Evidence

| Year | Contract | Adapter | Fixture | Real Download | Tests |
|------|----------|---------|---------|---------------|-------|
| 2026 | ✅ v1.0.0 | ✅ | ✅ seatmatrix_ka_r1_2026.csv | ❌ NO | ✅ Unit + conformance |
| 2025 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2024 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2023 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2022 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2021 | ❌ | ❌ | ❌ | ❌ NO | ❌ |

**Status**: Only 2026 seat matrix fixture exists. Allotments contract exists but NO fixture. Archive NOT VERIFIED per config.

---

### Current Karnataka Contract (v1.0.0) — 2026 Only

**Seat Matrix Columns**: Institute, Course, Category, Quota, TotalSeats
**Allotment Columns**: Institute, Course, Category, Quota, Round, OpeningRank, ClosingRank, SeatCount

**Category Normalization**: GM→gn, SC→sc, ST→st, CAT-1→bc, 2A→bc, 3B→bc, +PwD suffix
**Quota Normalization**: AI→ai, COMEDK→so, SO→so

**Note**: Quotas only "ai" and "so" — no "mm" (management) like Maharashtra

---

### Format Compatibility Assessment (Phase 5)

**Current Parser Assumption**: CSV format (stdlib-only UTF-8-sig parser)

**Unknown for Historical Years (2021-2025)**:
- Actual source format (CSV / HTML table / PDF)
- Column headers and ordering
- Category codes used (GM/SC/ST/CAT-1/2A/3B vs alternatives)
- Quota codes used
- Round naming convention

**Risk**: If historical format differs from 2026 fixture assumption, parser extension required.

---

### Karnataka Research Summary

| Item | Status | Evidence |
|------|--------|----------|
| Portal accessible | ✅ VERIFIED | Config confirms |
| Historical archive accessible | ❌ NOT_VERIFIED | Config: "archive NOT VERIFIED" |
| 2021-2025 documents available | ❌ NOT_VERIFIED | Zero repository evidence |
| 2026 seat matrix fixture | ✅ PARTIALLY_VERIFIED | Fixture exists, no real download |
| 2026 allotments fixture | ❌ NOT_VERIFIED | Contract only, no fixture |
| Contract compatibility (historical) | UNKNOWN | No source documents examined |
| Format consistency | UNKNOWN | No historical samples |

**Conclusion**: Karnataka has ZERO verified historical modelling data. Archive access and format must be investigated before any historical contracts can be implemented.