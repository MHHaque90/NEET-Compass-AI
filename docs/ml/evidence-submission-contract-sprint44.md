# Evidence Submission Contract — Sprint 4.4

**Classification:** CONTRACT SPECIFICATION  
**Version:** 1.0  
**Status:** AUTHORIZED FOR USE  
**Sprint:** 4.4 — Historical Evidence Acquisition Path & Readiness Activation

---

## 1. Purpose

This contract defines the **deterministic lifecycle** for submitting a historical artifact into the NEET Compass AI validation pipeline. It makes it **impossible to confuse**:

> **"Artifact exists"** ≠ **"Artifact is modelling-ready"**

Every transition requires documented evidence. Every failure fails closed.

---

## 2. Submission Lifecycle States

Using existing repository terminology from `etl/contracts/historical/status.py` and `etl/contracts/historical/lifecycle.py`:

```
UNSUBMITTED
    │  (artifact acquired, manifest prepared)
    ▼
RECEIVED
    │  (manifest validates, checksum matches)
    ▼
INTEGRITY_CHECKED
    │  (SHA-256 verified, source_file_id generated)
    ▼
PII_CHECKED
    │  (column headers screened, zero candidate PII)
    ▼
SOURCE_VERIFIED
    │  (source_url accessible, authority confirmed)
    ▼
CONTRACT_CHECKED
    │  (contract_version identified, compatibility classified)
    ▼
FORMAT_CHECKED
    │  (column headers/schema documented, format_status assigned)
    ▼
PROVENANCE_COMPLETE
    │  (all 10 SourceMetadata fields present and non-empty)
    ▼
QUALITY_CHECKED
    │  (all 15 Sprint 3.6 data quality gates executed)
    ▼
READINESS_CLASSIFIED
    │  (READY / READY_WITH_LIMITATIONS / NOT_READY assigned)
    ▼
[TEMPORAL_READY]  ← Separate gate: ≥3 verified modelling-ready years
    │
    ▼
[TARGET_READY]    ← Separate gate: TargetEngine returns READY
    │
    ▼
[TRAINING_ELIGIBLE]  ← Separate gate: TrainingGuard allows
```

---

## 3. State Definitions & Evidence Requirements

### 3.1 UNSUBMITTED
**Definition:** Artifact acquired by human operator, not yet entered into validation pipeline.

**Entry Criteria:** None (initial state)

**Required Evidence for Next State:**
- Complete `EvidenceManifest` with all `REQUIRED_MANIFEST_FIELDS` (23 fields)
- Artifact file accessible at local path
- SHA-256 computed and recorded in manifest

**Failure Mode:** `manifest_validation_failed` → missing fields documented

---

### 3.2 RECEIVED
**Definition:** Manifest submitted, basic validation passed.

**Entry Criteria:**
- `validate_manifest(manifest)` returns `(True, [])`
- `artifact_filename` exists at submission path
- `sha256` in manifest matches actual file checksum

**Required Evidence for Next State:**
- `ArtifactIntegrity.verify(artifact_bytes, expected_checksum=manifest.sha256)` → `passed=True`

**Failure Mode:** `integrity_check_failed` → checksum mismatch or missing expected checksum

---

### 3.3 INTEGRITY_CHECKED
**Definition:** Artifact integrity cryptographically verified.

**Entry Criteria:**
- `ArtifactIntegrityResult.passed == True`
- `source_file_id` generated deterministically: `{source_id}_{dataset}_{year}_{checksum[:12]}`

**Required Evidence for Next State:**
- `PIIGate.validate(column_headers)` → `passed=True` (zero detections)

**Failure Mode:** `pii_detected` → `PIIGateResult.detected_fields` non-empty → `BLOCKED_PII`

---

### 3.4 PII_CHECKED
**Definition:** Column headers screened — no candidate identifiers in canonical path.

**Entry Criteria:**
- `PIIGateResult.passed == True`
- `pii_status == "PII_CLEAR"`

