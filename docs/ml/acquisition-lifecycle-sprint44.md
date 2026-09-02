# Historical Evidence Acquisition Lifecycle — Sprint 4.4

**Classification:** ARCHITECTURE REFERENCE  
**Version:** 1.0  
**Status:** AUTHORIZED FOR USE  
**Sprint:** 4.4 — Historical Evidence Acquisition Path & Readiness Activation

---

## 1. Purpose

This document provides the **complete end-to-end chain** for historical evidence acquisition, from authoritative source to training eligibility. It maps every stage to its implementation, inputs, outputs, gate conditions, and failure states.

**Critical Distinctions (NOT interchangeable):**

| State | Meaning |
|-------|---------|
| **ARTIFACT EXISTS** | File downloaded, checksum computed |
| **ARTIFACT VERIFIED** | Integrity + PII + provenance + contract checked |
| **DATASET MODELLING-READY** | All 15 quality gates pass, provenance complete, idempotent |
| **TEMPORALLY ELIGIBLE** | ≥3 verified modelling-ready years, chronological, splittable |
| **TARGET-ELIGIBLE** | TargetEngine returns READY for at least one target |
| **TRAINING-ELIGIBLE** | TrainingGuard allows training (all gates pass) |

---

## 2. Complete Lifecycle Chain

```
AUTHORITATIVE SOURCE
         │
         ▼
LEGITIMATE HUMAN ACQUISITION
         │
         ▼
RAW ARTIFACT INTAKE
         │
         ▼
INTEGRITY / CHECKSUM (ArtifactIntegrity)
         │
         ▼
PII VALIDATION (PIIGate)
         │
         ▼
SOURCE VERIFICATION (ProvenanceGate - source_url accessible)
         │
         ▼
CONTRACT COMPATIBILITY (ContractGate)
         │
         ▼
FORMAT / SCHEMA VALIDATION (HumanArtifactIngestor._read_artifact_headers)
         │
         ▼
PROVENANCE COMPLETENESS (ProvenanceGate - 10 fields)
         │
         ▼
QUALITY GATES (HistoricalQualityGateRunner - 15 gates)
         │
         ▼
READINESS CLASSIFICATION (READY / READY_WITH_LIMITATIONS / NOT_READY)
         │
         ▼
TEMPORAL VALIDATION (TemporalReadinessGate - ≥3 years)
         │
         ▼
TARGET VALIDATION (TargetEngine - NO_TARGET_READY vs READY)
         │
         ▼
TRAINING ELIGIBILITY (TrainingGuard - all gates pass)
```

---

## 3. Stage-by-Stage Implementation Map

### Stage 0: Authoritative Source Discovery

| Aspect | Detail |
|--------|--------|
| **Implementation** | `config/data_sources.yaml` + `docs/ml/*-historical-research.md` |
| **Responsible** | `DataSourceRegistry` (ETL) |
| **Input** | Official authority name, base URL, claimed year support |
| **Output** | Registered `source_id` with `status: "ACTIVE"` |
| **Gate Condition** | Authority officially exists; URL returns HTTP 200 for portal |
| **Failure State** | `ARCHIVE_INACCESSIBLE` / `SOURCE_CLAIMED` (if not verified) |
| **Fail Closed** | YES — unverified source cannot proceed |

### Stage 1: Legitimate Human Acquisition

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/human_ingestion.py` → `HumanArtifactIngestor.ingest()` |
| **Responsible** | Human operator (manual browser) |
| **Input** | `IngestionInput`: artifact_path, source_url, authority, year, dataset_type, round, retrieval_timestamp, provided_sha256 |
| **Output** | Raw artifact bytes saved locally (NOT in repo) |
| **Gate Condition** | File exists at path; HTTP 200 on download; retrieval_timestamp recorded |
| **Failure State** | `AUTOMATED_DOWNLOAD_BLOCKED` (HTTP 403) / `ARTIFACT_UNAVAILABLE` (404) |
| **Fail Closed** | YES — HTTP 403 does NOT permit bypass; manual retrieval only if legitimately permitted |

### Stage 2: Raw Artifact Intake & Integrity

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/artifact_integrity.py` → `ArtifactIntegrity.verify()` |
| **Responsible** | `HumanArtifactIngestor.ingest()` (automatic) |
| **Input** | Artifact bytes, optional expected_checksum |
| **Output** | `ArtifactIntegrityResult`: passed, checksum, source_file_id, details |
| **Gate Condition** | SHA-256 computed; if expected_checksum provided → must match |
| **Failure State** | `ARTIFACT_INTEGRITY_FAILED` (checksum mismatch or missing expected checksum) |
| **Fail Closed** | YES — missing expected_checksum → `passed=False` (see `verify_artifact_integrity()`) |

