# Dataset Readiness Assessment — Sprint 3.6

## Phase 1: Historical Data Inventory

This document provides a rigorous, evidence-based inventory of historical data availability for each of the four counselling authorities currently implemented in the NEET Compass AI ETL architecture.

**Principle**: Never assume a year exists without repository evidence. Statuses are assigned strictly based on what exists in the repository (code, fixtures, data directories, documentation).

### Status Definitions

| Status | Meaning |
|--------|---------|
| **VERIFIED** | Year/dataset exists in repository with provenance (fixtures, raw data, or documented evidence) |
| **PARTIALLY_VERIFIED** | Some evidence exists but incomplete (e.g., only seat matrix, no allotments) |
| **NOT_VERIFIED** | Source documented in config but no repository evidence for this year/dataset |
| **UNAVAILABLE** | Source explicitly does not have this dataset/year |
| **NOT_APPLICABLE** | Dataset type not relevant for this authority |

---

### 1. MCC (Medical Counselling Committee) — All India Quota

**Source IDs**: `mcc_official_base`, `mcc_ug_counselling`, `mcc_ug_archive`, `mcc_ug_participating_institutes`
**Authority**: Medical Counselling Committee / DGHS
**Scope**: ALL_INDIA (AIQ)
**Courses**: MBBS+BDS+NURSING
**Contract Version**: 1.1.0

| Year | Round | Course | Quota | Category | Dataset Type | Source URL | Verification Status | Format | Evidence | Modelling Suitability | Limitations |
|------|-------|--------|-------|----------|--------------|------------|---------------------|--------|----------|----------------------|-------------|
| 2025 | Round 1 | MBBS+BDS | AIQ | All | Seat Matrix | mcc.nic.in/archive-ug/ | VERIFIED | PDF/CSV | Contract exists (seat_matrix_2025_contract) | HIGH - full contract, validation rules, adapters | Only Round 1 contract defined |
| 2025 | Round 3 | MBBS+BDS | AIQ | All | Allotments | mcc.nic.in/archive-ug/ | VERIFIED | CSV | Contract exists (allotments_2025_contract) | HIGH - full contract, validation rules, adapters | PII blocklist enforced |
| 2021-2025 | All | MBBS+BDS | AIQ | All | Information Bulletins | mcc.nic.in/archive-ug/ | PARTIALLY_VERIFIED | PDF | Documented in data_sources.yaml | N/A - reference only | Not machine-readable |
| 2021-2025 | All | MBBS+BDS | AIQ | All | Vacancy Reports | mcc.nic.in/archive-ug/ | PARTIALLY_VERIFIED | PDF | Documented in data_sources.yaml | MEDIUM - if parsed | PDF only, not machine-readable |
| 2021 | All | MBBS+BDS | AIQ | All | Joined/Admitted Lists | mcc.nic.in/archive-ug/ | VERIFIED | PDF | Documented in data_sources.yaml | LOW - PII concerns | Candidate PII, not ingestible |
| 2024 | All | MBBS+BDS | AIQ | All | Joined/Admitted Lists | mcc.nic.in/archive-ug/ | VERIFIED | PDF | Documented in data_sources.yaml | LOW - PII concerns | Candidate PII, not ingestible |
| 2025 | All | MBBS+BDS | AIQ | All | Joined/Admitted Lists | mcc.nic.in/archive-ug/ | VERIFIED | PDF | Documented in data_sources.yaml | LOW - PII concerns | Candidate PII, not ingestible |
| 2022, 2023 | All | MBBS+BDS | AIQ | All | Joined/Admitted Lists | mcc.nic.in/archive-ug/ | UNAVAILABLE | - | Documented as NOT FOUND in data_sources.yaml | N/A | Not published |
| 2025 | N/A | MBBS+BDS | AIQ | All | Participating Institutes | mcc.nic.in/ug-medical-counselling/ | VERIFIED | HTML/PDF | Documented in data_sources.yaml | MEDIUM - reference data | 2026 also available live |
| 2026 | N/A | MBBS+BDS | AIQ | All | Participating Institutes | mcc.nic.in/ug-medical-counselling/ | VERIFIED | HTML | data/raw/evidence/2026-08-12/mcc_live_evidence.json | MEDIUM - reference data | Live only |

