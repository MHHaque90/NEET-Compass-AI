# Historical Evidence Acquisition Guide — Sprint 3.9

**Classification**: OFFICIAL PROCEDURE
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 3.9 — Historical Evidence Acquisition & Data Readiness Gate

---

## 1. Purpose

This guide documents the **legitimate, auditable process** for a human contributor to provide a historical counselling artifact to the NEET Compass AI project. It ensures every artifact enters the repository with complete provenance, verified integrity, and no PII leakage.

**This guide does NOT provide instructions for bypassing access controls.**

---

## 2. Where to Obtain Artifacts

### 2.1 MCC (Medical Counselling Committee) — All India Quota

| Artifact | Official URL | Notes |
|----------|-------------|-------|
| Seat Matrix (per round) | `https://mcc.nic.in/archive-ug/` | Archive page lists all years 2021-2025 |
| Allotment Results (per round) | `https://mcc.nic.in/archive-ug/` | Same archive |
| Vacancy Reports | `https://mcc.nic.in/archive-ug/` | Same archive |
| Information Bulletins | `https://mcc.nic.in/archive-ug/` | Same archive |
| Joined/Admitted Lists | `https://mcc.nic.in/archive-ug/` | **PII EXCLUDED** — do not retrieve |

**Live verification (Sprint 3.1A, 2026-08-12)**: Archive page HTTP 200, automated downloads HTTP 403 (bot protection).

### 2.2 Maharashtra (MAHA CET Cell) — State Quota

| Artifact | Official URL | Notes |
|----------|-------------|-------|
| Seat Matrix / Allotments | `https://cetcell.mahacet.org/` | Archive **NOT VERIFIED** per config |

### 2.3 Karnataka (KEA) — State Quota

| Artifact | Official URL | Notes |
|----------|-------------|-------|
| Seat Matrix / Allotments | `https://cetonline.karnataka.gov.in/kea/` | Archive **NOT VERIFIED** per config |

### 2.4 Uttar Pradesh (UPMU/DME UP) — State Quota

| Artifact | Official URL | Notes |
|----------|-------------|-------|
| Seat Matrix / Allotments | `https://upneet.gov.in/` | Archive **NOT VERIFIED** per config; mappings are PLACEHOLDERS |

---

## 3. What Official Source Evidence to Record

For **every artifact**, record the following in the Evidence Manifest:

| Field | Description | Example |
|-------|-------------|---------|
| `source_authority` | Official body name | "Medical Counselling Committee" |
| `source_url` | Exact download URL | "https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.pdf" |
| `source_identifier` | Source ID from `data_sources.yaml` | "mcc_ug_archive" |
| `dataset_type` | seat_matrix / allotments / vacancy / bulletin | "seat_matrix" |
| `counselling_year` | NEET UG counselling year | 2024 |
| `round` | Counselling round | "Round 1" |
| `course` | Course coverage | "MBBS+BDS+NURSING" |
| `quota` | ALL_INDIA / STATE_QUOTA | "ALL_INDIA" |
| `retrieval_method` | "MANUAL_BROWSER" / "AUTOMATED" / "BLOCKED" | "MANUAL_BROWSER" |
| `retrieval_timestamp` | UTC ISO 8601 | "2026-08-15T14:30:00+00:00" |

---

## 4. What NOT to Do When HTTP 403 Occurs

**ABSOLUTELY PROHIBITED:**

- ❌ Do NOT use Selenium, Playwright, or undetected-chromedriver to bypass bot protection
- ❌ Do NOT solve CAPTCHAs programmatically
- ❌ Do NOT rotate proxies/IPs to evade rate limits
- ❌ Do NOT scrape protected government portals
- ❌ Do NOT use unauthorized credentials or cookies
- ❌ Do NOT modify headers to mimic browsers deceptively

**CORRECT ACTION:**

1. Document the HTTP 403 in the Evidence Manifest (`retrieval_status: "AUTOMATED_DOWNLOAD_BLOCKED"`)
2. Record the exact URL that returned 403
3. Document the manual retrieval path (see Section 7)
4. Do NOT commit code that attempts automated bypass

