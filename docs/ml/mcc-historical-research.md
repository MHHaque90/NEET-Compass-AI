# MCC Historical Data Research — Sprint 3.7

## Phase 3/4: MCC Source Research (2021-2025)

This document records the official source research for MCC historical counselling data. Evidence is based on repository documentation and config claims.

---

### MCC Official Sources (from config/data_sources.yaml)

| Source ID | Authority | Official URL | Verification Status |
|-----------|-----------|--------------|---------------------|
| `mcc_ug_archive` | MCC / DGHS | https://mcc.nic.in/archive-ug/ | VERIFIED (page accessible) |
| `mcc_ug_counselling` | MCC / DGHS | https://mcc.nic.in/ug-medical-counselling/ | VERIFIED (page accessible) |

---

### Sprint 3.1A Live Verification (2026-08-12)

**Evidence File**: `data/raw/evidence/2026-08-12/mcc_live_evidence.json`

| Check | Result |
|-------|--------|
| Archive page (https://mcc.nic.in/archive-ug/) | HTTP 200 - ACCESSIBLE |
| Counselling page (https://mcc.nic.in/ug-medical-counselling/) | HTTP 200 - ACCESSIBLE |
| Automated PDF downloads | HTTP 403 - BLOCKED (bot protection) |
| First-contact GET | SUCCESS |

**Status**: `FIRST_CONTACT_VERIFIED` / `AUTOMATED_DOWNLOAD_BLOCKED`

---

### Documented Historical Availability (from docs/data-sources/mcc-historical-dataset-matrix.md)

| Year | Seat Matrix | Allotment Result | Vacancy | Info Bulletin | Joined/Admitted List | Participating Institutes |
|------|-------------|------------------|---------|---------------|---------------------|-------------------------|
| 2025 | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified |
| 2024 | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ❌ Not Found |
| 2023 | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ❌ Not Found | ❌ Not Found |
| 2022 | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ❌ Not Found | ❌ Not Found |
| 2021 | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ✅ Verified | ❌ Not Found |

**Verification Method**: Three-day crawl of archive page (2026-08-09)
**Caveat**: "Automated downloads rejected HTTP 403" — documents found but NOT downloaded/ingested

---

### Repository Evidence vs Config Claims

| Year | Config Claim | Repository Evidence | Status |
|------|--------------|---------------------|--------|
| 2025 | Seat matrix + allotments available | Contracts (v1.1.0), adapters, tests, provenance | **VERIFIED** |
| 2024 | All document families available | NONE (no contracts, fixtures, raw data) | NOT_VERIFIED |
| 2023 | All document families available | NONE | NOT_VERIFIED |
| 2022 | All document families available | NONE | NOT_VERIFIED |
| 2021 | All document families available | NONE | NOT_VERIFIED |

**Critical Gap**: Config documents 2021-2025 as "verified available" but repository has ZERO ingestion evidence for 2021-2024.

---

### Contract Compatibility Assessment (Phase 4)

**Current MCC Contract (v1.1.0)**: Only implemented for 2025

| Year | Seat Matrix Contract | Allotment Contract | Compatible with v1.1.0? | Notes |
|------|---------------------|-------------------|------------------------|-------|
| 2025 | ✅ Implemented | ✅ Implemented | YES | Round 1 seat matrix, Round 3 allotments |
| 2024 | ❌ Not implemented | ❌ Not implemented | UNKNOWN | Format assumed same, needs verification |
| 2023 | ❌ Not implemented | ❌ Not implemented | UNKNOWN | Format assumed same, needs verification |
| 2022 | ❌ Not implemented | ❌ Not implemented | UNKNOWN | Format assumed same, needs verification |
| 2021 | ❌ Not implemented | ❌ Not implemented | UNKNOWN | Format assumed same, needs verification |

**Assumption**: MCC document format is consistent across years. This MUST be verified by examining actual source documents.

---

### Required Work to Make 2021-2024 VERIFIED

For each year (2021-2024), the following must exist in repository:

1. **Source Contracts** (`contracts.py`):
   - `seat_matrix_{year}_contract()` with correct `effective_year`
   - `allotments_{year}_contract()` with correct `effective_year` and `publication_version`
   - Same column definitions, validation rules as 2025

2. **Adapters** (`adapters.py`):
   - `MCCSeatMatrixAdapter` / `MCCAllotmentsAdapter` (can reuse 2025 adapters if format identical)
   - PII blocklist enforcement

3. **Provenance** (`provenance.py`):
   - Same SHA-256 / source_file_id logic
   - Parser version tracking

4. **Test Fixtures**:
   - Real or representative CSV/PDF samples for each year/round
   - Unit tests for contract, adapter, provenance, pipeline

5. **Pipeline Tests**:
   - Idempotency verification
   - PostgreSQL integration tests (where environment permits)

6. **Actual Source Artifacts** (or documented retrieval):
   - Evidence of successful download/parse (checksums, metadata)
   - OR documented `AUTOMATED_DOWNLOAD_BLOCKED` with manual retrieval path

---

### Automated Download Blocking — Honest Documentation

**Current Status**: MCC archive blocks automated PDF/CSV downloads (HTTP 403)

**Options for Sprint 3.7**:

| Option | Description | Feasibility |
|--------|-------------|-------------|
| **Manual download + commit fixtures** | Download via browser, commit minimal test fixtures | HIGH - but fixtures must be legally permissible |
| **Document manual retrieval path** | Record exact URLs, manual steps, checksums | HIGH - transparent, no automation bypass |
| **Request API access** | Contact MCC for official data access | LOW - unlikely in sprint timeframe |
| **Use alternative sources** | State archives, RTI, published reports | MEDIUM - may not be canonical |

**Sprint 3.7 Decision**: Document manual retrieval path with exact URLs and checksums. Do NOT bypass bot protection. If fixtures cannot be legally committed, record `SOURCE_URL_VERIFIED` / `CHECKSUM_VERIFIED` / `DOWNLOAD_BLOCKED`.

---

### MCC Research Summary

| Item | Status | Evidence |
|------|--------|----------|
| Archive page accessible | ✅ VERIFIED | Live evidence 2026-08-12 |
| 2021-2025 documents listed | ✅ VERIFIED | Archive crawl 2026-08-09 |
| 2021-2024 downloaded/ingested | ❌ NOT_VERIFIED | Zero repository evidence |
| 2025 downloaded/ingested | ✅ VERIFIED | Contracts, adapters, tests |
| Contract compatibility (2021-2024) | UNKNOWN | No source documents examined |
| Automated downloads | BLOCKED (HTTP 403) | Live evidence 2026-08-12 |
| Manual retrieval possible | LIKELY | Archive page accessible |

**Next Step**: Attempt manual retrieval of 2021-2024 seat matrix and allotment documents to verify format compatibility and create minimal test fixtures.