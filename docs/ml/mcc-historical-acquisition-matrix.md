# MCC Historical Acquisition Matrix — Sprint 3.8

## Phase 2: Explicit Historical Target Matrix

This document tracks the acquisition status for MCC historical artefacts across years 2021-2025.

**Evidence Taxonomy** (from `docs/ml/historical-artifact-handling.md`):
- `PORTAL_EXISTS` — Official portal reachable (HTTP 200)
- `DOCUMENT_EXISTS` — Document listed on archive page
- `DOCUMENT_RETRIEVED` — File successfully downloaded
- `DOCUMENT_EXAMINED` — Structure inspected, headers/schema recorded
- `FORMAT_VERIFIED` — Column headers, category/quota codes match contract expectations
- `CONTRACT_COMPATIBLE` — Can reuse existing MCC contract v1.1.0 with only year/round changes
- `MODELLING_READY` — Passes all 15 Sprint 3.6 quality gates

**Critical Distinction**: `PORTAL_EXISTS` ≠ `DOCUMENT_RETRIEVED` ≠ `FORMAT_VERIFIED` ≠ `CONTRACT_COMPATIBLE` ≠ `MODELLING_READY`

---

### MCC Seat Matrix Acquisition Matrix

| Year | Round | Portal Exists | Document Exists | Document Retrieved | Document Examined | Format Verified | Contract Compatible | Provenance Status | PII Status | Modelling Ready | Notes |
|------|-------|---------------|-----------------|-------------------|-------------------|-----------------|---------------------|-------------------|------------|-----------------|-------|
| 2025 | Round 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | COMPLETE | CLEAN | ✅ READY | Verified in Sprint 3.2-3.6 |
| 2024 | Round 1 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |
| 2023 | Round 1 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |
| 2022 | Round 1 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |
| 2021 | Round 1 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |

### MCC Allotment Results Acquisition Matrix

| Year | Round | Portal Exists | Document Exists | Document Retrieved | Document Examined | Format Verified | Contract Compatible | Provenance Status | PII Status | Modelling Ready | Notes |
|------|-------|---------------|-----------------|-------------------|-------------------|-----------------|---------------------|-------------------|------------|-----------------|-------|
| 2025 | Round 3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | COMPLETE | CLEAN | ✅ READY | Verified in Sprint 3.2-3.6 |
| 2024 | Round 3 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |
| 2023 | Round 3 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |
| 2022 | Round 3 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |
| 2021 | Round 3 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | UNKNOWN | NONE | UNKNOWN | ❌ NOT_READY | Automated download HTTP 403 |

### MCC Vacancy Data Acquisition Matrix

| Year | Round | Portal Exists | Document Exists | Document Retrieved | Document Examined | Format Verified | Contract Compatible | Provenance Status | PII Status | Modelling Ready | Notes |
|------|-------|---------------|-----------------|-------------------|-------------------|-----------------|---------------------|-------------------|------------|-----------------|-------|
| 2025 | All | ✅ | ✅ | ❌ | ❌ | ❌ | N/A | NONE | N/A | ❌ NOT_READY | No vacancy canonical model |
| 2024 | All | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | N/A | ❌ NOT_READY | |
| 2023 | All | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | N/A | ❌ NOT_READY | |
| 2022 | All | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | N/A | ❌ NOT_READY | |
| 2021 | All | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | N/A | ❌ NOT_READY | |

### MCC Information Bulletins Acquisition Matrix

| Year | Portal Exists | Document Exists | Document Retrieved | Document Examined | Format Verified | Contract Compatible | Provenance Status | Notes |
|------|---------------|-----------------|-------------------|-------------------|-----------------|---------------------|-------------------|-------|
| 2025 | ✅ | ✅ | ❌ | ❌ | ❌ | N/A | NONE | Reference only |
| 2024 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | Reference only |
| 2023 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | Reference only |
| 2022 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | Reference only |
| 2021 | ✅ | ✅ | ❌ BLOCKED | ❌ | ❌ | N/A | NONE | Reference only |

### MCC Joined/Admitted Lists Acquisition Matrix