**Required Evidence for Next State:**
- Source authority officially confirmed
- `source_url` returns HTTP 200 (verified separately)
- `source_id` registered in `data_sources.yaml`

**Failure Mode:** `source_unverified` → `SOURCE_CLAIMED` or `ARCHIVE_INACCESSIBLE`

---

### 3.5 SOURCE_VERIFIED
**Definition:** Authoritative source confirmed accessible.

**Entry Criteria:**
- Official URL accessible (HTTP 200)
- Authority name matches registered source
- `source_id` exists in `data_sources.yaml`

**Required Evidence for Next State:**
- `contract_version` identified (e.g., "1.1.0")
- `ContractGate.validate(compat, format_verified, limitations)` → `passed=True`
- Compatibility ∈ {`COMPATIBLE`, `COMPATIBLE_WITH_LIMITATIONS`}

**Failure Mode:** `contract_unknown` (no contract_version) → `CONTRACT_UNKNOWN` → `BLOCKED_CONTRACT_INCOMPATIBLE`  
**Failure Mode:** `contract_incompatible` → `CONTRACT_INCOMPATIBLE` → `BLOCKED_CONTRACT_INCOMPATIBLE`

---

### 3.6 CONTRACT_CHECKED
**Definition:** Contract compatibility classified with evidence.

**Entry Criteria:**
- `ContractGateResult.passed == True`
- `compatibility` ∈ {`COMPATIBLE`, `COMPATIBLE_WITH_LIMITATIONS`}
- If `COMPATIBLE` → `format_verified == True` (mandatory per `ContractGate.require_verified_format`)

**Required Evidence for Next State:**
- Column headers/schema documented via `_read_artifact_headers()`
- `format_status` assigned: `FORMAT_VERIFIED` / `FORMAT_UNKNOWN` / `FORMAT_MISMATCH`
- MIME type, file_size recorded

**Failure Mode:** `format_mismatch` → `FORMAT_MISMATCH` → `BLOCKED_FORMAT_INCOMPATIBLE`  
**Failure Mode:** `format_unknown` → `FORMAT_UNKNOWN` (cannot proceed to READY without verification)

---

### 3.7 FORMAT_CHECKED
**Definition:** Artifact structure inspected and documented.

**Entry Criteria:**
- `format_status` ∈ {`FORMAT_VERIFIED`, `FORMAT_UNKNOWN`, `FORMAT_MISMATCH`}
- Headers, data types, sample rows documented

**Required Evidence for Next State:**
- `ProvenanceGate.validate(SourceMetadata)` → `passed=True`
- All 10 provenance fields present and non-empty

**Failure Mode:** `provenance_incomplete` → `ProvenanceGateResult.missing_fields` non-empty → `BLOCKED_PROVENANCE_INCOMPLETE`

---

### 3.8 PROVENANCE_COMPLETE
**Definition:** Complete provenance chain recorded.

**Entry Criteria:**
- `ProvenanceGateResult.passed == True`
- All 10 fields: `source_id`, `authority`, `dataset`, `effective_year`, `publication_version`, `contract_version`, `retrieval_timestamp`, `source_file_id`, `file_checksum`, `parser_version`, `source_url`

**Required Evidence for Next State:**
- `HistoricalQualityGateRunner.run()` → all critical quality gates pass
- `data_quality_results` dict with 15 gate results
- `temporal_safety == True` (for final READY)

**Failure Mode:** `quality_gates_failed` → specific gate failures documented → `BLOCKED_QUALITY_GATES_FAILED`

---

### 3.9 QUALITY_CHECKED
**Definition:** All data quality gates executed with results.

**Entry Criteria:**
- `HistoricalQualityResult.classification` ∈ {`READY`, `READY_WITH_LIMITATIONS`, `NOT_READY`}
- `readiness` boolean reflects classification
- `evidence_status` assigned per classification
- `lifecycle_stage` assigned per classification

**Required Evidence for Next State:**
- Maintainer review confirms evidence completeness
- `modelling_readiness.yaml` updated with evidence-based classification

