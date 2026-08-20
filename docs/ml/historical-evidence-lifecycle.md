# Historical Evidence Lifecycle — Sprint 3.9

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 3.9 — Historical Evidence Acquisition & Data Readiness Gate

---

## 1. Overview

This document defines the **formal lifecycle** for a historical source artifact in the NEET Compass AI project. Every artifact must progress through defined stages, with **evidence required at each transition**. A document existing on an official website does NOT automatically move through the lifecycle.

---

## 2. Lifecycle Stages

### 2.1 Stage Definitions

| Stage | Code | Description | Evidence Required |
|-------|------|-------------|-------------------|
| **0. Discovered** | `DISCOVERED` | Source mentioned in config/research | Config entry or research doc |
| **1. Source Verified** | `SOURCE_VERIFIED` | Official URL accessible (HTTP 200) | Live verification log |
| **2. Retrieved** | `RETRIEVED` | File successfully downloaded | Retrieval timestamp, method, HTTP 200 |
| **3. Hashed** | `HASHED` | SHA-256 computed and recorded | Checksum hex digest |
| **4. Format Inspected** | `FORMAT_INSPECTED` | Column headers/schema documented | Schema observation record |
| **5. PII Screened** | `PII_SCREENED` | PII blocklist applied | PII status (CLEAR/DETECTED/EXCLUDED) |
| **6. Contract Checked** | `CONTRACT_CHECKED` | Compatibility classified | Compatibility classification |
| **7. Parsed** | `PARSED` | Canonical records produced | Adapter output, validation results |
| **8. Validated** | `VALIDATED` | All 15 quality gates executed | Gate results, classification |
| **9. Provenance Complete** | `PROVENANCE_COMPLETE` | All 10 provenance fields present | Complete SourceMetadata |
| **10. Idempotency Verified** | `IDEMPOTENCY_VERIFIED` | Re-ingestion produces identical results | Checksum short-circuit test |
| **11. Quality Gates Passed** | `QUALITY_GATES_PASSED` | Final classification assigned | READY / READY_WITH_LIMITATIONS |
| **12. Modelling Ready** | `MODELLING_READY` | Temporal readiness satisfied | Temporal gate passed, registry updated |

### 2.2 Blocking States

| State | Code | Resolution Required |
|-------|------|---------------------|
| Automated Download Blocked | `BLOCKED_AUTOMATED_DOWNLOAD` | Manual retrieval + documentation |
| Format Incompatible | `BLOCKED_FORMAT_INCOMPATIBLE` | New contract version |
| PII Detected | `BLOCKED_PII_DETECTED` | Exclude from modelling boundary |
| Contract Incompatible | `BLOCKED_CONTRACT_INCOMPATIBLE` | New contract version (explicit) |
| Provenance Incomplete | `BLOCKED_PROVENANCE_INCOMPLETE` | Complete missing fields |
| Quality Gates Failed | `BLOCKED_QUALITY_GATES_FAILED` | Fix data quality issues |

---

## 3. Valid Transitions

Every transition **MUST** have documented evidence. Invalid transitions are rejected.

```mermaid
DISCOVERED → SOURCE_VERIFIED → RETRIEVED → HASHED → FORMAT_INSPECTED
    ↓              ↓              ↓           ↓            ↓
BLOCKED_       BLOCKED_       BLOCKED_    BLOCKED_     BLOCKED_
DOWNLOAD       DOWNLOAD       DOWNLOAD    DOWNLOAD     DOWNLOAD
```

**Key Principle**: `PORTAL_EXISTS` ≠ `DOCUMENT_RETRIEVED` ≠ `FORMAT_VERIFIED` ≠ `CONTRACT_COMPATIBLE` ≠ `MODELLING_READY`

---

## 4. Evidence Manifest

Each artifact carries a machine-readable **Evidence Manifest** capturing:

### 4.1 Required Fields

| Category | Fields |
|----------|--------|
| **Source** | authority, URL, identifier, dataset_type, year, round, course, quota |
| **Retrieval** | method, timestamp, status, HTTP status |
| **Artifact** | filename, MIME type, size, SHA-256, source_file_id |
| **Contract** | contract_version, parser_version, format_status |
| **PII** | pii_status |
| **Validation** | validation_status, modelling_readiness |
| **Limitations** | limitations[], notes |

### 4.2 Reuse of Existing Infrastructure

The manifest **reuses** the existing 10-field provenance taxonomy from `SourceMetadata`:
- `source_id`, `authority`, `dataset`, `effective_year`, `publication_version`
- `contract_version`, `retrieval_timestamp`, `source_file_id`, `file_checksum`
- `parser_version`, `source_url`

