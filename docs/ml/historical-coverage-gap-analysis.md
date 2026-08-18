# Historical Coverage Gap Analysis — Sprint 3.7

## Phase 2: Gap Matrix for MCC, Maharashtra, Karnataka, Uttar Pradesh

This document provides an exact, evidence-based gap analysis for each source/year combination. Statuses are assigned ONLY based on repository evidence (contracts, fixtures, raw data, documentation) — NOT on config claims.

---

### Status Definitions

| Status | Meaning |
|--------|---------|
| **VERIFIED** | Actual source artifact exists in repository with full contract/adapter/provenance coverage |
| **PARTIALLY_VERIFIED** | Some evidence exists (e.g., contract exists but no fixture, or fixture exists but no real download) |
| **NOT_VERIFIED** | Source documented in config but NO repository evidence for this year/dataset |
| **UNAVAILABLE** | Source explicitly does not have this dataset/year |

---

## 1. MCC (Medical Counselling Committee) — All India Quota

**Source IDs**: `mcc_ug_archive`, `mcc_ug_counselling`
**Contract Version**: 1.1.0 (implemented for 2025 only)
**Current Repository Evidence**: 2025 only (seat_matrix R1 + allotments R3)

| Year | Round | Seat Matrix | Allotments | Vacancy | Info Bulletin | Joined Lists | Institutes | Modelling Ready |
|------|-------|-------------|------------|---------|---------------|--------------|------------|-----------------|
| 2026 | R1 | PARTIALLY_VERIFIED* | NOT_VERIFIED | NOT_VERIFIED | PARTIALLY_VERIFIED* | NOT_VERIFIED | VERIFIED | NO |
| 2025 | R1 | **VERIFIED** | NOT_VERIFIED | PARTIALLY_VERIFIED* | PARTIALLY_VERIFIED* | VERIFIED | VERIFIED | **YES (seat)** |
| 2025 | R3 | NOT_VERIFIED | **VERIFIED** | PARTIALLY_VERIFIED* | PARTIALLY_VERIFIED* | VERIFIED | VERIFIED | **YES (allot)** |
| 2024 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | VERIFIED | NOT_VERIFIED | NO |
| 2023 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2022 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2021 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | VERIFIED | NOT_VERIFIED | NO |

* = Documented in config/data_sources.yaml as "available" but NO repository evidence (no contracts, no fixtures, no raw data, no tests)

**Key Finding**: Only 2025 has VERIFIED contract-ready data. 2021-2024 are NOT_VERIFIED in the repository despite config claims.

---

## 2. Maharashtra (MAHA CET Cell) — State Quota

**Source ID**: `mcc_state_maharashtra`
**Contract Version**: 1.0.0 (implemented for 2026 only)
**Current Repository Evidence**: 2026 fixtures ONLY (no real downloads)

| Year | Round | Seat Matrix | Allotments | Vacancy | Info Bulletin | Joined Lists | Institutes | Modelling Ready |
|------|-------|-------------|------------|---------|---------------|--------------|------------|-----------------|
| 2026 | R1 | PARTIALLY_VERIFIED (fixture only) | PARTIALLY_VERIFIED (fixture only) | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | READY_WITH_LIMITATIONS |
| 2025 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2024 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2023 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2022 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2021 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |

**Key Finding**: Zero historical data in repository. Archive NOT VERIFIED per data_sources.yaml. Only 2026 test fixtures exist.

---

## 3. Karnataka (KEA) — State Quota

**Source ID**: `mcc_state_karnataka`
**Contract Version**: 1.0.0 (implemented for 2026 only)
**Current Repository Evidence**: 2026 seat matrix fixture ONLY

| Year | Round | Seat Matrix | Allotments | Vacancy | Info Bulletin | Joined Lists | Institutes | Modelling Ready |
|------|-------|-------------|------------|---------|---------------|--------------|------------|-----------------|
| 2026 | R1 | PARTIALLY_VERIFIED (fixture only) | PARTIALLY_VERIFIED (contract only, no fixture) | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | READY_WITH_LIMITATIONS |
| 2025 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2024 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2023 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2022 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2021 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |

**Key Finding**: Zero historical data. Archive NOT VERIFIED per data_sources.yaml. Only one 2026 fixture exists.

---

## 4. Uttar Pradesh (UPMU/DME UP) — State Quota

