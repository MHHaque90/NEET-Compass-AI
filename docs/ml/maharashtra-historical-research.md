# Maharashtra Historical Data Research — Sprint 3.7

## Phase 3: Maharashtra (MAHA CET Cell) Source Research

---

### Maharashtra Official Source (from config/data_sources.yaml)

| Source ID | Authority | Official URL | Verification Status |
|-----------|-----------|--------------|---------------------|
| `mcc_state_maharashtra` | State CET Cell, Maharashtra | https://cetcell.mahacet.org/ | VERIFIED (portal exists) |

**Scope**: STATE_QUOTA
**Courses**: MBBS+BDS
**Year Support (config)**: "2026 (registration announced); archive NOT VERIFIED"
**Format**: HTML

---

### Repository Evidence

| Year | Contract | Adapter | Fixture | Real Download | Tests |
|------|----------|---------|---------|---------------|-------|
| 2026 | ✅ v1.0.0 | ✅ | ✅ seat_matrix_r1_2026.csv, allotments_r1_2026.csv | ❌ NO | ✅ Unit + conformance |
| 2025 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2024 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2023 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2022 | ❌ | ❌ | ❌ | ❌ NO | ❌ |
| 2021 | ❌ | ❌ | ❌ | ❌ NO | ❌ |

**Status**: Only 2026 fixtures exist. Archive NOT VERIFIED per config.

---

### Current Maharashtra Contract (v1.0.0) — 2026 Only

**Seat Matrix Columns**: StateName, Institute, Course, Category, Quota, TotalSeats
**Allotment Columns**: Institute, Course, Category, Quota, Round, OpeningRank, ClosingRank, SeatCount

**Category Normalization**: OP→gn, GN→gn, BC→bc, EW→ew, SC→sc, ST→st, +PwD suffix
**Quota Normalization**: AI→ai, MNG→mm, SO→so

---

### Format Compatibility Assessment (Phase 5)

**Current Parser Assumption**: CSV format (stdlib-only UTF-8-sig parser)

**Unknown for Historical Years (2021-2025)**:
- Actual source format (CSV / HTML table / PDF)
- Column headers and ordering
- Category/quota codes used
- Round naming convention
- Institute naming convention

**Risk**: If historical format differs from 2026 fixture assumption, parser extension required.

**Sprint 3.7 Requirement**: Must verify actual historical format before assuming contract compatibility.

---

### Maharashtra Research Summary

| Item | Status | Evidence |
|------|--------|----------|
| Portal accessible | ✅ VERIFIED | Config confirms |
| Historical archive accessible | ❌ NOT_VERIFIED | Config: "archive NOT VERIFIED" |
| 2021-2025 documents available | ❌ NOT_VERIFIED | Zero repository evidence |
| 2026 fixtures | ✅ PARTIALLY_VERIFIED | Fixtures exist, no real download |
| Contract compatibility (historical) | UNKNOWN | No source documents examined |
| Format consistency | UNKNOWN | No historical samples |

**Conclusion**: Maharashtra has ZERO verified historical modelling data. Archive access and format must be investigated before any historical contracts can be implemented.