# Historical Artifact Handling & Provenance — Sprint 3.7

## Phase 7/8: Evidence Collection and Provenance Standards

---

### Repository Data Rules (from Sprint 3.7 constraints)

- **DO NOT commit restricted/raw source data** if .gitignore or policy prohibits
- **Prefer**: metadata, checksums, source manifests, schema observations, small legally/safely usable fixtures, provenance records
- **Never include PII**: candidate names, roll numbers, application numbers, phone, addresses, emails, other identifiers
- **Minimal fixtures only**: deterministic test fixtures, not full datasets

---

### Evidence Collection Protocol

For each verified historical dataset:

| Evidence Type | Required | Storage |
|---------------|----------|---------|
| **Source URL** | YES | Provenance metadata |
| **Retrieval timestamp** | YES | Provenance metadata |
| **SHA-256 checksum** | YES | Provenance metadata + `source_file_id` |
| **Document title/description** | YES | Provenance metadata |
| **Schema observation** | YES | Contract/adapter documentation |
| **Minimal test fixture** | IF legally permissible | `etl/contracts/sources/{state}/fixtures/` |
| **Retrieval method** | YES | Provenance metadata (manual/automated/blocked) |

---

### Provenance Fields (Reuse Existing Architecture)

From `etl.contracts.canonical.SourceMetadata`:

```python
@dataclass
class SourceMetadata:
    source_id: str                    # e.g., "mcc_ug_archive"
    authority: str                    # e.g., "MCC / DGHS"
    dataset: str                      # e.g., "seat_matrix"
    effective_year: int               # e.g., 2024
    publication_version: str          # e.g., "Round 1"
    contract_version: str             # e.g., "1.1.0"
    retrieval_timestamp: str          # UTC ISO format
    source_file_id: str               # Deterministic: {source_id}_{dataset}_{year}_{checksum[:12]}
    file_checksum: str                # SHA-256 hex digest
    parser_version: str               # e.g., "mcc_etl_v1"
    source_url: str | None            # Exact download URL
```

---

### Historical Artifact Status Codes

| Code | Meaning | Repository Action |
|------|---------|-------------------|
| `VERIFIED` | Downloaded, checksummed, schema-verified | Full provenance + minimal fixture (if legal) |
| `SOURCE_URL_VERIFIED` | URL confirmed accessible, not downloaded | Provenance with URL, no checksum |
| `CHECKSUM_VERIFIED` | Checksum known (from manual download), not in repo | Provenance with checksum, no fixture |
| `FORMAT_VERIFIED` | Schema confirmed, data not ingested | Contract/adapter documentation |
| `AUTOMATED_DOWNLOAD_BLOCKED` | HTTP 403/429 on automated retrieval | Document blocking, manual path if available |
| `ARCHIVE_INACCESSIBLE` | Archive page not found/blocked | Document failure |
| `MAPPING_NOT_VERIFIED` | Placeholder mappings (UP) | Explicit in contract/readiness |

---

### PII Protection Checklist

For ANY historical artifact (seat matrix, allotment, vacancy, joined list):

- [ ] No candidate names
- [ ] No roll numbers / application numbers
- [ ] No phone numbers
- [ ] No email addresses
- [ ] No physical addresses
- [ ] No guardian/parent names
- [ ] No caste certificate numbers
- [ ] No Aadhaar numbers
- [ ] No NEET percentile/score (if linked to candidate)
- [ ] No photograph/signature data

**Joined/Admitted Lists**: EXCLUDED from modelling (PII by definition). Documented as `PII_EXCLUDED`.

---

### Fixture Policy for Historical Data

| Scenario | Fixture Action |
|----------|----------------|
| Real source document legally distributable | Commit minimal representative sample (10-20 rows) |
| Real source document NOT legally distributable | Commit synthetic fixture matching schema ONLY; document `SYNTHETIC_FIXTURE` |
| Source document inaccessible | No fixture; document `NO_FIXTURE` |
| PII-containing document | EXCLUDE; document `PII_EXCLUDED` |

**Never**: Commit full raw datasets. Never represent synthetic as real.

---

### Provenance for Sprint 3.7 Verified Artifacts

**Currently Verified (from Sprint 3.6)**:
- MCC 2025 seat matrix + allotments (full provenance in contracts/adapters)
- Maharashtra 2026 fixtures (provenance via test fixtures)
- Karnataka 2026 seat matrix fixture (provenance via test fixtures)
- UP 2026 seat matrix fixture (provenance via test fixtures)

**Target for Sprint 3.7** (if manual retrieval succeeds):
- MCC 2021-2024 seat matrix + allotments (with provenance)
- State historical data (if archives accessible)

**If manual retrieval blocked**: Document `AUTOMATED_DOWNLOAD_BLOCKED` / `MANUAL_RETRIEVAL_REQUIRED` with exact URLs and retrieval instructions.