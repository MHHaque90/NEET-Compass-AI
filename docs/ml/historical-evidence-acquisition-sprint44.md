# Official Human Historical Evidence Acquisition Procedure — Sprint 4.4

**Classification:** OFFICIAL PROCEDURE  
**Version:** 1.0  
**Status:** AUTHORIZED FOR USE  
**Sprint:** 4.4 — Historical Evidence Acquisition Path & Readiness Activation  
**Supersedes:** `docs/ml/historical-acquisition-guide.md` (Sprint 3.9) — This document is the authoritative Sprint 4.4 update

---

## 1. Purpose

This document defines the **legitimate, auditable, fail-closed procedure** for a human operator to acquire and submit historical NEET UG counselling evidence to the NEET Compass AI project.

**This procedure does NOT provide instructions for bypassing access controls.**

**Core Principle:** An artifact entering the repository must have complete provenance, verified integrity, no PII leakage, and pass all gates. Possession of an artifact does NOT imply modelling readiness.

---

## 2. Authoritative Sources & Legitimate Acquisition Methods

### 2.1 MCC (Medical Counselling Committee) — All India Quota

| Artifact Type | Official URL | Acquisition Method | Status |
|---------------|--------------|-------------------|--------|
| Seat Matrix (per round) | `https://mcc.nic.in/archive-ug/` | Manual browser download | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) |
| Allotment Results (per round) | `https://mcc.nic.in/archive-ug/` | Manual browser download | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) |
| Vacancy Reports | `https://mcc.nic.in/archive-ug/` | Manual browser download | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) |
| Information Bulletins | `https://mcc.nic.in/archive-ug/` | Manual browser download | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) |
| Joined/Admitted Lists | `https://mcc.nic.in/archive-ug/` | **EXCLUDED** — PII by definition | PII_EXCLUDED |

**Live Verification (2026-08-31):** Archive page returns HTTP 200; direct file downloads return HTTP 403 (bot protection). Automated download is BLOCKED. Manual browser retrieval path is documented but NOT EXECUTED.

### 2.2 Maharashtra (MAHA CET Cell) — State Quota

| Artifact Type | Official URL | Acquisition Method | Status |
|---------------|--------------|-------------------|--------|
| Seat Matrix / Allotments | `https://cetcell.mahacet.org/` | UNKNOWN | Archive NOT VERIFIED per config |

**Status:** Archive accessibility completely UNVERIFIED. No manual retrieval path documented. No repository evidence for 2021-2025.

### 2.3 Karnataka (KEA) — State Quota

| Artifact Type | Official URL | Acquisition Method | Status |
|---------------|--------------|-------------------|--------|
| Seat Matrix / Allotments | `https://cetonline.karnataka.gov.in/kea/` | UNKNOWN | Archive NOT VERIFIED per config |

**Status:** Archive accessibility completely UNVERIFIED. No manual retrieval path documented. No repository evidence for 2021-2025.

### 2.4 Uttar Pradesh (UPMU/DME UP) — State Quota

| Artifact Type | Official URL | Acquisition Method | Status |
|---------------|--------------|-------------------|--------|
| Seat Matrix / Allotments | `https://upneet.gov.in/` (alt: `https://bqnmc.up.gov.in/`) | UNKNOWN | Archive NOT VERIFIED per config |

**Critical Blocker:** Category/quota mappings in `etl/contracts/sources/uttar_pradesh/mappings.py` are explicitly documented as **PLACEHOLDERS**. Even if data is downloaded, Gate 5 (category validity) and Gate 6 (quota validity) will FAIL on real data. UP cannot be modelling-ready until mappings are verified against actual source documents.

---

## 3. What Constitutes Acceptable Evidence

### 3.1 Required Metadata (per `EvidenceManifest` in `etl/contracts/historical/manifest.py`)

For **every artifact**, the following MUST be recorded:

| Field | Description | Example |
|-------|-------------|---------|
| `source_authority` | Official body name | "Medical Counselling Committee" |
| `source_url` | Exact download URL | "https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.pdf" |
| `source_identifier` | Source ID from `data_sources.yaml` | "mcc_ug_archive" |
| `dataset_type` | "seat_matrix" / "allotments" / "vacancy" / "bulletin" | "seat_matrix" |
| `counselling_year` | NEET UG counselling year (not publication year) | 2024 |
| `round` | Counselling round | "Round 1" |
| `course` | Course coverage | "MBBS+BDS+NURSING" (MCC) / "MBBS+BDS" (State) |
| `quota` | "ALL_INDIA" / "STATE_QUOTA" | "ALL_INDIA" |
| `retrieval_method` | "MANUAL_BROWSER" / "AUTOMATED" / "BLOCKED" | "MANUAL_BROWSER" |
| `retrieval_timestamp` | UTC ISO 8601 at moment of download | "2026-09-01T14:30:00+00:00" |
| `retrieval_status` | "SUCCESS" / "AUTOMATED_DOWNLOAD_BLOCKED" / "FAILED" | "SUCCESS" |

### 3.2 Artifact Integrity Requirements

| Requirement | Specification |
|-------------|---------------|
| **SHA-256 Checksum** | Full 64-character hex digest of original file bytes |
| **File Preservation** | Save exactly as downloaded — do NOT rename, convert, or modify |
| **Original Filename** | Record in `artifact_filename` |
| **MIME Type** | `application/pdf`, `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| **File Size** | Bytes |

**Commands to compute SHA-256:**
```bash
# Linux/macOS
sha256sum /path/to/artifact.pdf

# Windows PowerShell
Get-FileHash -Algorithm SHA256 -Path "C:\path\to\artifact.pdf"

# Python
import hashlib
with open("artifact.pdf", "rb") as f:
    print(hashlib.sha256(f.read()).hexdigest())
```

### 3.3 Provenance Requirements (10 Required Fields)

From `etl.contracts.canonical.SourceMetadata` — ALL must be present and non-empty:

1. `source_id` — e.g., "mcc_ug_archive"
2. `authority` — e.g., "Medical Counselling Committee"
3. `dataset` — e.g., "seat_matrix"
4. `effective_year` — e.g., 2024
5. `publication_version` — e.g., "Round 1"
6. `contract_version` — e.g., "1.1.0" (if known)
7. `retrieval_timestamp` — UTC ISO 8601
8. `source_file_id` — Deterministic: `{source_id}_{dataset}_{year}_{checksum[:12]}`
9. `file_checksum` — SHA-256 hex digest
9. `parser_version` — e.g., "mcc_etl_v1"
10. `source_url` — Exact download URL

### 3.4 PII Screening Requirements

**MANDATORY:** Run PII gate on column headers BEFORE submission.

**Blocklist (representative — see `etl/contracts/historical/pii_gate.py` for full list):**
- Direct identifiers: `candidate_name`, `father_name`, `mother_name`, `roll_number`, `application_number`, `registration_number`, `neet_roll_number`
- Contact: `phone`, `mobile`, `email`, `address`
- Identity: `aadhaar`, `pan`, `passport_number`, `caste_certificate_number`
- Scores linked to candidate: `percentile`, `neet_score`, `all_india_rank`, `air`, `state_rank`
- Photos/signatures: `photograph`, `signature`, `thumb_impression`
- Application: `application_id`, `form_number`, `user_id`, `login_id`
- Demographics: `date_of_birth`, `gender`, `category`, `sub_category`, `pwd_status`, `ews_status`

**If PII detected:**
1. DO NOT submit the raw file
2. Document `pii_status: "PII_DETECTED"` in manifest
3. Record which columns triggered detection
4. Artifact classified as `BLOCKED_PII` — CANNOT enter canonical modelling boundary
5. Joined/Admitted lists are ALWAYS `PII_EXCLUDED` by definition

**Screening Command:**
```python
from etl.contracts.historical.pii_gate import detect_pii
# For CSV/Excel: read column headers
detected = detect_pii(column_headers)
if detected:
    print(f"PII DETECTED: {detected}")
    # DO NOT SUBMIT