No duplicate provenance system is created.

---

## 5. Evidence Status Taxonomy

### 5.1 Status Categories

**Source Discovery**
- `SOURCE_CLAIMED` — In config, not verified
- `SOURCE_VERIFIED` — URL accessible (HTTP 200)

**Retrieval**
- `ARTIFACT_UNAVAILABLE` — Not found on portal
- `AUTOMATED_DOWNLOAD_BLOCKED` — HTTP 403/429
- `MANUALLY_RETRIEVED` — Human downloaded via browser
- `RETRIEVED` — Successfully obtained

**Format**
- `FORMAT_VERIFIED` — Matches contract
- `FORMAT_UNKNOWN` — Not examined
- `FORMAT_MISMATCH` — Differs from contract

**PII**
- `PII_DETECTED` — Candidate identifiers found
- `PII_CLEAR` — No PII in canonical path
- `PII_EXCLUDED` — Entire document excluded

**Contract**
- `CONTRACT_COMPATIBLE` — Reuses existing contract
- `CONTRACT_COMPATIBLE_WITH_LIMITATIONS` — Minor differences documented
- `CONTRACT_INCOMPATIBLE` — Requires new contract
- `CONTRACT_UNKNOWN` — No contract for this year

**Validation**
- `VALIDATED` — Gates pass
- `VALIDATED_WITH_LIMITATIONS` — Non-critical gates documented
- `NOT_VALIDATED` — Gates not run/failed

**Modelling Readiness**
- `MODELLING_READY` — All gates pass, temporal ready
- `READY_WITH_LIMITATIONS` — Critical gates pass, non-critical documented
- `NOT_READY` — Any critical gate fails

### 5.2 Legacy Status Mapping (Sprint 3.7/3.8 Compatibility)

| Legacy Status | Maps To |
|---------------|---------|
| `VERIFIED` | `VERIFIED` |
| `SOURCE_URL_VERIFIED` | `SOURCE_URL_VERIFIED` |
| `CHECKSUM_VERIFIED` | `CHECKSUM_VERIFIED` |
| `FORMAT_VERIFIED` | `FORMAT_VERIFIED` |
| `AUTOMATED_DOWNLOAD_BLOCKED` | `AUTOMATED_DOWNLOAD_BLOCKED` |
| `ARCHIVE_INACCESSIBLE` | `ARCHIVE_INACCESSIBLE` |
| `MAPPING_NOT_VERIFIED` | `MAPPING_NOT_VERIFIED` |
| `NOT_VERIFIED` | `NOT_VERIFIED` |
| `PARTIALLY_VERIFIED` | `PARTIALLY_VERIFIED` |

---

## 6. Gates (Deterministic, Non-Overrideable)

### 6.1 Provenance Gate (10 Fields)

**Required**: All 10 `SourceMetadata` fields present and non-empty.

### 6.2 PII Gate (Fail-Closed)

**Blocklist**: 50+ candidate identifier patterns. Any detection → `NOT_READY`.

**Applies to**: Canonical modelling boundary only. Source evidence preserved.

### 6.3 Artifact Integrity Gate

**Checks**:
- SHA-256 stability (same bytes → same hash)
- Identity determinism (same bytes → same source_file_id)
- Modified bytes → different identity
- Missing checksum → `NOT_READY`
- Invalid source identity → `NOT_READY`
- Inconsistent metadata → `NOT_READY`

### 6.4 Contract Compatibility Gate

**Classification**: `COMPATIBLE` / `COMPATIBLE_WITH_LIMITATIONS` / `INCOMPATIBLE` / `UNKNOWN`

**Rules**:
- `UNKNOWN` → `NOT_READY` (never modelling-ready)
- `INCOMPATIBLE` → `NOT_READY` (no forced adapters)
- `COMPATIBLE_WITH_LIMITATIONS` → `READY_WITH_LIMITATIONS`
- `COMPATIBLE` + format verified → `READY`

### 6.5 Data Quality Gates (15 from Sprint 3.6)

**Integrated, not duplicated**. Run via `QualityGateRunner`.

**Classification**:
- `READY`: All 15 gates pass
- `READY_WITH_LIMITATIONS`: Gates 1-10 pass, 11/15 documented
- `NOT_READY`: Any critical gate (1-10, 12-15) fails

**Gate 13 (Source Verification)**: `NOT_VERIFIED` sources **NEVER** `READY`.

### 6.6 Temporal Readiness Gate

