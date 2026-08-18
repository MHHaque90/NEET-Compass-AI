# State Historical Data Format Compatibility — Sprint 3.7

## Phase 5: Format Compatibility Assessment for Maharashtra, Karnataka, UP

---

### Current State Contracts (All v1.0.0, 2026 Only)

| State | Seat Matrix Columns | Allotment Columns | Category Codes | Quota Codes |
|-------|---------------------|-------------------|----------------|-------------|
| Maharashtra | StateName, Institute, Course, Category, Quota, TotalSeats | Institute, Course, Category, Quota, Round, OpeningRank, ClosingRank, SeatCount | gn, bc, ew, sc, st (+_pwd) | ai, mm, so |
| Karnataka | Institute, Course, Category, Quota, TotalSeats | Institute, Course, Category, Quota, Round, OpeningRank, ClosingRank, SeatCount | gn, bc, ew, sc, st (+_pwd) | ai, so |
| Uttar Pradesh | Institute, Course, Category, Quota, TotalSeats | Institute, Course, Category, Quota, Round, OpeningRank, ClosingRank, SeatCount | gn, bc, ew, sc, st (NO _pwd) | ai, so |

---

### Format Compatibility Unknowns for Historical Years

For EACH state and EACH historical year (2021-2025), the following are UNKNOWN:

| Unknown | Maharashtra | Karnataka | Uttar Pradesh |
|---------|-------------|-----------|---------------|
| **Source format** | CSV / HTML / PDF? | CSV / HTML / PDF? | CSV / HTML / PDF? |
| **Seat matrix columns** | Same as 2026? | Same as 2026? | Same as 2026? |
| **Allotment columns** | Same as 2026? | Same as 2026? | Same as 2026? |
| **Category codes** | Same (OP/GN/BC/EW/SC/ST)? | Same (GM/SC/ST/CAT-1/2A/3B)? | Same (GM/SC/ST/BC/EW)? |
| **Quota codes** | Same (AI/MNG/SO)? | Same (AI/COMEDK/SO)? | Same (AI/SO)? |
| **Round naming** | "Round 1" etc? | "Round 1" etc? | "Round 1" etc? |
| **Institute naming** | Same convention? | Same convention? | Same convention? |
| **PwD handling** | Same suffix? | Same suffix? | MISSING in current contract! |

---

### Compatibility Risk Assessment

| State | Risk Level | Rationale |
|-------|------------|-----------|
| **Maharashtra** | MEDIUM | Large state, established counselling process, but format unverified |
| **Karnataka** | MEDIUM | KEA has consistent process, but COMEDK quota adds complexity |
| **Uttar Pradesh** | **HIGH** | Placeholder mappings, no PwD handling, format completely unverified |

---

### Parser Extension Requirements (If Format Differs)

If historical format differs from 2026 assumption:

1. **Parser extension** in state-specific `parsers.py`
   - Must remain stdlib-only (no pdfplumber/Selenium)
   - Must handle actual historical format

2. **Adapter extension** in state-specific `adapters.py`
   - Additional category/quota normalization
   - Handle different column names

3. **Contract extension** in state-specific `contracts.py`
   - Year-specific `expected_columns`
   - Updated validation rules

**Constraint**: No core architecture redesign. Extensions must be state-specific only.

---

### Verification Protocol for Each State

For each state, before implementing historical contracts:

1. **Access historical archive** (if exists)
2. **Download sample documents** for 1-2 historical years
3. **Compare** with 2026 fixture assumptions
4. **Document** exact differences
5. **Implement** minimal parser/adapter extensions
6. **Test** with historical fixtures

**If archive inaccessible**: Document `ARCHIVE_INACCESSIBLE` / `FORMAT_UNVERIFIED`

---

### Current Status

| State | 2026 Fixture Format | Historical Format | Compatibility | Action |
|-------|---------------------|-------------------|---------------|--------|
| Maharashtra | CSV (assumed) | UNKNOWN | UNKNOWN | Investigate archive |
| Karnataka | CSV (assumed) | UNKNOWN | UNKNOWN | Investigate archive |
| Uttar Pradesh | CSV (assumed) | UNKNOWN | **HIGH RISK** | Investigate archive + verify mappings |

**Conclusion**: NO state historical data can be assumed contract-compatible without format verification. Sprint 3.7 must investigate state archives before assuming compatibility.