**Failure Mode:** `classification_not_ready` → remains `NOT_READY` (no promotion)

---

### 3.10 READINESS_CLASSIFIED
**Definition:** Final modelling readiness assigned for this dataset/year.

**Entry Criteria:**
- `modelling_readiness` ∈ {`READY`, `READY_WITH_LIMITATIONS`, `NOT_READY`}
- Registry entry complete in `config/modelling_readiness.yaml`

**Terminal States for Historical Artifacts:**
- `READY` → Eligible for temporal validation
- `READY_WITH_LIMITATIONS` → Eligible for temporal validation (with documented caveats)
- `NOT_READY` → Blocked (see `blocking_reasons`)

---

## 4. Separate Readiness Gates (Post-Classification)

These are **NOT part of artifact submission** but are required for training:

### 4.1 TEMPORAL_READY
- **Gate:** `TemporalReadinessGate.validate(modelling_ready_years)`
- **Requirement:** ≥3 verified modelling-ready years across authorities, chronological, splittable
- **Current State:** BLOCKED (1 year: MCC 2025)

### 4.2 TARGET_READY
- **Gate:** `TargetEngine.get_first_modelling_target()` != `"NO_TARGET_READY"`
- **Requirement:** At least one target definition has `readiness_status == READY`
- **Current State:** NO_TARGET_READY (all 5 targets blocked)

### 4.3 TRAINING_ELIGIBLE
- **Gate:** `TrainingGuard.check_training_allowed()` → `allowed == True`
- **Requirement:** Temporal + Target + Years + Leakage + Quality + Provenance all pass
- **Current State:** TRAINING_BLOCKED

---

## 5. Failure Contract — Every Failure Fails Closed

| Failure State | Trigger | Recovery | Can Reach READY? |
|---------------|---------|----------|------------------|
| `INVALID_MANIFEST` | Missing required fields | Complete manifest | Only after fix |
| `ARTIFACT_INTEGRITY_FAILED` | Checksum mismatch / missing expected | Re-download, recompute | Only after fix |
| `PII_DETECTED` | Candidate identifiers in headers | Cannot proceed — PII_EXCLUDED | NEVER for this artifact |
| `SOURCE_UNVERIFIED` | URL not accessible / authority unconfirmed | Verify source | Only after fix |
| `CONTRACT_UNKNOWN` | No contract_version provided | Inspect format, create contract | Only after fix |
| `CONTRACT_INCOMPATIBLE` | Format differs from contract | Create new contract version | Only after new contract |
| `FORMAT_MISMATCH` | Structure incompatible | Document differences | Only after new contract |
| `FORMAT_UNKNOWN` | No source document examined | Examine actual document | Only after inspection |
| `PROVENANCE_INCOMPLETE` | Missing any of 10 fields | Complete all fields | Only after fix |
| `QUALITY_GATES_FAILED` | Any critical gate fails | Fix data quality issues | Only after fix |
| `TEMPORAL_BLOCKED` | <3 verified years | Acquire more verified years | Only after ≥3 years |
| `TARGET_BLOCKED` | No target READY | Meet target requirements | Only after target READY |
| `TRAINING_BLOCKED` | Any guard check fails | Resolve all block reasons | Only after all pass |

---

## 6. Explicit Non-Promotion Rules

**The following CANNOT cause promotion:**

| Non-Promoting Factor | Reason |
|---------------------|--------|
| Artifact exists locally | Existence ≠ evidence |
| Checksum computed | Integrity only, not quality |
| PII screening passed | Necessary but not sufficient |
| Source URL accessible | Verification only, not content |
| Contract version matches | Compatibility ≠ quality gates |
| Format inspected | Inspection ≠ validation |
| Provenance complete | Provenance ≠ data quality |
| Single quality gate passes | All critical gates required |
| 1 verified year exists | Temporal needs ≥3 |
| 2 verified years exist | Temporal needs ≥3 |
| Fixture exists | Fixture ≠ real data |
| Manual retrieval done | Retrieval ≠ verification |
| Human says "looks good" | Subjective ≠ evidence |