**Key Code:** `artifact_integrity.py:140-147` — missing expected_checksum forces `passed=False`

### Stage 3: PII Validation

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/pii_gate.py` → `PIIGate.validate()` |
| **Responsible** | `HumanArtifactIngestor.ingest()` (automatic) |
| **Input** | Column headers from artifact (CSV/XLSX) |
| **Output** | `PIIGateResult`: passed, detected_fields, scanned_fields, details |
| **Gate Condition** | Zero candidate PII fields detected in column headers |
| **Failure State** | `PII_DETECTED` / `PII_EXCLUDED` (joined lists) |
| **Fail Closed** | YES — any detection → `passed=False` → `BLOCKED_PII` lifecycle |

**Key Code:** `pii_gate.py:203-225` — conservative fuzzy matching on patterns

### Stage 4: Source Verification

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/provenance_gate.py` → `ProvenanceGate.validate()` |
| **Responsible** | `HumanArtifactIngestor.ingest()` (automatic via SourceMetadata) |
| **Input** | `SourceMetadata` with `source_url` |
| **Output** | `ProvenanceGateResult`: passed, missing_fields, present_fields |
| **Gate Condition** | Source URL accessible (HTTP 200) — verified separately; here: provenance fields complete |
| **Failure State** | `PROVENANCE_INCOMPLETE` (missing any of 10 required fields) |
| **Fail Closed** | YES — any missing field → `passed=False` |

**Key Code:** `provenance_gate.py:56-87` — all 10 fields must be non-empty

### Stage 5: Contract Compatibility

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/contract_gate.py` → `ContractGate.validate()` |
| **Responsible** | `HumanArtifactIngestor.ingest()` (automatic) |
| **Input** | `ContractCompatibility` enum, `format_verified` bool, `limitations` list |
| **Output** | `ContractGateResult`: compatibility, passed, details |
| **Gate Condition** | `COMPATIBLE` with `format_verified=True` OR `COMPATIBLE_WITH_LIMITATIONS` |
| **Failure State** | `CONTRACT_UNKNOWN` (no contract_version) / `CONTRACT_INCOMPATIBLE` |
| **Fail Closed** | YES — `UNKNOWN` → `passed=False`; `INCOMPATIBLE` → `passed=False` |

**Key Code:** `contract_gate.py:100-124` — `require_verified_format=True` by default

### Stage 6: Format / Schema Validation

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/human_ingestion.py` → `_read_artifact_headers()` |
| **Responsible** | `HumanArtifactIngestor.ingest()` (automatic) |
| **Input** | Artifact file path |
| **Output** | `mime_type`, `headers` (list[str]), `file_size` |
| **Gate Condition** | File readable; headers extracted; MIME type supported (CSV/XLSX) |
| **Failure State** | `FORMAT_MISMATCH` / `BLOCKED_FORMAT_INCOMPATIBLE` / `NotImplementedError` (PDF) |
| **Fail Closed** | YES — unsupported format raises exception; PDF requires manual conversion first |

### Stage 7: Provenance Completeness

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/provenance_gate.py` → `ProvenanceGate.validate()` (re-run) |
| **Responsible** | `HistoricalQualityGateRunner.run()` (full quality pipeline) |
| **Input** | Complete `SourceMetadata` from ingestion + adapter parsing |
| **Output** | `ProvenanceGateResult` with all 10 fields present |
| **Gate Condition** | All 10 provenance fields non-empty |
| **Failure State** | `BLOCKED_PROVENANCE_INCOMPLETE` |
| **Fail Closed** | YES |

### Stage 8: Quality Gates (15 Sprint 3.6 Gates)

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/quality_gate_integration.py` → `HistoricalQualityGateRunner.run()` |
| **Responsible** | Full ETL pipeline + modelling readiness evaluation |
| **Input** | `EvidenceManifest`, `SourceMetadata`, artifact bytes, data_quality_results, temporal_safety |
| **Output** | `HistoricalQualityResult`: classification, readiness, evidence_status, lifecycle_stage |
| **Gate Condition** | All critical gates (1-10, 12, 15) pass + PII + provenance + integrity + contract + temporal |
| **Failure State** | `BLOCKED_QUALITY_GATES_FAILED` / specific gate failure |
| **Fail Closed** | YES — any critical gate failure → `NOT_READY` |