---

## 5. How to Record Automated Access Blocking

When automated download fails with HTTP 403/429:

```yaml
retrieval_method: "AUTOMATED"
retrieval_status: "AUTOMATED_DOWNLOAD_BLOCKED"
http_status: 403
blocking_reason: "Bot protection (confirmed Sprint 3.1A live verification)"
manual_path_documented: true
```

This status is a **valid, honest evidence state** — it does not indicate failure.

---

## 6. How to Preserve the Original File

1. **Save the file exactly as downloaded** — do not rename, convert, or modify
2. **Store in secure local location** — not in the repository
3. **Record the original filename** in `artifact_filename`
4. **Record MIME type** (e.g., `application/pdf`, `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
5. **Record file size in bytes**

---

## 7. How to Calculate SHA-256

**Command (Linux/macOS):**
```bash
sha256sum /path/to/artifact.pdf
```

**Command (Windows PowerShell):**
```powershell
Get-FileHash -Algorithm SHA256 -Path "C:\path\to\artifact.pdf"
```

**Command (Python):**
```python
import hashlib
with open("artifact.pdf", "rb") as f:
    print(hashlib.sha256(f.read()).hexdigest())
```

Record the **full 64-character hex digest** in the manifest field `sha256`.

---

## 8. How to Record Retrieval Time

Use **UTC ISO 8601 format**:

```text
2026-08-15T14:30:00+00:00
```

Generate at the moment of successful download:
```python
from datetime import UTC, datetime
retrieval_timestamp = datetime.now(UTC).isoformat()
```

---

## 9. How to Identify the Counselling Year

The counselling year is the **NEET UG admission year**, printed on the document:

- "NEET UG 2024 Counselling" → `counselling_year: 2024`
- "NEET UG 2023 Round 1 Seat Matrix" → `counselling_year: 2023`

**Do NOT use** the document publication year if different from counselling year.

---

## 10. How to Identify Round / Dataset

| Document Title Keyword | `round` Value | `dataset_type` Value |
|------------------------|---------------|----------------------|
| "Round 1 Seat Matrix" | "Round 1" | "seat_matrix" |
| "Round 2 Allotment Result" | "Round 2" | "allotments" |
| "Round 3 Vacancy" | "Round 3" | "vacancy" |
| "Stray Vacancy" | "Stray Vacancy" | "vacancy" |
| "Information Bulletin" | "All" | "bulletin" |

If the document covers multiple rounds, use `"All"` for round.

---

## 11. How to Perform PII Screening

**Before submitting any artifact**, screen for candidate PII:

### 11.1 Automated Screening (Required)

Run the PII detection script on the raw file:

```python
from etl.contracts.historical.pii_gate import detect_pii

# For CSV/Excel: read column headers
# For PDF: extract text and check for PII patterns
detected = detect_pii(column_headers)
if detected:
    print(f"PII DETECTED: {detected}")
    # DO NOT SUBMIT — see Section 11.3
```

### 11.2 PII Blocklist (Representative)

The system screens for these field patterns (not exhaustive):

- `candidate_name`, `father_name`, `mother_name`, `guardian_name`
- `roll_number`, `application_number`, `registration_number`
- `phone`, `mobile`, `contact_no`, `email`
- `address`, `aadhaar`, `pan`, `passport_number`
- `percentile`, `neet_score`, `air`, `state_rank`
- `photograph`, `signature`, `thumb_impression`
- `application_id`, `form_number`, `user_id`, `login_id`
- `date_of_birth`, `gender`, `caste_certificate_number`

### 11.3 If PII Detected

1. **Do NOT submit the raw file** to the repository
2. Document `pii_status: "PII_DETECTED"` in manifest
3. Record which columns triggered detection
4. The artifact will be classified as `BLOCKED_PII` — it **cannot** enter the canonical modelling boundary
5. Joined/Admitted candidate lists are **always PII_EXCLUDED** by definition

---

## 12. How to Create a Safe Fixture

**Only if the source document is legally distributable** (check copyright/terms):

1. **Extract 10-20 representative rows** (no PII columns)
2. **Save as CSV** with only canonical columns:
   - Seat Matrix: `college_id, course_id, quota_id, category_id, total_seats, effective_year`
   - Allotments: `college_id, course_id, quota_id, category_id, round_id, rank, score, seat_count, effective_year`
3. **Name fixture**: `{source}_{dataset}_{year}_{round}_fixture.csv`
4. **Place in**: `etl/contracts/sources/{authority}/fixtures/`
5. **Document in manifest**: `fixture_exists: true`, `fixture_type: "REAL_SAMPLE"`

**If NOT legally distributable:**
- Create **synthetic fixture** matching schema only
- Name: `{source}_{dataset}_{year}_{round}_SYNTHETIC_fixture.csv`
- Document: `fixture_type: "SYNTHETIC"`
- **Never represent synthetic as real**

**Never commit full raw datasets.**

---

## 13. How to Submit Evidence for Validation

### 13.1 Prepare Submission Package

```
submission/
├── evidence_manifest.yaml      # Complete EvidenceManifest
├── fixture.csv                 # If legally permissible (optional)
├── sha256.txt                  # SHA-256 checksum
└── retrieval_notes.md          # Human-readable retrieval log
```

### 13.2 Validation Checklist (Contributor)

- [ ] Evidence manifest complete (all required fields)
- [ ] SHA-256 matches submitted file
- [ ] PII screening passed (`pii_status: "PII_CLEAR"`)
- [ ] No automated bypass attempted
- [ ] Retrieval method documented honestly
- [ ] Counselling year and round correctly identified
- [ ] Source URL exact and accessible

### 13.3 Validation Checklist (Maintainer)

- [ ] Manifest validates against schema
- [ ] Provenance gate passes (all 10 fields)
- [ ] Artifact integrity verified (checksum matches)
- [ ] Contract compatibility assessed
- [ ] All 15 data quality gates executed
- [ ] Temporal readiness evaluated
- [ ] `modelling_readiness.yaml` updated with evidence

---

## 14. Submission Channels

**Do NOT commit artifacts directly to Git.**

Submit via:
1. **GitHub Issue** with "historical-evidence" label — attach manifest + notes
2. **Secure file transfer** (coordinate with maintainer) for fixtures
3. **Pull Request** touching only:
   - `config/modelling_readiness.yaml` (status updates)
   - `etl/contracts/sources/*/fixtures/` (safe fixtures only)
   - `docs/ml/*.md` (documentation updates)

**Maintainer reviews** all evidence before merging.

---

## 15. Quick Reference: Evidence Status Flow

```
DISCOVERED
    ↓ (source verified)
SOURCE_VERIFIED
    ↓ (manual download)
RETRIEVED
    ↓ (SHA-256 computed)
HASHED
    ↓ (schema documented)
FORMAT_INSPECTED
    ↓ (PII screen clean)
PII_SCREENED
    ↓ (contract compatible)
CONTRACT_CHECKED
    ↓ (parsed successfully)
PARSED
    ↓ (quality gates pass)
VALIDATED
    ↓ (provenance complete)
PROVENANCE_COMPLETE
    ↓ (idempotent)
IDEMPOTENCY_VERIFIED
    ↓ (all gates pass)
QUALITY_GATES_PASSED
    ↓ (temporal ready)
MODELLING_READY
```

**Blocking states** (require manual resolution):
- `BLOCKED_AUTOMATED_DOWNLOAD` → Manual retrieval required
- `BLOCKED_FORMAT_INCOMPATIBLE` → New contract needed
- `BLOCKED_PII_DETECTED` → Cannot enter modelling boundary
- `BLOCKED_CONTRACT_INCOMPATIBLE` → New contract version required
- `BLOCKED_PROVENANCE_INCOMPLETE` → Missing required fields
- `BLOCKED_QUALITY_GATES_FAILED` → Fix data quality issues

---

## 16. Contact

For questions about this procedure, open a GitHub issue with label `historical-evidence`.

**Remember**: SOURCE TRUTH > DATA VOLUME. An artifact with complete, honest evidence is worth more than ten artifacts with gaps.

---

*End of Acquisition Guide*
