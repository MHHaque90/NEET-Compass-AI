# Historical Evidence Acquisition Matrix — Sprint 4.4

**Classification:** OPERATIONAL REFERENCE  
**Version:** 1.0  
**Status:** AUTHORIZED FOR USE  
**Sprint:** 4.4 — Historical Evidence Acquisition Path & Readiness Activation  
**Baseline:** Sprint 4.3 Certified State (HEAD 6d8f1f6)

---

## 1. Purpose

This matrix documents the **exact current acquisition status** for every historical dataset/year combination across all four authorities in scope. It is derived directly from `config/modelling_readiness.yaml` and the existing evidence taxonomy. No values are invented. Unknown values remain UNKNOWN/NOT_VERIFIED.

**Critical Principle:** SOURCE TRUTH > DATA VOLUME > MODEL AVAILABILITY

---

## 2. Scope Definition

| Authority | Source ID | Years in Scope | Datasets |
|-----------|-----------|----------------|----------|
| Medical Counselling Committee (MCC) | `mcc_ug_archive` | 2021-2025 | seat_matrix, allotments |
| Maharashtra (MAHA CET Cell) | `mcc_state_maharashtra` | 2021-2025 | seat_matrix, allotments |
| Karnataka (KEA) | `mcc_state_karnataka` | 2021-2025 | seat_matrix, allotments |
| Uttar Pradesh (UPMU/DME UP) | `mcc_state_uttar_pradesh` | 2021-2025 | seat_matrix, allotments |

**Total Combinations:** 4 authorities × 5 years × 2 datasets = **40 dataset/year combinations**

**Note:** 2026 is excluded from historical scope (current cycle, not historical). 2025 MCC is already MODELLING_READY.

---

## 3. Status Vocabulary (from `etl/contracts/historical/status.py`)

| Status | Meaning |
|--------|---------|
| `SOURCE_CLAIMED` | Claimed in config, no verification |
| `SOURCE_VERIFIED` | Official URL accessible (HTTP 200) |
| `AUTOMATED_DOWNLOAD_BLOCKED` | HTTP 403/429 on automated retrieval |
| `MANUALLY_RETRIEVED` | Human downloaded via browser |
| `NOT_VERIFIED` | Config claims but zero repository evidence |
| `FORMAT_VERIFIED` | Schema matches contract expectations |
| `FORMAT_UNKNOWN` | No source document examined |
| `FORMAT_MISMATCH` | Structure differs from contract |
| `PII_DETECTED` | Candidate identifiers found |
| `PII_CLEAR` | No PII columns in canonical path |
| `CONTRACT_COMPATIBLE` | Reuses existing contract |
| `CONTRACT_COMPATIBLE_WITH_LIMITATIONS` | Minor differences documented |
| `CONTRACT_INCOMPATIBLE` | Requires new contract version |
| `CONTRACT_UNKNOWN` | No contract exists for this year |
| `VALIDATED` | Passed data quality gates |
| `MODELLING_READY` | All gates pass, temporal ready |
| `READY_WITH_LIMITATIONS` | Critical gates pass, non-critical documented |
| `NOT_READY` | Any critical gate fails |
| `MAPPING_NOT_VERIFIED` | Placeholder mappings (UP specific) |

---

## 4. MCC (Medical Counselling Committee) — All India Quota

**Source:** `https://mcc.nic.in/archive-ug/`  
**Automated Access:** HTTP 403 confirmed (2026-08-31 re-verification)  
**Contract:** v1.1.0 (2025 only)  
**Modelling-Ready Years:** 2025 only

### 4.1 Seat Matrix

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2025 | Round 1 | VERIFIED | READY | MODELLING_READY | MODELLING_READY | CONTRACT_COMPATIBLE (v1.1.0) | COMPLETE | PII_CLEAR | 15/15 PASS | None | Sprint 3.2-3.6 verified |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |

### 4.2 Allotments

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2025 | Round 3 | VERIFIED | READY | MODELLING_READY | MODELLING_READY | CONTRACT_COMPATIBLE (v1.1.0) | COMPLETE | PII_CLEAR | 15/15 PASS | None | Sprint 3.2-3.6 verified |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | config/modelling_readiness.yaml |

**MCC Summary:** 2/10 dataset/year combinations MODELLING_READY. 8/10 blocked by AUTOMATED_DOWNLOAD_BLOCKED. Format compatibility for 2021-2024 is UNKNOWN — cannot assume v1.1.0 applies without examining actual source documents.

