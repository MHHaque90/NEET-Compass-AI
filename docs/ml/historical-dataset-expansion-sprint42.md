# Historical Dataset Expansion — Sprint 4.2

**Classification**: TECHNICAL SPECIFICATION
**Version**: 1.0
**Status**: AUTHORIZED FOR USE
**Sprint**: 4.2 — Historical Dataset Expansion & Target Validation

---

## 1. Purpose

This document builds an evidence-backed historical coverage matrix for MCC, Maharashtra, Karnataka, and Uttar Pradesh. For every candidate historical year/dataset combination, it determines the verification status across all required dimensions per the Historical Evidence Lifecycle (Sprint 3.9).

**Principle**: PORTAL_EXISTS ≠ DOCUMENT_RETRIEVED ≠ FORMAT_VERIFIED ≠ CONTRACT_COMPATIBLE ≠ MODELLING_READY

---

## 2. Evidence-Backed Coverage Matrix

### 2.1 MCC (Medical Counselling Committee) — All India Quota

| Authority | Year | Dataset | Round | Official Source | Source Verification | Artifact Availability | Retrieval Status | Checksum | Format Status | Contract Compatibility | Provenance Status | PII Status | Quality Status | Temporal Eligibility | Final Readiness |
|-----------|------|---------|-------|-----------------|---------------------|----------------------|------------------|----------|---------------|------------------------|-------------------|------------|----------------|---------------------|-----------------|
| MCC | 2025 | seat_matrix | Round 1 | mcc_ug_archive | VERIFIED (HTTP 200, Sprint 3.1A) | YES (fixture + tests) | RETRIEVED | VERIFIED (in tests) | FORMAT_VERIFIED | CONTRACT_COMPATIBLE (v1.1.0) | COMPLETE (10 fields) | PII_CLEAR | 15/15 PASSED | ELIGIBLE | **READY** |
| MCC | 2025 | allotments | Round 3 | mcc_ug_archive | VERIFIED (HTTP 200, Sprint 3.1A) | YES (fixture + tests) | RETRIEVED | VERIFIED (in tests) | FORMAT_VERIFIED | CONTRACT_COMPATIBLE (v1.1.0) | COMPLETE (10 fields) | PII_CLEAR | 15/15 PASSED | ELIGIBLE | **READY** |
| MCC | 2024 | seat_matrix | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2024 | allotments | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2023 | seat_matrix | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2023 | allotments | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2022 | seat_matrix | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2022 | allotments | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2021 | seat_matrix | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |
| MCC | 2021 | allotments | All | mcc_ug_archive | VERIFIED (archive page HTTP 200) | DOCUMENTED ON PORTAL | AUTOMATED_DOWNLOAD_BLOCKED (HTTP 403) | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | ELIGIBLE (if verified) | **NOT_VERIFIED** |

**MCC Summary**: 2 datasets READY (2025), 8 datasets NOT_VERIFIED (2021-2024). Automated download blocked by HTTP 403 bot protection. Manual retrieval path documented but not executed. Format compatibility UNKNOWN without examining actual source documents.

---

### 2.2 Maharashtra (MAHA CET Cell) — State Quota

| Authority | Year | Dataset | Round | Official Source | Source Verification | Artifact Availability | Retrieval Status | Checksum | Format Status | Contract Compatibility | Provenance Status | PII Status | Quality Status | Temporal Eligibility | Final Readiness |
|-----------|------|---------|-------|-----------------|---------------------|----------------------|------------------|----------|---------------|------------------------|-------------------|------------|----------------|---------------------|-----------------|
| Maharashtra | 2026 | seat_matrix | Round 1 | mcc_state_maharashtra | VERIFIED (portal HTTP 200) | YES (fixture only) | FIXTURE_ONLY | FIXTURE_CHECKSUM | FORMAT_VERIFIED (fixture) | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE (10 fields) | PII_CLEAR | 13/15 PASSED | NOT_ELIGIBLE (fixture only) | **READY_WITH_LIMITATIONS** |
| Maharashtra | 2026 | allotments | Round 1 | mcc_state_maharashtra | VERIFIED (portal HTTP 200) | YES (fixture only) | FIXTURE_ONLY | FIXTURE_CHECKSUM | FORMAT_VERIFIED (fixture) | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE (10 fields) | PII_CLEAR | 13/15 PASSED | NOT_ELIGIBLE (fixture only) | **READY_WITH_LIMITATIONS** |
| Maharashtra | 2025 | seat_matrix | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2025 | allotments | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2024 | seat_matrix | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2024 | allotments | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2023 | seat_matrix | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2023 | allotments | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2022 | seat_matrix | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2022 | allotments | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2021 | seat_matrix | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Maharashtra | 2021 | allotments | All | mcc_state_maharashtra | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |

**Maharashtra Summary**: 2 datasets READY_WITH_LIMITATIONS (2026 fixtures only), 10 datasets NOT_VERIFIED (2021-2025). Archive access NOT VERIFIED per `data_sources.yaml`. No historical artifacts in repository. Contract v1.0.0 is fixture-based; real historical format UNKNOWN.

