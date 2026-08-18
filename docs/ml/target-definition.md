# Canonical Modelling Dataset Definition — Sprint 3.6

## Phase 3: Define the Future Canonical Modelling Dataset

This document defines the expected schema for the future canonical modelling dataset. It separates fields into four categories and documents gaps where required modelling fields do not currently exist.

**CRITICAL**: Do NOT add fields to canonical architecture merely because they would be useful for ML. If a required modelling field does not currently exist, document the gap explicitly.

---

### A. SOURCE FACTS (Directly from canonical ETL output)

These fields come directly from the canonical SeatMatrix and Allotment records produced by the existing ETL pipeline. They are verifiable, provenance-tracked, and already exist in the architecture.

| Field | Source | Type | Description | Current Availability |
|-------|--------|------|-------------|---------------------|
| `counselling_year` | SeatMatrix.effective_year / Allotment.effective_year | int | NEET UG counselling year (2025, 2026, ...) | ✅ MCC 2025 |
| `state` | SeatMatrix.state / inferred from source_id | string | State name or "ALL_INDIA" for MCC | ✅ MCC 2025 |
| `counselling_authority` | SourceContract.authority | string | "MCC / DGHS", "State CET Cell Maharashtra", etc. | ✅ MCC 2025 |
| `round` | Allotment.round_id / SeatMatrix.publication_version | string | "round_1", "round_2", "round_3", "stray_vacancy" | ✅ MCC 2025 (partial) |
| `course` | SeatMatrix.course_id / Allotment.course_id | string | "MBBS", "BDS" | ✅ MCC 2025 |
| `institute` | SeatMatrix.college_name / Allotment.college_name | string | College/institute name | ✅ MCC 2025 |
| `institute_code` | SeatMatrix.college_id / Allotment.college_id | string | MCC institute code or state code | ✅ MCC 2025 |
| `quota` | SeatMatrix.quota_id / Allotment.quota_id | string | "ai", "so", "mm", "du", "am", etc. | ✅ MCC 2025 |
| `category` | SeatMatrix.category_id / Allotment.category_id | string | "gn", "bc", "ew", "sc", "st", "gn_pwd", etc. | ✅ MCC 2025 |
| `total_seats` | SeatMatrix.total_seats | int | Sanctioned seats for this college/course/quota/category | ✅ MCC 2025 |
| `vacancy_seats` | NOT CURRENTLY IN CANONICAL | int | Vacant seats at specific round | ❌ GAP - No vacancy canonical model |
| `allotment_count` | Allotment.seat_count (per record) | int | Seats allotted in this specific allotment record | ✅ MCC 2025 |
| `opening_rank` | NOT CURRENTLY IN CANONICAL | int | Opening rank for this college/course/quota/category/round | ❌ GAP - Allotment has rank but not opening/closing |
| `closing_rank` | Allotment.rank (last allotted) | int | Closing rank for this college/course/quota/category/round | ⚠️ PARTIAL - rank is per-allotment, not aggregated |
| `score` | Allotment.score | float | NEET score corresponding to rank | ✅ MCC 2025 |

---

### B. DERIVED FEATURES (Computed at dataset construction time)

These features are computed from source facts during dataset assembly. They must be computable at PREDICTION TIME using only information available then.

| Feature | Computation | Prediction-Time Available? | Current Availability |
|---------|-------------|---------------------------|---------------------|
| `seat_availability_ratio` | total_seats / applicants (if known) | ❌ NO - applicants unknown at prediction time | N/A |
| `historical_closing_rank_median` | Median closing_rank for same college/course/quota/category over prior years | ⚠️ ONLY if prior years exist in dataset | ❌ Only 1 year (2025) |
| `historical_closing_rank_p10` | 10th percentile closing rank over prior years | ⚠️ ONLY if prior years exist | ❌ Only 1 year |
| `historical_closing_rank_p90` | 90th percentile closing rank over prior years | ⚠️ ONLY if prior years exist | ❌ Only 1 year |
| `round_number` | Ordinal: 1, 2, 3, 4 (stray) | ✅ YES - known from counselling schedule | ✅ MCC 2025 |
| `is_first_round` | round_number == 1 | ✅ YES | ✅ MCC 2025 |
| `category_quota_combo` | category + "_" + quota | ✅ YES | ✅ MCC 2025 |
| `institute_type` | SeatMatrix.institute_type (govt/private/deemed/central) | ✅ YES - from seat matrix | ✅ MCC 2025 |
| `state_quota_indicator` | quota in {"so", "mm", "du", "am"} | ✅ YES | ✅ MCC 2025 |
| `year_index` | counselling_year - min_year_in_dataset | ✅ YES | ✅ MCC 2025 |
| `seat_count_log` | log(total_seats + 1) | ✅ YES | ✅ MCC 2025 |