**Classification Logic:** `quality_gate_integration.py:182-240`
- `READY`: All critical pass + temporal_safety + non-critical pass
- `READY_WITH_LIMITATIONS`: Critical 1-10 pass, non-critical documented
- `NOT_READY`: Any critical gate fails

### Stage 9: Readiness Classification

| Aspect | Detail |
|--------|--------|
| **Implementation** | `config/modelling_readiness.yaml` registry + `modelling/config/modelling_readiness.py` |
| **Responsible** | Maintainer (manual update after evidence review) |
| **Input** | `HistoricalQualityResult` + maintainer review |
| **Output** | Updated registry entry with `readiness`, `lifecycle_stage`, `evidence_status` |
| **Gate Condition** | Evidence-based: quality gates + temporal + provenance + contract |
| **Failure State** | `NOT_READY` (default for any missing evidence) |
| **Fail Closed** | YES — registry default is `NOT_READY`; promotion requires evidence |

### Stage 10: Temporal Validation

| Aspect | Detail |
|--------|--------|
| **Implementation** | `etl/contracts/historical/temporal_gate.py` → `TemporalReadinessGate.validate()` |
| **Responsible** | `modelling/splits/engine.py` → `TemporalSplitter.get_current_status()` |
| **Input** | `modelling_ready_years: dict[str, list[int]]` from registry |
| **Output** | `TemporalReadinessResult`: passed, verified_years, can_split_train_val_test |
| **Gate Condition** | ≥3 verified modelling-ready years across authorities, chronological, no gaps blocking split |
| **Failure State** | `BLOCKED_INSUFFICIENT_YEARS` (1 or 2 years) |
| **Fail Closed** | YES — synthetic/future/unverified years NOT counted |

**Key Code:** `temporal_gate.py:68-86` — only counts years where `readiness == "READY"` AND `lifecycle_stage == "MODELLING_READY"`

**Thresholds Verified:**
- 1 verified year → BLOCKED ✅
- 2 verified years → BLOCKED ✅
- 3+ verified years → eligible (subject to all other gates) ✅
- Synthetic/fixture years → NOT counted ✅

### Stage 11: Target Validation

| Aspect | Detail |
|--------|--------|
| **Implementation** | `modelling/targets/engine.py` → `TargetEngine.get_first_modelling_target()` |
| **Responsible** | Modelling pipeline entry point |
| **Input** | Current registry state (verified years, data availability) |
| **Output** | Target name or `"NO_TARGET_READY"` |
| **Gate Condition** | At least one target has `readiness_status == READY` |
| **Failure State** | `NO_TARGET_READY` (all targets blocked) |
| **Fail Closed** | YES — `get_first_modelling_target()` returns `"NO_TARGET_READY"` by default |

**Current State:** All 5 targets (`closing_rank`, `opening_rank`, `admission_probability`, `seat_allocation`, `vacancy_after_round`) → `NO_TARGET_READY`

**Blocking Reasons:**
- `closing_rank`/`opening_rank`: Need ≥3 years historical allotments, MCC 2021-2024 + state data
- `admission_probability`/`seat_allocation`: Fundamentally unavailable (applicant pool, preferences = PII)
- `vacancy_after_round`: No vacancy canonical model, no vacancy data ingested

### Stage 12: Training Eligibility