---

### 2.3 Karnataka (KEA) — State Quota

| Authority | Year | Dataset | Round | Official Source | Source Verification | Artifact Availability | Retrieval Status | Checksum | Format Status | Contract Compatibility | Provenance Status | PII Status | Quality Status | Temporal Eligibility | Final Readiness |
|-----------|------|---------|-------|-----------------|---------------------|----------------------|------------------|----------|---------------|------------------------|-------------------|------------|----------------|---------------------|-----------------|
| Karnataka | 2026 | seat_matrix | Round 1 | mcc_state_karnataka | VERIFIED (portal HTTP 200) | YES (fixture only) | FIXTURE_ONLY | FIXTURE_CHECKSUM | FORMAT_VERIFIED (fixture) | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE (10 fields) | PII_CLEAR | 13/15 PASSED | NOT_ELIGIBLE (fixture only) | **READY_WITH_LIMITATIONS** |
| Karnataka | 2026 | allotments | Round 1 | mcc_state_karnataka | VERIFIED (portal HTTP 200) | YES (fixture only) | FIXTURE_ONLY | FIXTURE_CHECKSUM | FORMAT_VERIFIED (fixture) | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE (10 fields) | PII_CLEAR | 12/15 PASSED | NOT_ELIGIBLE (fixture only) | **READY_WITH_LIMITATIONS** |
| Karnataka | 2025 | seat_matrix | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2025 | allotments | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2024 | seat_matrix | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2024 | allotments | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2023 | seat_matrix | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2023 | allotments | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2022 | seat_matrix | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2022 | allotments | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2021 | seat_matrix | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| Karnataka | 2021 | allotments | All | mcc_state_karnataka | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |

**Karnataka Summary**: 2 datasets READY_WITH_LIMITATIONS (2026 fixtures only), 10 datasets NOT_VERIFIED (2021-2025). Archive access NOT VERIFIED per `data_sources.yaml`. No historical artifacts in repository. Contract v1.0.0 is fixture-based; real historical format UNKNOWN.

---

### 2.4 Uttar Pradesh (UPMU/DME UP) — State Quota

| Authority | Year | Dataset | Round | Official Source | Source Verification | Artifact Availability | Retrieval Status | Checksum | Format Status | Contract Compatibility | Provenance Status | PII Status | Quality Status | Temporal Eligibility | Final Readiness |
|-----------|------|---------|-------|-----------------|---------------------|----------------------|------------------|----------|---------------|------------------------|-------------------|------------|----------------|---------------------|-----------------|
| UP | 2026 | seat_matrix | Round 1 | mcc_state_uttar_pradesh | VERIFIED (portal HTTP 200) | YES (fixture only) | FIXTURE_ONLY | FIXTURE_CHECKSUM | FORMAT_VERIFIED (fixture) | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE (10 fields) | PII_CLEAR | 10/15 PASSED | NOT_ELIGIBLE (fixture only) | **NOT_READY** |
| UP | 2026 | allotments | Round 1 | mcc_state_uttar_pradesh | VERIFIED (portal HTTP 200) | NO FIXTURE | FIXTURE_ONLY (seat_matrix only) | N/A | FORMAT_UNKNOWN | CONTRACT_COMPATIBLE (v1.0.0) | COMPLETE (10 fields) | UNKNOWN | 9/15 PASSED | NOT_ELIGIBLE | **NOT_READY** |
| UP | 2025 | seat_matrix | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2025 | allotments | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2024 | seat_matrix | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2024 | allotments | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2023 | seat_matrix | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2023 | allotments | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2022 | seat_matrix | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2022 | allotments | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2021 | seat_matrix | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |
| UP | 2021 | allotments | All | mcc_state_uttar_pradesh | NOT_VERIFIED (archive NOT VERIFIED per config) | UNKNOWN | NOT_VERIFIED | NOT_COMPUTED | FORMAT_UNKNOWN | CONTRACT_UNKNOWN | INCOMPLETE | UNKNOWN | NOT_RUN | UNKNOWN | **NOT_VERIFIED** |

**UP Summary**: 1 dataset NOT_READY (2026 seat_matrix - placeholder mappings), 1 dataset NOT_READY (2026 allotments - no fixture, placeholder mappings), 10 datasets NOT_VERIFIED (2021-2025). **Critical Blocker**: Category/quota mappings are explicitly PLACEHOLDERS — must be verified against real UP source data before any UP dataset can reach READY.

---

## 3. Verification Status Definitions