---

### C. TARGET VARIABLES (What we might predict)

These are candidate targets evaluated in Phase 4. Do NOT implement - only define.

| Target | Definition | Type | Required Source Data | Current Availability |
|--------|------------|------|---------------------|---------------------|
| `closing_rank` | Last rank admitted for college/course/quota/category/round | Numeric (int) | Allotments with rank | ✅ MCC 2025 (per-record, not aggregated) |
| `opening_rank` | First rank admitted for college/course/quota/category/round | Numeric (int) | Allotments with rank | ❌ GAP - not in canonical |
| `admission_probability` | P(admitted \| student_rank, college, course, quota, category, round) | Probability [0,1] | Allotments + student rank distribution | ❌ GAP - no student-level data |
| `seat_allocation` | Which college/course/quota/category a student gets | Multi-class | Allotments + student preferences | ❌ GAP - no preferences |
| `vacancy_after_round` | Seats remaining after each round | Numeric (int) | Vacancy reports | ❌ GAP - no vacancy canonical |

---

### D. PROVENANCE (Required for every modelling record)

Every record in the modelling dataset MUST carry full provenance to enable reproducibility and audit.

| Field | Source | Description |
|-------|--------|-------------|
| `source_file_id` | SourceMetadata.source_file_id | Deterministic ID from SHA-256 |
| `file_checksum` | SourceMetadata.file_checksum | SHA-256 of source file bytes |
| `source_url` | SourceMetadata.source_url | Original download URL |
| `parser_version` | SourceMetadata.parser_version | e.g., "mcc_etl_v1", "mah_etl_v1" |
| `retrieval_timestamp` | SourceMetadata.retrieval_timestamp | UTC ISO timestamp of download |
| `contract_version` | SourceMetadata.contract_version | e.g., "1.1.0", "1.0.0" |
| `adapter_version` | SourceAdapter class version | Track adapter logic changes |
| `transformation_version` | Dataset builder version | Track feature engineering changes |
| `feature_version` | Feature set version | Track derived feature changes |

---

### Documented Gaps (Fields Required for Modelling But Missing)

| Gap | Description | Impact | Resolution Path |
|-----|-------------|--------|-----------------|
| **No Vacancy Canonical Model** | Vacancy reports not ingested into canonical schema | Cannot compute seat availability trends | Add Vacancy canonical model + adapter |
| **No Opening Rank in Canonical** | Allotment has single rank, not opening/closing | Cannot compute rank range per college/round | Aggregate allotments per college/course/quota/category/round |
| **No Historical Closing Ranks** | Only 2025 MCC data exists | Cannot compute year-over-year features | Ingest 2021-2024 MCC allotments |
| **No Student Preference Data** | Student choice lists not available | Cannot model college allocation | Not feasible (PII) |
| **No Applicant Counts** | Number of applicants per category/quota not published | Cannot compute competition ratios | May use proxy (seats * factor) |
| **State Historical Data** | Zero historical data for Maharashtra, Karnataka, UP | Cannot build multi-state models | Requires archive downloads |
| **UP Mappings Unverified** | UP category/quota mappings are placeholders | UP data unusable even if downloaded | Verify mappings against real UP data |

---

### Modelling Dataset Construction Rules

1. **One row per**: college × course × quota × category × round × year
2. **Source of truth**: Aggregated from canonical SeatMatrix + Allotment records
3. **Provenance**: Each row inherits provenance from source records
4. **Temporal boundary**: Features for year Y can only use data from years < Y
5. **Missingness**: Explicit NA for unavailable features (not imputed)
6. **Versioning**: Dataset version = hash of (source_file_ids + transformation_version + feature_version)

---

### Canonical Architecture Constraint Check

**Do NOT add these to canonical models** (they belong in modelling dataset only):
- Historical aggregations (medians, percentiles over years)
- Derived competition metrics
- Prediction-time features
- Target variables

The canonical models (SeatMatrix, Allotment) remain pure source-fact representations. The modelling dataset is a SEPARATE derived artifact built on top.