---

## 5. Maharashtra (MAHA CET Cell) — State Quota

**Source:** `https://cetcell.mahacet.org/`  
**Archive Status:** NOT VERIFIED per `config/data_sources.yaml`  
**Contract:** v1.0.0 (2026 fixture only)  
**Modelling-Ready Years:** None (2026 is READY_WITH_LIMITATIONS — fixture only)

### 5.1 Seat Matrix

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2026 | Round 1 | VERIFIED | READY_WITH_LIMITATIONS | QUALITY_GATES_PASSED | READY_WITH_LIMITATIONS | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE | PII_CLEAR | 13/15 PASS | Fixture-only, no live download | config/modelling_readiness.yaml |
| 2025 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |

### 5.2 Allotments

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2026 | Round 1 | VERIFIED | READY_WITH_LIMITATIONS | QUALITY_GATES_PASSED | READY_WITH_LIMITATIONS | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE | PII_CLEAR | 13/15 PASS | Fixture-only, no live download | config/modelling_readiness.yaml |
| 2025 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |

**Maharashtra Summary:** 0/10 historical (2021-2025) dataset/year combinations have any evidence. 2026 fixtures exist but are not historical. Archive access completely UNVERIFIED. Format compatibility UNKNOWN.

---

## 6. Karnataka (KEA) — State Quota

**Source:** `https://cetonline.karnataka.gov.in/kea/`  
**Archive Status:** NOT VERIFIED per `config/data_sources.yaml`  
**Contract:** v1.0.0 (2026 fixture only)  
**Modelling-Ready Years:** None (2026 is READY_WITH_LIMITATIONS — fixture only)

### 6.1 Seat Matrix

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2026 | Round 1 | VERIFIED | READY_WITH_LIMITATIONS | QUALITY_GATES_PASSED | READY_WITH_LIMITATIONS | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE | PII_CLEAR | 13/15 PASS | Fixture-only, no live download | config/modelling_readiness.yaml |
| 2025 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |

### 6.2 Allotments

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2026 | Round 1 | VERIFIED | READY_WITH_LIMITATIONS | QUALITY_GATES_PASSED | READY_WITH_LIMITATIONS | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE | PII_CLEAR | 12/15 PASS | Fixture-only, no fixture for allotments | config/modelling_readiness.yaml |
| 2025 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, zero repo evidence | config/modelling_readiness.yaml |

**Karnataka Summary:** 0/10 historical (2021-2025) dataset/year combinations have any evidence. 2026 seat_matrix fixture exists, allotments has no fixture. Archive access completely UNVERIFIED. Format compatibility UNKNOWN.

---

## 7. Uttar Pradesh (UPMU/DME UP) — State Quota

**Source:** `https://upneet.gov.in/` (alt: `https://bqnmc.up.gov.in/`)  
**Archive Status:** NOT VERIFIED per `config/data_sources.yaml`  
**Contract:** v1.0.0 (2026 fixture only) — **Category/Quota Mappings are PLACEHOLDERS**  
**Modelling-Ready Years:** None (2026 is NOT_READY due to placeholder mappings)

### 7.1 Seat Matrix

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2026 | Round 1 | VERIFIED | NOT_READY | NOT_READY | NOT_READY | CONTRACT_COMPATIBLE_WITH_LIMITATIONS | COMPLETE | PII_CLEAR | 10/15 PASS | Category/quota mappings are PLACEHOLDERS | config/modelling_readiness.yaml, mappings.py |
| 2025 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readings.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |

### 7.2 Allotments

| Year | Round | Verification Status | Readiness | Lifecycle Stage | Evidence Status | Contract Status | Provenance | PII Status | Quality Gates | Blocker | Evidence Reference |
|------|-------|---------------------|-----------|-----------------|-----------------|-----------------|------------|------------|---------------|---------|---------------------|
| 2026 | Round 1 | VERIFIED | NOT_READY | NOT_READY | NOT_READY | CONTRACT_COMPATIBLE_WITH_LIMITATIONS | COMPLETE | PII_CLEAR | 9/15 PASS | Category/quota mappings PLACEHOLDER, no fixture | config/modelling_readiness.yaml, mappings.py |
| 2025 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2024 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2023 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2022 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |
| 2021 | All | NOT_VERIFIED | NOT_READY | DISCOVERED | NOT_VERIFIED | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | 0/15 | Archive NOT VERIFIED, mappings PLACEHOLDER | config/modelling_readiness.yaml |