**Source ID**: `mcc_state_uttar_pradesh`
**Contract Version**: 1.0.0 (implemented for 2026 only) — **PLACEHOLDER MAPPINGS**
**Current Repository Evidence**: 2026 seat matrix fixture ONLY

| Year | Round | Seat Matrix | Allotments | Vacancy | Info Bulletin | Joined Lists | Institutes | Modelling Ready |
|------|-------|-------------|------------|---------|---------------|--------------|------------|-----------------|
| 2026 | R1 | PARTIALLY_VERIFIED (fixture only, PLACEHOLDER mappings) | PARTIALLY_VERIFIED (contract only, PLACEHOLDER mappings) | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | **NOT_READY** |
| 2025 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2024 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2023 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2022 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |
| 2021 | All | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NO |

**Critical Finding**: UP mappings are explicitly PLACEHOLDERS ("MUST be verified against actual UP source data"). Even with data, NOT_READY until mappings verified.

---

## Cross-Source Summary Matrix

| Authority | Verified Years (Modelling Ready) | Partially Verified Years | Unverified Years (Config Claims) | Total Years Needed (≥4) |
|-----------|----------------------------------|--------------------------|----------------------------------|-------------------------|
| **MCC** | **1** (2025) | 1 (2026 live only) | 4 (2021-2024) | **3 MORE NEEDED** |
| **Maharashtra** | 0 | 1 (2026 fixture) | 5 (2021-2025) | **4 NEEDED** |
| **Karnataka** | 0 | 1 (2026 fixture) | 5 (2021-2025) | **4 NEEDED** |
| **Uttar Pradesh** | 0 | 1 (2026 fixture, placeholder) | 5 (2021-2025) | **4 NEEDED + Mappings** |

---

## Modelling Readiness by Dataset Type

| Dataset Type | MCC | Maharashtra | Karnataka | Uttar Pradesh |
|--------------|-----|-------------|-----------|---------------|
| **Seat Matrix (R1)** | **READY (2025)** | READY_WITH_LIMITATIONS (2026) | READY_WITH_LIMITATIONS (2026) | NOT_READY (placeholder) |
| **Allotments** | **READY (2025 R3)** | READY_WITH_LIMITATIONS (2026) | READY_WITH_LIMITATIONS (2026) | NOT_READY (placeholder) |
| **Vacancy** | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED |
| **Joined Lists** | PII EXCLUDED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED |
| **Institutes** | VERIFIED (2025, 2026) | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED |

---

## Evidence Location Summary

| Source | Evidence Location | Status |
|--------|------------------|--------|
| MCC 2025 Seat Matrix | `etl/contracts/sources/mcc/contracts.py` (seat_matrix_2025_contract) | VERIFIED |
| MCC 2025 Allotments | `etl/contracts/sources/mcc/contracts.py` (allotments_2025_contract) | VERIFIED |
| MCC 2021-2024 | Config only (`config/data_sources.yaml`) | NOT_VERIFIED (no repo evidence) |
| Maharashtra 2026 | Fixtures: `etl/contracts/sources/maharashtra/fixtures/` | PARTIALLY_VERIFIED |
| Karnataka 2026 | Fixture: `etl/contracts/sources/karnataka/fixtures/` | PARTIALLY_VERIFIED |
| Uttar Pradesh 2026 | Fixture: `etl/contracts/sources/uttar_pradesh/fixtures/` | PARTIALLY_VERIFIED (placeholder mappings) |
| MCC Live 2026 | `data/raw/evidence/2026-08-12/mcc_live_evidence.json` | FIRST_CONTACT_VERIFIED / AUTOMATED_DOWNLOAD_BLOCKED |

---

## Gap Analysis Conclusions

1. **MCC is the only source with ANY modelling-ready data** (2 datasets: 2025 seat_matrix + allotments)
2. **Zero state historical data** exists in the repository for modelling
3. **2021-2024 MCC data** is documented as "available" in config but has NO repository evidence
4. **Automated MCC downloads blocked** by HTTP 403 bot protection
5. **UP mappings are unverified placeholders** — explicit reliability issue
6. **Minimum requirement**: 4 verified years per source for temporal validation
7. **Current state**: 1 verified year (MCC 2025) — **3 more years needed**

**Sprint 3.7 must focus on**: Converting config-claimed availability into repository-verified evidence, starting with MCC 2021-2024.