| Field | Values | Meaning |
|-------|--------|---------|
| **Source Verification** | VERIFIED / NOT_VERIFIED | Official URL accessible (HTTP 200) via live verification |
| **Artifact Availability** | YES / DOCUMENTED ON PORTAL / UNKNOWN / FIXTURE_ONLY / NO FIXTURE | Physical/logical existence of source document |
| **Retrieval Status** | RETRIEVED / AUTOMATED_DOWNLOAD_BLOCKED / FIXTURE_ONLY / NOT_VERIFIED | How/whether file was obtained |
| **Checksum** | VERIFIED / FIXTURE_CHECKSUM / NOT_COMPUTED | SHA-256 computed and recorded |
| **Format Status** | FORMAT_VERIFIED / FORMAT_UNKNOWN / FORMAT_MISMATCH | Column headers/schema match contract |
| **Contract Compatibility** | CONTRACT_COMPATIBLE / CONTRACT_COMPATIBLE_WITH_LIMITATIONS / CONTRACT_INCOMPATIBLE / CONTRACT_UNKNOWN | Classification per ContractGate |
| **Provenance Status** | COMPLETE / INCOMPLETE | All 10 SourceMetadata fields present |
| **PII Status** | PII_CLEAR / PII_DETECTED / PII_EXCLUDED / UNKNOWN | PII blocklist screening result |
| **Quality Status** | X/15 PASSED / NOT_RUN | Sprint 3.6 quality gates executed |
| **Temporal Eligibility** | ELIGIBLE / NOT_ELIGIBLE / UNKNOWN | Year can contribute to temporal validation if all gates pass |
| **Final Readiness** | READY / READY_WITH_LIMITATIONS / NOT_READY / NOT_VERIFIED | Modelling readiness classification |

---

## 4. Key Findings

### 4.1 No New Verified Historical Artifacts Since Sprint 4.1

- **MCC 2021-2024**: Portal accessible (archive page HTTP 200), but automated downloads blocked by HTTP 403. No manual retrieval executed. Format compatibility UNKNOWN.
- **Maharashtra 2021-2025**: Archive access NOT VERIFIED. Zero repository evidence.
- **Karnataka 2021-2025**: Archive access NOT VERIFIED. Zero repository evidence.
- **UP 2021-2025**: Archive access NOT VERIFIED. Zero repository evidence. Mappings unverified.

### 4.2 MCC 2024 — Highest Priority for Manual Retrieval

- Archive page verified with documents listed for 2024
- Contract v1.1.0 exists for 2025; format compatibility UNKNOWN without examining actual 2024 documents
- Human ingestion path exists (`etl/contracts/historical/human_ingestion.py`)

### 4.3 UP Mapping Blocker Persists

- Category/quota mappings explicitly documented as PLACEHOLDERS
- Even if UP historical data obtained, it cannot reach READY without verified mappings
- Gate 5/6 (category/quota validity) would fail on real data

### 4.4 State Historical Data: Contract v1.0.0 is Fixture-Based

- Maharashtra/Karnataka 2026 datasets use contract v1.0.0 built from synthetic fixtures
- Real historical format (2021-2025) UNKNOWN — cannot assume 2026 contract applies
- Must examine actual historical documents before compatibility classification

---

## 5. Acquisition Path for Sprint 4.2

### MCC (Priority 1)
1. Human obtains MCC 2024 Round 1 Seat Matrix PDF + Round 3 Allotment CSV from `https://mcc.nic.in/archive-ug/`
2. Records SHA-256, retrieval timestamp, exact URLs, method = "MANUAL_BROWSER"
3. Runs PII screening on column headers via `human_ingestion.py`
4. Compares format to MCC 2025 contract v1.1.0 → classify COMPATIBLE / COMPATIBLE_WITH_LIMITATIONS / INCOMPATIBLE / UNKNOWN
5. If COMPATIBLE: parse through existing adapters, run 15 quality gates, complete provenance
6. If COMPATIBLE_WITH_LIMITATIONS: document limitations, promote to READY_WITH_LIMITATIONS
7. If INCOMPATIBLE: document exact differences, decide on new contract version (explicit)
8. Update `modelling_readiness.yaml` with evidence-based status
9. Repeat for 2023, 2022, 2021

### State (Priority 2-4)
- **Prerequisite**: Archive access must be VERIFIED (live verification of archive pages)
- Same workflow as MCC, but contract compatibility against v1.0.0 (fixture-based)
- UP requires verified category/quota mappings before any dataset can reach READY

---

## 6. Current Modelling-Ready Year Count

| Authority | Verified Modelling-Ready Years |
|-----------|-------------------------------|
| MCC | [2025] |
| Maharashtra | [] |
| Karnataka | [] |
| Uttar Pradesh | [] |

**Total**: 1 year (MCC 2025 only)

---

## 7. Temporal Validation Status

- **Minimum required**: 3 verified modelling-ready years
- **Current**: 1 verified year
- **Status**: **TEMPORAL_VALIDATION_BLOCKED**

---

## 8. Next Steps

Sprint 4.2 investigation complete. The evidence confirms:
1. No new historical artifacts verified
2. MCC 2021-2024 remain blocked by HTTP 403 (no manual retrieval executed)
3. State archives NOT VERIFIED
4. UP mappings remain PLACEHOLDERS
5. Temporal validation remains BLOCKED
6. Target readiness remains NO_TARGET_READY

**Honest Assessment**: If no additional artifacts can be obtained, the status remains unchanged. This is an acceptable and scientifically honest outcome.

---

*End of Historical Dataset Expansion — Sprint 4.2*