**Uttar Pradesh Summary:** 0/10 historical (2021-2025) dataset/year combinations have any evidence. 2026 has contract/adapter but **category/quota mappings are explicitly PLACEHOLDERS** (documented in `etl/contracts/sources/uttar_pradesh/mappings.py`). Gate 5 (category validity) and Gate 6 (quota validity) would fail on real data. UP cannot be modelling-ready until mappings are verified against actual source data.

---

## 8. Cross-Authority Summary

### 8.1 Modelling-Ready Count by Authority

| Authority | Historical Years (2021-2025) | Total Combinations | MODELLING_READY | READY_WITH_LIMITATIONS | NOT_READY / NOT_VERIFIED |
|-----------|------------------------------|-------------------|-----------------|------------------------|--------------------------|
| MCC | 2021-2025 | 10 | 2 (2025 only) | 0 | 8 |
| Maharashtra | 2021-2025 | 10 | 0 | 0 | 10 |
| Karnataka | 2021-2025 | 10 | 0 | 0 | 10 |
| Uttar Pradesh | 2021-2025 | 10 | 0 | 0 | 10 |
| **TOTAL** | | **40** | **2** | **0** | **38** |

### 8.2 Blocker Distribution

| Blocker Type | Count | Affected Authorities |
|--------------|-------|---------------------|
| AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | 8 | MCC (2021-2024 both datasets) |
| Archive NOT VERIFIED | 30 | Maharashtra (10), Karnataka (10), UP (10) |
| Category/Quota Mappings PLACEHOLDER | 2 (2026) + 10 historical | UP (all years) |
| CONTRACT_UNKNOWN | 38 | All historical years all authorities |
| FORMAT_UNKNOWN | 38 | All historical years all authorities |
| PROVENANCE_INCOMPLETE | 38 | All historical years all authorities |

### 8.3 Verified Modelling-Ready Years (from registry)

```yaml
modelling_ready_years:
  MCC: [2025]
  Maharashtra: []
  Karnataka: []
  Uttar_Pradesh: []
```

---

## 9. Acquisition Method Status

| Authority | Automated Download | Manual Browser Path | Manual Path Documented | Manual Path Tested |
|-----------|-------------------|---------------------|------------------------|---------------------|
| MCC | BLOCKED (HTTP 403) | Documented | YES (Sprint 3.1A) | NO |
| Maharashtra | UNKNOWN (Archive NOT VERIFIED) | UNKNOWN | NO | NO |
| Karnataka | UNKNOWN (Archive NOT VERIFIED) | UNKNOWN | NO | NO |
| Uttar Pradesh | UNKNOWN (Archive NOT VERIFIED) | UNKNOWN | NO | NO |

---

## 10. Evidence References

All status values in this matrix are derived from:
- `config/modelling_readiness.yaml` (primary source of truth)
- `etl/contracts/historical/status.py` (status taxonomy)
- `etl/contracts/historical/lifecycle.py` (lifecycle stages)
- `docs/ml/mcc-historical-acquisition-matrix.md` (Sprint 3.8)
- `docs/ml/maharashtra-historical-research.md` (Sprint 3.7)
- `docs/ml/karnataka-historical-research.md` (Sprint 3.7)
- `docs/ml/uttar_pradesh-historical-research.md` (Sprint 3.7)

---

## 11. Key Conclusions for Sprint 4.4

1. **No new historical evidence verified** since Sprint 3.8 baseline
2. **MCC 2021-2024**: Only blocker is HTTP 403 automated download — manual path documented but not executed
3. **Maharashtra/Karnataka/UP 2021-2025**: Archive access completely UNVERIFIED — zero repository evidence
4. **UP Critical Blocker**: Category/quota mappings are explicit PLACEHOLDERS — cannot be modelling-ready even if data obtained
5. **Format compatibility**: UNKNOWN for all historical years — cannot assume current contracts apply
6. **Temporal validation**: BLOCKED (1 verified year, need ≥3)
7. **Target readiness**: NO_TARGET_READY (insufficient historical coverage)
8. **Training**: TRAINING_BLOCKED (temporal blocked + no target)

**This matrix will not change until legitimate evidence is acquired and passes all gates.**

---

*End of Historical Acquisition Matrix — Sprint 4.4*