| Year | Portal Exists | Document Exists | Document Retrieved | Document Examined | PII Status | Modelling Ready | Notes |
|------|---------------|-----------------|-------------------|-------------------|------------|-----------------|-------|
| 2025 | ✅ | ✅ | ❌ BLOCKED | ❌ | PII_BEARING | ❌ EXCLUDED | Candidate PII, not ingestible |
| 2024 | ✅ | ✅ | ❌ BLOCKED | ❌ | PII_BEARING | ❌ EXCLUDED | Candidate PII, not ingestible |
| 2023 | ✅ | ❌ | ❌ | ❌ | N/A | ❌ EXCLUDED | Not published per archive crawl |
| 2022 | ✅ | ❌ | ❌ | ❌ | N/A | ❌ EXCLUDED | Not published per archive crawl |
| 2021 | ✅ | ✅ | ❌ BLOCKED | ❌ | PII_BEARING | ❌ EXCLUDED | Candidate PII, not ingestible |

---

### Retrieval Status Summary

**Automated Retrieval**: BLOCKED — HTTP 403 on all direct file downloads from `https://mcc.nic.in/archive-ug/` (Sprint 3.1A live verification 2026-08-12)

**Manual Retrieval Path** (if attempted):
1. Navigate to `https://mcc.nic.in/archive-ug/` in browser
2. Select year (2021, 2022, 2023, 2024)
3. Download seat matrix PDF, allotment result CSV/PDF, vacancy PDF
4. Record SHA-256 checksums, retrieval timestamps, exact URLs
5. Convert PDF tables to CSV using `pdfplumber` (same parser as 2025)

**Status for 2021-2024**: `AUTOMATED_DOWNLOAD_BLOCKED` — no legitimate automated retrieval possible without bypassing bot protection.

---

### Contract Compatibility Assessment

**Current MCC Contract (v1.1.0)** implemented for 2025 only:
- Seat Matrix: `StateName, InstituteType, Institute, Quota, Branch, Category, TotalSeats`
- Allotments: `Institute Code, Institute Name, Course, Quota, Category, Round, Rank, Score, Seats`

**Assumption**: MCC document format is consistent across 2021-2025. **UNVERIFIED** — no historical source documents examined.

**If format compatible** (same columns, same category/quota codes):
- Minimal contract extension: new contract functions `seat_matrix_{year}_contract()`, `allotments_{year}_contract()` with only `effective_year` and `publication_version` changed
- Can reuse existing `MCCSeatMatrixAdapter`, `MCCAllotmentsAdapter`, mappings, provenance

**If format differs**:
- Document exact differences per year
- Create year-specific contract only if real source evidence proves necessary
- Never change canonical models to accommodate one historical document

---

### Target for Sprint 3.8

Given `AUTOMATED_DOWNLOAD_BLOCKED` for all 2021-2024 artefacts:

| Year | Dataset | Expected Outcome |
|------|---------|------------------|
| 2024 | seat_matrix | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2024 | allotments | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2023 | seat_matrix | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2023 | allotments | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2022 | seat_matrix | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2022 | allotments | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2021 | seat_matrix | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |
| 2021 | allotments | NOT_VERIFIED → NOT_READY (documented `AUTOMATED_DOWNLOAD_BLOCKED`) |

**If manual retrieval is performed and format verified**:
- Update status to `FORMAT_VERIFIED` / `CONTRACT_COMPATIBLE`
- Create minimal test fixtures (10-20 rows, no PII)
- Run through full quality gates
- Update `modelling_readiness.yaml` with evidence-based classification

**Acceptable Final Result**: MCC 2025 = READY, 2021-2024 = NOT_READY (if evidence supports it)

---

### Remaining Gaps for Temporal Validation

| Requirement | Current Status | Gap |
|-------------|----------------|-----|
| Minimum 3 verified MCC years | 1 (2025 only) | Need 2-3 more |
| Minimum 4 verified years (preferred) | 1 | Need 3-4 more |
| Cross-state validation | 0 state years | Need state historical data |
| Verified UP mappings | Placeholder only | UP cannot be modelling-ready |

---

*This matrix will be updated as Sprint 3.8 progresses. Each status change requires evidence.*