**Only COMPLETE EVIDENCE CHAIN promotes.**

---

## 7. Validation Functions (Existing Implementation)

| Contract Stage | Validation Function | Location |
|----------------|---------------------|----------|
| Manifest | `validate_manifest(manifest)` | `etl/contracts/historical/manifest.py:274` |
| Integrity | `ArtifactIntegrity.verify(data, expected_checksum)` | `etl/contracts/historical/artifact_integrity.py:49` |
| PII | `PIIGate.validate(headers)` | `etl/contracts/historical/pii_gate.py:203` |
| Source/Provenance | `ProvenanceGate.validate(SourceMetadata)` | `etl/contracts/historical/provenance_gate.py:56` |
| Contract | `ContractGate.validate(compat, format_verified, limitations)` | `etl/contracts/historical/contract_gate.py:68` |
| Format | `HumanArtifactIngestor._read_artifact_headers(path)` | `etl/contracts/historical/human_ingestion.py:116` |
| Quality | `HistoricalQualityGateRunner.run(...)` | `etl/contracts/historical/quality_gate_integration.py:90` |
| Temporal | `TemporalReadinessGate.validate(modelling_ready_years)` | `etl/contracts/historical/temporal_gate.py:55` |
| Target | `TargetEngine.get_target_readiness(name)` | `modelling/targets/engine.py:254` |
| Training | `TrainingGuard.check_training_allowed(...)` | `modelling/training/guard.py:66` |

---

## 8. Submission Package Contract

**Required Files:**
```
submission/
├── evidence_manifest.yaml    # EvidenceManifest.to_dict() serialized
├── fixture.csv               # Optional: 10-20 rows, no PII, legally distributable
├── sha256.txt                # Single line: 64-char hex digest
└── retrieval_notes.md        # Human-readable: who, when, where, how, observations
```

**Manifest Must Validate:**
```python
from etl.contracts.historical.manifest import validate_manifest, EvidenceManifest
manifest = EvidenceManifest.from_dict(yaml_data)
is_valid, missing = validate_manifest(manifest)
assert is_valid, f"Missing fields: {missing}"
```

**Checksum Must Match:**
```python
from etl.contracts.historical.artifact_integrity import verify_artifact_integrity
with open(artifact_path, "rb") as f:
    data = f.read()
result = verify_artifact_integrity(data, source_id, dataset, year, expected_checksum=manifest.sha256)
assert result.passed, "Checksum mismatch"
```

---

## 9. Maintainer Review Contract

**Maintainer MUST verify before merging:**

- [ ] `validate_manifest()` passes
- [ ] `ArtifactIntegrity.verify()` passes with expected checksum
- [ ] `PIIGate.validate()` passes (zero detections)
- [ ] Source URL accessible (HTTP 200) — verified independently
- [ ] `ContractGate.validate()` passes with `COMPATIBLE` or `COMPATIBLE_WITH_LIMITATIONS`
- [ ] `format_status` assigned based on actual document inspection
- [ ] `ProvenanceGate.validate()` passes (10 fields)
- [ ] `HistoricalQualityGateRunner.run()` produces classification with evidence
- [ ] `modelling_readiness.yaml` updated with **evidence-based** status
- [ ] No automated bypass attempted (HTTP 403 documented honestly)
- [ ] No PII in any committed file
- [ ] No secrets in any committed file

**If ANY check fails → REJECT submission. Do not merge.**

---

## 10. Version Compatibility

This contract uses **existing repository types and enums**:

- `EvidenceStatus` from `etl/contracts/historical/status.py`
- `EvidenceLifecycleStage` from `etl/contracts/historical/lifecycle.py`
- `ContractCompatibility` from `etl/contracts/historical/contract_gate.py`
- `PromotionStage` from `etl/contracts/historical/promotion.py`
- `EvidenceManifest` from `etl/contracts/historical/manifest.py`

**No new statuses introduced.** Contract maps to existing taxonomy.

---

*End of Evidence Submission Contract — Sprint 4.4*