```

---

## 4. Contract & Format Verification

### 4.1 Contract Compatibility Classification

| Classification | Meaning | Modelling Readiness |
|----------------|---------|---------------------|
| `CONTRACT_COMPATIBLE` | Reuses existing contract exactly | Eligible for READY (if all other gates pass) |
| `CONTRACT_COMPATIBLE_WITH_LIMITATIONS` | Minor differences documented | READY_WITH_LIMITATIONS |
| `CONTRACT_INCOMPATIBLE` | Requires new contract version | NOT_READY — must NOT force through adapter |
| `CONTRACT_UNKNOWN` | No contract exists for this year | NOT_READY — cannot proceed without verification |

**Rule:** `UNKNOWN` and `INCOMPATIBLE` MUST fail closed. No automatic promotion.

### 4.2 Format Verification Steps

1. **Inspect column headers** — document exact names and order
2. **Record data types** — string, integer, numeric per column
3. **Inspect sample rows** — minimum 5 rows, verify structure
4. **Map category/quota codes** — verify against contract enums
5. **Document `format_status`**: `FORMAT_VERIFIED` / `FORMAT_UNKNOWN` / `FORMAT_MISMATCH`

**If format differs from contract:** Create new contract version ONLY if real source evidence proves necessary. Never change canonical models to accommodate one historical document.

---

## 5. Quality Gate Requirements

All 15 Sprint 3.6 data quality gates must execute and pass:

| Gate | Description | Critical |
|------|-------------|----------|
| gate_1 | Schema compliance | YES |
| gate_2 | Required columns present | YES |
| gate_3 | No duplicate primary keys | YES |
| gate_4 | Foreign key validity | YES |
| gate_5 | Category validity | YES |
| gate_6 | Quota validity | YES |
| gate_7 | Round validity | YES |
| gate_8 | Year validity | YES |
| gate_9 | Rank bounds | YES |
| gate_10 | Seat count bounds | YES |
| gate_11 | Data freshness | NO |
| gate_12 | Cross-reference integrity | YES |
| gate_13 | Source verification | YES |
| gate_14 | PII exclusion | YES |
| gate_15 | Provenance completeness | YES |

**Classification Logic:**
- `READY`: All critical gates pass + temporal safety
- `READY_WITH_LIMITATIONS`: Critical gates 1-10 pass, non-critical documented
- `NOT_READY`: Any critical gate fails

---

## 6. Readiness Promotion Requirements

An artifact becomes **MODELLING_READY** ONLY when ALL conditions met:

1. ✅ Source authority verified (official URL HTTP 200)
2. ✅ Artifact retrieved (manual or automated, HTTP 200)
3. ✅ SHA-256 computed and recorded
4. ✅ Format inspected and documented
5. ✅ PII screening PASSED (no candidate identifiers)
6. ✅ Contract compatibility = `COMPATIBLE` or `COMPATIBLE_WITH_LIMITATIONS`
7. ✅ Parsed through canonical adapter successfully
8. ✅ All 15 quality gates executed and passed
9. ✅ Complete provenance (10 fields) recorded
10. ✅ Idempotency verified (re-ingestion produces identical results)
11. ✅ `modelling_readiness.yaml` updated with evidence-based classification
12. ✅ Temporal readiness gate passed (minimum 3 verified years)

**READY_WITH_LIMITATIONS** requires 1-10 above but with documented non-critical limitations.

**NO shortcuts.** Each stage requires documented evidence.

---

## 7. Rejection Conditions

An artifact is **REJECTED** (cannot proceed) if ANY condition applies:

| Condition | Resulting Status | Recovery |
|-----------|------------------|----------|
| HTTP 403 on automated download | `AUTOMATED_DOWNLOAD_BLOCKED` | Manual retrieval required (if permitted) |
| Source URL returns 404/not found | `ARCHIVE_INACCESSIBLE` | Document failure, no recovery |
| PII columns detected | `PII_DETECTED` / `PII_EXCLUDED` | Cannot enter modelling boundary |
| Contract = `INCOMPATIBLE` | `CONTRACT_INCOMPATIBLE` | New contract version required |
| Contract = `UNKNOWN` | `CONTRACT_UNKNOWN` | Format inspection required |
| Provenance fields missing | `PROVENANCE_INCOMPLETE` | Complete all 10 fields |
| Quality gates fail | `BLOCKED_QUALITY_GATES_FAILED` | Fix data quality issues |
| Checksum mismatch | `ARTIFACT_INTEGRITY_FAILED` | Re-download, recompute |
| Temporal gate fails | `TEMPORAL_VALIDATION_BLOCKED` | Need ≥3 verified years |

---

## 8. Explicit Prohibitions

**ABSOLUTELY PROHIBITED when HTTP 403 occurs:**
- ❌ Do NOT use Selenium, Playwright, undetected-chromedriver to bypass bot protection
- ❌ Do NOT solve CAPTCHAs programmatically
- ❌ Do NOT rotate proxies/IPs to evade rate limits
- ❌ Do NOT scrape protected government portals
- ❌ Do NOT use unauthorized credentials, cookies, or tokens
- ❌ Do NOT modify headers to mimic browsers deceptively

**CORRECT ACTION when HTTP 403:**
1. Document `retrieval_status: "AUTOMATED_DOWNLOAD_BLOCKED"` in manifest
2. Record exact URL that returned 403
3. Document manual retrieval path (if available and permitted)
4. Do NOT commit code that attempts automated bypass

---

## 9. Submission Process

### 9.1 Prepare Submission Package

```
submission/
├── evidence_manifest.yaml    # Complete EvidenceManifest (all required fields)
├── fixture.csv               # If legally permissible (10-20 rows, no PII)
├── sha256.txt                # SHA-256 checksum
└── retrieval_notes.md        # Human-readable retrieval log
```

### 9.2 Contributor Validation Checklist

- [ ] Evidence manifest complete (all required fields per `REQUIRED_MANIFEST_FIELDS`)
- [ ] SHA-256 matches submitted file exactly
- [ ] PII screening passed (`pii_status: "PII_CLEAR"`)
- [ ] No automated bypass attempted
- [ ] Retrieval method documented honestly
- [ ] Counselling year and round correctly identified
- [ ] Source URL exact and accessible
- [ ] Contract version identified (or documented as UNKNOWN)
- [ ] Limitations explicitly listed

### 9.3 Maintainer Validation Checklist

- [ ] Manifest validates against schema (`validate_manifest()`)
- [ ] Provenance gate passes (all 10 fields)
- [ ] Artifact integrity verified (checksum matches)
- [ ] Contract compatibility assessed
- [ ] All 15 data quality gates executed
- [ ] Temporal readiness evaluated
- [ ] `modelling_readiness.yaml` updated with evidence

### 9.4 Submission Channels

**Do NOT commit artifacts directly to Git.**

1. **GitHub Issue** with "historical-evidence" label — attach manifest + notes
2. **Secure file transfer** (coordinate with maintainer) for fixtures
3. **Pull Request** touching ONLY:
   - `config/modelling_readiness.yaml` (status updates with evidence)
   - `etl/contracts/sources/*/fixtures/` (safe fixtures only)
   - `docs/ml/*.md` (documentation updates)

**Maintainer reviews ALL evidence before merging.**

---

## 10. Authority-Specific Procedures

### 10.1 MCC 2021-2024

| Step | Action |
|------|--------|
| 1 | Navigate to `https://mcc.nic.in/archive-ug/` in browser |
| 2 | Select year (2021, 2022, 2023, 2024) |
| 3 | Download seat matrix PDF, allotment result CSV/PDF, vacancy PDF |
| 4 | Record SHA-256, retrieval timestamp, exact URLs |
| 5 | Convert PDF tables to CSV using `pdfplumber` (same parser as 2025) |
| 6 | Run PII screening on column headers |
| 7 | Verify format against MCC contract v1.1.0 |
| 8 | Submit via procedure in Section 9 |

**Expected Outcome if format matches:** Minimal contract extension (year/round only), reuse existing adapters.

### 10.2 Maharashtra 2021-2025

| Step | Action |
|------|--------|
| 1 | Verify archive accessibility at `https://cetcell.mahacet.org/` |
| 2 | Document archive structure and available years |
| 3 | If accessible, follow manual download procedure |
| 4 | Record all metadata, checksums, format inspection |
| 5 | Verify against Maharashtra contract v1.0.0 |
| 6 | Submit via procedure in Section 9 |

**Prerequisite:** Archive access must be verified first. Current status: UNKNOWN.

### 10.3 Karnataka 2021-2025

| Step | Action |
|------|--------|
| 1 | Verify archive accessibility at `https://cetonline.karnataka.gov.in/kea/` |
| 2 | Document archive structure and available years |
| 3 | If accessible, follow manual download procedure |
| 4 | Record all metadata, checksums, format inspection |
| 5 | Verify against Karnataka contract v1.0.0 |
| 6 | Submit via procedure in Section 9 |

**Prerequisite:** Archive access must be verified first. Current status: UNKNOWN.

### 10.4 Uttar Pradesh 2021-2025

| Step | Action |
|------|--------|
| 1 | Verify archive accessibility at `https://upneet.gov.in/` / `https://bqnmc.up.gov.in/` |
| 2 | **CRITICAL:** Obtain actual source documents to verify category/quota mappings |
| 3 | Update `etl/contracts/sources/uttar_pradesh/mappings.py` with verified mappings |
| 4 | Remove PLACEHOLDER status from mappings |
| 5 | Follow manual download procedure |
| 6 | Record all metadata, checksums, format inspection |
| 7 | Verify against UP contract v1.0.0 |
| 8 | Submit via procedure in Section 9 |

**Hard Requirement:** Category/quota mappings MUST be verified against real source data before UP can ever be modelling-ready.

---

## 11. Quick Reference: Evidence Status Flow

```
DISCOVERED (config claims, no evidence)
    ↓ [source verified: URL HTTP 200, source_id registered]
SOURCE_VERIFIED
    ↓ [manual download: file retrieved, HTTP 200, timestamp recorded]
RETRIEVED / MANUALLY_RETRIEVED
    ↓ [SHA-256 computed, source_file_id generated]
HASHED
    ↓ [schema documented, column headers recorded, format_status set]
FORMAT_INSPECTED
    ↓ [PII blocklist applied, no candidate identifiers in canonical path]
PII_SCREENED (PII_CLEAR)
    ↓ [contract version identified, column mapping verified]
CONTRACT_CHECKED (CONTRACT_COMPATIBLE / COMPATIBLE_WITH_LIMITATIONS)
    ↓ [parsed through adapter, canonical records produced]
PARSED
    ↓ [all 15 quality gates executed, classification assigned]
VALIDATED
    ↓ [all 10 provenance fields present, checksum chain verified]
PROVENANCE_COMPLETE
    ↓ [re-ingestion produces identical canonical records]
IDEMPOTENCY_VERIFIED
    ↓ [all critical gates pass, no gate silently overridden]
QUALITY_GATES_PASSED
    ↓ [temporal readiness gate passed, minimum years satisfied]
MODELLING_READY
```

**Blocking States (require manual resolution):**
- `BLOCKED_AUTOMATED_DOWNLOAD` → Manual retrieval required
- `BLOCKED_FORMAT_INCOMPATIBLE` → New contract needed
- `BLOCKED_PII_DETECTED` → Cannot enter modelling boundary
- `BLOCKED_CONTRACT_INCOMPATIBLE` → New contract version required
- `BLOCKED_PROVENANCE_INCOMPLETE` → Missing required fields
- `BLOCKED_QUALITY_GATES_FAILED` → Fix data quality issues

---

## 12. Contact

For questions about this procedure, open a GitHub issue with label `historical-evidence`.

**Remember:** SOURCE TRUTH > DATA VOLUME. An artifact with complete, honest evidence is worth more than ten artifacts with gaps.

---

*End of Official Human Historical Evidence Acquisition Procedure — Sprint 4.4*