**MCC Summary**:
- **Contract-ready years**: 2025 only (seat matrix + allotments)
- **Repository evidence**: Contracts, adapters, validation rules, tests exist for 2025
- **Historical gap**: 2021-2024 have documented availability in config but NO repository fixtures, raw data, or contracts
- **2026**: Only live evidence (HTTP 200), no downloadable fixtures due to 403 bot protection

---

### 2. Maharashtra (MAHA CET Cell) — State Quota

**Source ID**: `mcc_state_maharashtra`
**Authority**: State Common Entrance Test Cell, Maharashtra
**Scope**: STATE_QUOTA
**Courses**: MBBS+BDS
**Contract Version**: 1.0.0

| Year | Round | Course | Quota | Category | Dataset Type | Source URL | Verification Status | Format | Evidence | Modelling Suitability | Limitations |
|------|-------|--------|-------|----------|--------------|------------|---------------------|--------|----------|----------------------|-------------|
| 2026 | Round 1 | MBBS+BDS | State | All | Seat Matrix | cetcell.mahacet.org | NOT_VERIFIED | CSV/HTML | Fixture exists (seat_matrix_r1_2026.csv) | MEDIUM - contract + adapter exist | Fixture only, no actual source download |
| 2026 | Round 1 | MBBS+BDS | State | All | Allotments | cetcell.mahacet.org | NOT_VERIFIED | CSV/HTML | Fixture exists (allotments_r1_2026.csv) | MEDIUM - contract + adapter exist | Fixture only, no actual source download |
| 2021-2025 | Any | Any | Any | Any | Any | cetcell.mahacet.org | UNAVAILABLE | - | No repository evidence | N/A | Archive NOT VERIFIED per data_sources.yaml |

**Maharashtra Summary**:
- **Contract-ready years**: 2026 only (fixtures only, no real source data)
- **Repository evidence**: Contracts, adapters, test fixtures for 2026 Round 1
- **Historical gap**: 2021-2025 completely unavailable in repository; archive NOT VERIFIED in config
- **Real data**: Zero verified downloads from actual Maharashtra portal

---

### 3. Karnataka (KEA) — State Quota

**Source ID**: `mcc_state_karnataka`
**Authority**: Karnataka Examinations Authority
**Scope**: STATE_QUOTA
**Courses**: MBBS+BDS
**Contract Version**: 1.0.0

| Year | Round | Course | Quota | Category | Dataset Type | Source URL | Verification Status | Format | Evidence | Modelling Suitability | Limitations |
|------|-------|--------|-------|----------|--------------|------------|---------------------|--------|----------|----------------------|-------------|
| 2026 | Round 1 | MBBS+BDS | State | All | Seat Matrix | cetonline.karnataka.gov.in/kea/ | NOT_VERIFIED | CSV/HTML | Fixture exists (seatmatrix_ka_r1_2026.csv) | MEDIUM - contract + adapter exist | Fixture only, no actual source download |
| 2026 | Round 1 | MBBS+BDS | State | All | Allotments | cetonline.karnataka.gov.in/kea/ | NOT_VERIFIED | CSV/HTML | Contract + adapter exist (no fixture) | MEDIUM - contract + adapter exist | No fixture, no actual source download |
| 2021-2025 | Any | Any | Any | Any | Any | cetonline.karnataka.gov.in/kea/ | UNAVAILABLE | - | No repository evidence | N/A | Archive NOT VERIFIED per data_sources.yaml |