| Aspect | Detail |
|--------|--------|
| **Implementation** | `modelling/training/guard.py` → `TrainingGuard.check_training_allowed()` |
| **Responsible** | Any training invocation (global singleton) |
| **Input** | `DatasetVersion`, `LeakageResult`, `QualityGateResult`, `target_name` |
| **Output** | `TrainingGuardResult`: allowed, block_reasons, details |
| **Gate Condition** | ALL must pass: temporal_status == READY, target_readiness == "READY", verified_years ≥ minimum, leakage passed, quality gates passed, provenance complete, target defined |
| **Failure State** | `TRAINING_BLOCKED` with specific `TrainingBlockReason` enum |
| **Fail Closed** | YES — **IMPOSSIBLE TO BYPASS ACCIDENTALLY** (no force option) |

**Block Reasons (checked in order):**
1. `TEMPORAL_VALIDATION_BLOCKED`
2. `INSUFFICIENT_VERIFIED_YEARS`
3. `TARGET_NOT_READY`
4. `LEAKAGE_CHECKS_FAILED`
5. `DATA_QUALITY_GATES_FAILED`
6. `PROVENANCE_INCOMPLETE`
7. `NO_TARGET_DEFINED`

**Current State:** `TRAINING_BLOCKED` (temporal blocked + no target + insufficient years)

---

## 4. Ownership & Responsibility Matrix

| Stage | Owner | Accountability |
|-------|-------|----------------|
| Source Discovery | Data Engineer | Register in `data_sources.yaml` |
| Human Acquisition | Human Operator | Follow acquisition procedure honestly |
| Integrity/Checksum | System (automatic) | `ArtifactIntegrity` computes/verifies |
| PII Validation | System (automatic) | `PIIGate` screens column headers |
| Source Verification | System (automatic) | `ProvenanceGate` validates 10 fields |
| Contract Compatibility | Maintainer + System | `ContractGate` + manual format inspection |
| Format Validation | Human Operator + System | Document headers; system reads |
| Quality Gates | System (automatic) | `HistoricalQualityGateRunner` runs 15 gates |
| Readiness Classification | Maintainer | Update `modelling_readiness.yaml` with evidence |
| Temporal Validation | System (automatic) | `TemporalReadinessGate` evaluates registry |
| Target Validation | System (automatic) | `TargetEngine` evaluates target definitions |
| Training Eligibility | System (automatic) | `TrainingGuard` blocks if any gate fails |

---

## 5. Audit Trail Expectations

Every artifact that reaches `MODELLING_READY` must have:

1. **Source Discovery Record** — `data_sources.yaml` entry with verification date
2. **Acquisition Manifest** — Complete `EvidenceManifest` (all required fields)
3. **Integrity Record** — SHA-256, `source_file_id`, checksum match proof
4. **PII Screening Log** — `PIIGateResult` with zero detections
5. **Provenance Record** — Complete `SourceMetadata` (10 fields)
6. **Contract Assessment** — `ContractGateResult` with compatibility classification
7. **Quality Gate Report** — All 15 gate results (`HistoricalQualityResult`)
8. **Registry Entry** — `modelling_readiness.yaml` with evidence-based status
9. **Temporal Evaluation** — `TemporalReadinessResult` showing ≥3 years
10. **Target Readiness** — `TargetEngine.get_target_readiness()` for chosen target
11. **Training Guard Log** — `TrainingGuardResult` showing `allowed=True` (if training)

**Missing any item = NOT_READY.**

---

## 6. State Transition Rules (from `lifecycle.py`)

**Valid Transitions (evidence REQUIRED for each):**

