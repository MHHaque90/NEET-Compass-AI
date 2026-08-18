# MCC Contract Compatibility for Historical Years — Sprint 3.7

## Phase 4: Determining Contract-Compatible Historical Datasets

---

### Current MCC Contract (v1.1.0) — 2025 Implementation

**Seat Matrix Contract** (`seat_matrix_2025_contract`):
- Columns: StateName, InstituteType, Institute, Quota, Branch, Category, TotalSeats
- Supported Formats: csv, table
- Validation: Required fields, enum (quota/category), range, unique_key

**Allotment Contract** (`allotments_2025_contract`):
- Columns: Institute Code, Institute Name, Course, Quota, Category, Round, Rank, Score, Seats
- Supported Formats: csv
- Validation: Required fields, enum (quota/category), range, unique_key

---

### Format Compatibility Hypothesis

**Assumption**: MCC document format is consistent across years (2021-2025).
**Risk**: If format changed, separate contracts needed per year.

**Evidence Needed** (per year 2021-2024):
1. Actual seat matrix PDF/CSV column headers
2. Actual allotment CSV column headers
3. Category/quota codes used
4. Round naming convention

---

### Required Contract Extensions for Historical Years

If format is consistent, minimal changes needed:
- New contract functions: `seat_matrix_2024_contract()`, `allotments_2024_contract()`, etc.
- Only `effective_year` and `publication_version` differ
- Can reuse column definitions, validation rules, field mappings

If format differs:
- May need version-specific column mappings
- May need version-specific category/quota normalization

---

### Contract Compatibility Matrix

| Year | Seat Matrix Format | Allotment Format | Category Codes | Quota Codes | Round Names | Compatibility |
|------|-------------------|------------------|----------------|-------------|-------------|---------------|
| 2025 | ✅ Known | ✅ Known | ✅ Known | ✅ Known | ✅ Known | **VERIFIED** |
| 2024 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NEEDS_VERIFICATION |
| 2023 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NEEDS_VERIFICATION |
| 2022 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NEEDS_VERIFICATION |
| 2021 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NEEDS_VERIFICATION |

---

### Required Verification Steps for Each Historical Year

For each year 2021-2024:
1. **Obtain source documents** (seat matrix PDF, allotment CSV, vacancy PDF)
2. **Extract and compare** column headers with 2025 contract
3. **Extract and compare** category/quota codes
4. **Document** any differences
5. **Create** year-specific contract if needed, or extend existing

---

### Priority Order for MCC Historical Ingestion

1. **2024** — Most recent, likely same format as 2025
2. **2023** — Likely same format
3. **2022** — May have format differences
4. **2021** — Oldest, highest risk of format differences

---

### Modelling Impact

If 2021-2024 are contract-compatible:
- **4 additional verified years** for temporal validation
- **Total MCC years**: 5 (2021-2025)
- **Temporal validation**: POSSIBLE (train 2021-2023, val 2024, test 2025)
- **Baselines**: COMPUTABLE (≥2 prior years available)

If format differs significantly:
- Each year may need separate contract version
- Increases implementation effort
- May reduce usable historical coverage