**Karnataka Summary**:
- **Contract-ready years**: 2026 only (seat matrix fixture only, allotments no fixture)
- **Repository evidence**: Contracts, adapters, one seat matrix fixture for 2026
- **Historical gap**: 2021-2025 completely unavailable; archive NOT VERIFIED in config
- **Real data**: Zero verified downloads from actual KEA portal

---

### 4. Uttar Pradesh (UPMU/DME UP) — State Quota

**Source ID**: `mcc_state_uttar_pradesh`
**Authority**: Directorate of Medical Education, Uttar Pradesh
**Scope**: STATE_QUOTA
**Courses**: MBBS+BDS
**Contract Version**: 1.0.0 (PLACEHOLDER - mappings must be verified)

| Year | Round | Course | Quota | Category | Dataset Type | Source URL | Verification Status | Format | Evidence | Modelling Suitability | Limitations |
|------|-------|--------|-------|----------|--------------|------------|---------------------|--------|----------|----------------------|-------------|
| 2026 | Round 1 | MBBS+BDS | State | All | Seat Matrix | upneet.gov.in | NOT_VERIFIED | CSV/HTML | Fixture exists (seatmatrix_up_r1_2026.csv) | LOW - placeholder mappings | Fixture only, mappings NOT VERIFIED against real data |
| 2026 | Round 1 | MBBS+BDS | State | All | Allotments | upneet.gov.in | NOT_VERIFIED | CSV/HTML | Contract + adapter exist (no fixture) | LOW - placeholder mappings | No fixture, mappings NOT VERIFIED |
| 2021-2025 | Any | Any | Any | Any | Any | upneet.gov.in | UNAVAILABLE | - | No repository evidence | N/A | Archive NOT VERIFIED per data_sources.yaml |

**Uttar Pradesh Summary**:
- **Contract-ready years**: 2026 only (placeholder mappings, one seat matrix fixture)
- **Repository evidence**: Contracts, adapters, one seat matrix fixture for 2026
- **CRITICAL LIMITATION**: Mappings explicitly documented as "MUST be verified against actual UP source data"
- **Historical gap**: 2021-2025 completely unavailable; archive NOT VERIFIED in config
- **Real data**: Zero verified downloads from actual UP portal

---

### Cross-Source Historical Coverage Matrix

| Authority | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----------|------|------|------|------|------|------|
| **MCC (AIQ)** | PARTIALLY_VERIFIED* | PARTIALLY_VERIFIED* | PARTIALLY_VERIFIED* | PARTIALLY_VERIFIED* | VERIFIED (seat + allotment) | LIVE EVIDENCE ONLY |
| **Maharashtra** | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | NOT_VERIFIED (fixtures only) |
| **Karnataka** | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | NOT_VERIFIED (1 fixture) |
| **Uttar Pradesh** | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | NOT_VERIFIED (placeholder) |

* MCC 2021-2025: Documented in config as "verified available" but NO repository evidence (fixtures, raw data, contracts). Only config documentation exists.

---

### Key Findings

1. **Only MCC 2025 has full contract + adapter + test coverage in the repository**
2. **All three states (Maharashtra, Karnataka, UP) only have 2026 test fixtures - NO historical data**
3. **No state has verified historical archive downloads (2021-2025)**
4. **UP mappings are explicitly placeholder/unverified**
5. **2026 live data for MCC exists but automated downloads blocked (HTTP 403)**
6. **The "verified" status in config/data_sources.yaml refers to SOURCE VERIFICATION (portal exists), not DATA VERIFICATION (historical files downloaded and ingested)**

---

### Modelling Readiness Conclusion (Phase 1 Output)

**VERIFIED repository evidence for modelling exists ONLY for**:
- MCC 2025: Seat Matrix (Round 1) + Allotments (Round 3)

**ALL OTHER year/authority combinations have NO repository evidence suitable for modelling**.

This is the evidence-based reality. The config documents source *availability*, not data *ingestion*.