```
DISCOVERED → SOURCE_VERIFIED
    Evidence: Official source confirmed; URL HTTP 200; source_id registered

SOURCE_VERIFIED → RETRIEVED
    Evidence: File downloaded; HTTP 200; timestamp recorded; method documented

SOURCE_VERIFIED → BLOCKED_AUTOMATED_DOWNLOAD
    Evidence: HTTP 403/429; bot protection confirmed; manual path documented

RETRIEVED → HASHED
    Evidence: SHA-256 computed; recorded in provenance; source_file_id generated

HASHED → FORMAT_INSPECTED
    Evidence: Column headers/schema documented; data types recorded; format_status set

FORMAT_INSPECTED → PII_SCREENED
    Evidence: PII blocklist applied; status CLEAR/DETECTED/EXCLUDED

PII_SCREENED → CONTRACT_CHECKED
    Evidence: Contract version identified; mapping verified; compatibility classified

PII_SCREENED → BLOCKED_PII_DETECTED
    Evidence: PII columns detected; documented as PII_BEARING

CONTRACT_CHECKED → PARSED
    Evidence: Parsed through adapter; canonical records produced; validation passed

CONTRACT_CHECKED → BLOCKED_CONTRACT_INCOMPATIBLE
    Evidence: Compatibility = INCOMPATIBLE; differences documented

CONTRACT_CHECKED → BLOCKED_FORMAT_INCOMPATIBLE
    Evidence: Structural incompatibility; cannot parse with existing contracts

PARSED → VALIDATED
    Evidence: All 15 quality gates executed; classification assigned

VALIDATED → PROVENANCE_COMPLETE
    Evidence: All 10 provenance fields present; checksum chain verified

PROVENANCE_COMPLETE → IDEMPOTENCY_VERIFIED
    Evidence: Re-ingestion produces identical records; short-circuit works

IDEMPOTENCY_VERIFIED → QUALITY_GATES_PASSED
    Evidence: All critical gates pass; classification READY/READY_WITH_LIMITATIONS

QUALITY_GATES_PASSED → MODELLING_READY
    Evidence: Temporal gate passed; minimum years satisfied; registry updated
```

**INVALID Transitions (enforced by `validate_transition()`):**
- Skipping any stage
- Moving from BLOCKING state to any other state
- Moving to MODELLING_READY without temporal readiness

---

## 7. Current Pipeline Status (Sprint 4.4 Baseline)

| Stage | MCC 2025 | MCC 2021-2024 | Maharashtra 2021-2025 | Karnataka 2021-2025 | UP 2021-2025 |
|-------|----------|---------------|----------------------|---------------------|--------------|
| Source Discovery | ✅ | ✅ | ✅ | ✅ | ✅ |
| Human Acquisition | ✅ (2025) | ❌ BLOCKED_403 | ❌ UNKNOWN | ❌ UNKNOWN | ❌ UNKNOWN |
| Integrity | ✅ | ❌ | ❌ | ❌ | ❌ |
| PII Validation | ✅ | ❌ | ❌ | ❌ | ❌ |
| Source Verification | ✅ | ❌ | ❌ | ❌ | ❌ |
| Contract Compatibility | ✅ v1.1.0 | ❌ UNKNOWN | ❌ UNKNOWN | ❌ UNKNOWN | ❌ PLACEHOLDER |
| Format Validation | ✅ | ❌ | ❌ | ❌ | ❌ |
| Provenance | ✅ | ❌ | ❌ | ❌ | ❌ |
| Quality Gates | ✅ 15/15 | ❌ 0/15 | ❌ 0/15 | ❌ 0/15 | ❌ 0/15 |
| Readiness | ✅ READY | ❌ NOT_READY | ❌ NOT_READY | ❌ NOT_READY | ❌ NOT_READY |
| Temporal | N/A (1 yr) | ❌ BLOCKED | ❌ BLOCKED | ❌ BLOCKED | ❌ BLOCKED |
| Target | ❌ NO_TARGET | ❌ NO_TARGET | ❌ NO_TARGET | ❌ NO_TARGET | ❌ NO_TARGET |
| Training | ❌ BLOCKED | ❌ BLOCKED | ❌ BLOCKED | ❌ BLOCKED | ❌ BLOCKED |

---

## 8. Key Invariants (NEVER Violate)

1. **No stage may be skipped** — `validate_transition()` enforces this
2. **All transitions require documented evidence** — `lifecycle_requires_evidence()` always returns True
3. **Blocking states are terminal** — `VALID_PROMOTIONS[BLOCKED_*]` = empty tuple
4. **UNKNOWN never becomes READY** — `ContractGate` rejects `UNKNOWN`; `TemporalGate` ignores unverified years
5. **HTTP 403 never grants permission** — `AUTOMATED_DOWNLOAD_BLOCKED` is a valid honest state, not a failure to work around
6. **Provenance is mandatory** — 10 fields or `NOT_READY`
7. **PII fails closed** — Any detection → `BLOCKED_PII`
8. **Temporal requires real verified years** — Synthetic/fixture years excluded
9. **Target requires evidence** — `NO_TARGET_READY` until requirements met
10. **Training requires all gates** — `TrainingGuard` has no override

---

*End of Acquisition Lifecycle Document — Sprint 4.4*