**Requirements**:
- Minimum 3 verified modelling-ready years
- Chronologically ordered
- Train/validate/test split possible
- No gaps in verified sequence (preferred)

**Current State**: 1 verified year (MCC 2025) → **BLOCKED**

---

## 7. Promotion Workflow

### 7.1 Valid Promotions (No Skipping)

```
NOT_VERIFIED → VERIFIED → VALIDATED → READY_WITH_LIMITATIONS → READY
```

**Forbidden**: `NOT_VERIFIED` → `READY` (direct jump)

**Forbidden**: `READY_WITH_LIMITATIONS` → `READY` (silent upgrade)

### 7.2 Promotion Requirements

| From → To | Required Evidence |
|-----------|-------------------|
| NOT_VERIFIED → VERIFIED | Source authority + URL verified |
| VERIFIED → VALIDATED | Artifact retrieved, hashed, format inspected, PII screened |
| VALIDATED → READY_WITH_LIMITATIONS | Contract compatible, parsed, 15 gates executed |
| READY_WITH_LIMITATIONS → READY | Provenance complete, idempotent, limitations resolved, temporal ready |

---

## 8. Safe Artifact Boundary

### 8.1 Allowed in Git

- Deterministic synthetic fixtures
- Minimal non-PII representative fixtures (≤20 rows)
- Metadata manifests (YAML/JSON)
- Checksums (SHA-256)
- Schema descriptions
- Parser tests
- Source documentation

### 8.2 Prohibited in Git

- Candidate-level allotment records
- Raw government datasets containing PII
- Credentials, cookies, tokens
- Restricted documents
- Database dumps
- Model artifacts

---

## 9. Current Modelling Coverage (Sprint 3.9 Baseline)

| Authority | Verified Years | Modelling-Ready | Status |
|-----------|---------------|-----------------|--------|
| **MCC** | 2025 | 2025 | ✅ READY |
| **MCC** | 2021-2024 | — | ❌ NOT_READY (AUTOMATED_DOWNLOAD_BLOCKED) |
| **Maharashtra** | 2026 (fixture) | — | ❌ NOT_READY (archive NOT_VERIFIED) |
| **Karnataka** | 2026 (fixture) | — | ❌ NOT_READY (archive NOT_VERIFIED) |
| **Uttar Pradesh** | 2026 (fixture) | — | ❌ NOT_READY (placeholder mappings) |

**Temporal Validation**: **BLOCKED** (1 verified year, need ≥3)

---

## 10. Integration Points

| Component | Location | Purpose |
|-----------|----------|---------|
| Lifecycle Stages | `etl/contracts/historical/lifecycle.py` | Stage definitions, transitions |
| Evidence Manifest | `etl/contracts/historical/manifest.py` | Machine-readable evidence |
| Status Taxonomy | `etl/contracts/historical/status.py` | Status codes, helpers |
| Provenance Gate | `etl/contracts/historical/provenance_gate.py` | 10-field validation |
| PII Gate | `etl/contracts/historical/pii_gate.py` | PII detection |
| Artifact Integrity | `etl/contracts/historical/artifact_integrity.py` | Checksum verification |
| Contract Gate | `etl/contracts/historical/contract_gate.py` | Compatibility classification |
| Quality Gate Integration | `etl/contracts/historical/quality_gate_integration.py` | Aggregated gate runner |
| Temporal Gate | `etl/contracts/historical/temporal_gate.py` | Temporal readiness |
| Promotion Workflow | `etl/contracts/historical/promotion.py` | Stage promotion logic |

---

## 11. Compliance Checklist

- [ ] Evidence lifecycle is deterministic
- [ ] Evidence statuses clearly defined (no duplicates)
- [ ] Acquisition process documented
- [ ] No access-control bypass introduced
- [ ] Artifact integrity validated
- [ ] SHA-256 identity deterministic
- [ ] Provenance gate works (10 fields)
- [ ] PII gate works (fail-closed)
- [ ] Contract compatibility gate works
- [ ] Existing 15 data-quality gates intact
- [ ] Temporal readiness gate works
- [ ] Unverified datasets cannot become READY
- [ ] Insufficient history blocks modelling
- [ ] MCC 2025 remains READY
- [ ] No unsupported years promoted
- [ ] Deterministic tests pass
- [ ] Existing ETL tests pass
- [ ] Ruff changed scope passes
- [ ] Format check passes
- [ ] No new mypy errors
- [ ] Migrations 0001/0002 untouched
- [ ] No ML implemented
- [ ] No prediction implemented
- [ ] No new state added
- [ ] No PII/secrets committed
- [ ] Documentation complete

---

*End of Lifecycle Specification*
