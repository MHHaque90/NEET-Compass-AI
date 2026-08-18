# Dataset Readiness Classification — Sprint 3.6

## Phase 2: Determine Dataset Readiness

This document classifies each historical source/year/dataset combination into one of three readiness levels based on the Phase 1 evidence.

### Readiness Definitions

| Classification | Criteria |
|----------------|----------|
| **READY** | Full contract + adapter + validation + provenance + test coverage + verified repository data (fixtures or raw) for the specific year/round |
| **READY_WITH_LIMITATIONS** | Contract + adapter exist but data is fixture-only (not from live source), or missing some dataset types (e.g., seat matrix but no allotments), or mappings unverified |
| **NOT_READY** | No contract, no adapter, no repository data, or critical gaps (unverified mappings, missing validation) |

---

### Readiness Matrix by Authority

#### MCC (Medical Counselling Committee)

| Year | Dataset | Round | Classification | Rationale |
|------|---------|-------|----------------|-----------|
| 2025 | Seat Matrix | Round 1 | **READY** | Full contract (v1.1.0), adapter, validation rules, provenance, tests, PII protection |
| 2025 | Allotments | Round 3 | **READY** | Full contract (v1.1.0), adapter, validation rules, provenance, tests, PII blocklist |
| 2025 | Vacancy Reports | All | **NOT_READY** | No contract, no adapter, PDF only |
| 2025 | Info Bulletins | All | **NOT_READY** | No contract, no adapter, PDF only |
| 2025 | Joined Lists | All | **NOT_READY** | PII exclusion, no ingestion path |
| 2025 | Institutes | N/A | **READY_WITH_LIMITATIONS** | Reference data only, not modelled |
| 2024 | Seat Matrix | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2024 | Allotments | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2023 | Seat Matrix | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2023 | Allotments | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2022 | Seat Matrix | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2022 | Allotments | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2021 | Seat Matrix | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2021 | Allotments | Any | **NOT_READY** | No contract, no adapter, no repository data |
| 2026 | Seat Matrix | Round 1 | **NOT_READY** | Live evidence only, 403 blocks download, no fixtures |
| 2026 | Allotments | Any | **NOT_READY** | No verified download, no fixtures |

#### Maharashtra (MAHA CET Cell)

| Year | Dataset | Round | Classification | Rationale |
|------|---------|-------|----------------|-----------|
| 2026 | Seat Matrix | Round 1 | **READY_WITH_LIMITATIONS** | Contract v1.0.0, adapter, validation, tests exist BUT only test fixtures (no live download verified) |
| 2026 | Allotments | Round 1 | **READY_WITH_LIMITATIONS** | Contract v1.0.0, adapter, validation, tests exist BUT only test fixtures |
| 2025 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2024 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2023 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2022 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2021 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |

#### Karnataka (KEA)

| Year | Dataset | Round | Classification | Rationale |
|------|---------|-------|----------------|-----------|
| 2026 | Seat Matrix | Round 1 | **READY_WITH_LIMITATIONS** | Contract v1.0.0, adapter, validation, tests exist BUT only test fixture (no live download verified) |
| 2026 | Allotments | Round 1 | **READY_WITH_LIMITATIONS** | Contract v1.0.0, adapter, validation exist BUT no fixture, no live download |
| 2025 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2024 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2023 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2022 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2021 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |

#### Uttar Pradesh (UPMU/DME UP)

| Year | Dataset | Round | Classification | Rationale |
|------|---------|-------|----------------|-----------|
| 2026 | Seat Matrix | Round 1 | **NOT_READY** | Contract v1.0.0, adapter exist BUT mappings explicitly placeholder/unverified, fixture only |
| 2026 | Allotments | Round 1 | **NOT_READY** | Contract v1.0.0, adapter exist BUT mappings explicitly placeholder/unverified, no fixture |
| 2025 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2024 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2023 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2022 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |
| 2021 | Any | Any | **NOT_READY** | No contract, no adapter, no repository evidence |

---

### Summary Classification Count

| Classification | Count |
|----------------|-------|
| **READY** | 2 (MCC 2025 Seat Matrix + Allotments) |
| **READY_WITH_LIMITATIONS** | 5 (MCC 2025 Institutes; Maharashtra 2026 Seat+Allotment; Karnataka 2026 Seat+Allotment) |
| **NOT_READY** | 37 (all other combinations) |

---

### Critical Separation: SOURCE AVAILABLE vs SOURCE SUITABLE FOR MODELLING

| Aspect | SOURCE AVAILABLE | SOURCE SUITABLE FOR MODELLING |
|--------|------------------|-------------------------------|
| MCC 2025 | ✅ Yes (config + contracts) | ✅ YES (2 datasets) |
| Maharashtra 2026 | ⚠️ Config only | ⚠️ FIXTURES ONLY (not live) |
| Karnataka 2026 | ⚠️ Config only | ⚠️ FIXTURES ONLY (not live) |
| UP 2026 | ⚠️ Config only | ❌ PLACEHOLDER MAPPINGS |
| MCC 2021-2024 | ⚠️ Config claims only | ❌ NO REPOSITORY EVIDENCE |
| States 2021-2025 | ⚠️ Config claims only | ❌ NO REPOSITORY EVIDENCE |

**Key Distinction**: The config/data_sources.yaml documents *source portal verification* (the website exists), NOT *data ingestion verification* (files downloaded, parsed, validated). Repository evidence is the only basis for modelling suitability.

---

### Modelling Readiness Verdict

**Only TWO dataset/year combinations are READY for modelling:**
1. MCC 2025 Seat Matrix (Round 1) - ALL_INDIA quota
2. MCC 2025 Allotments (Round 3) - ALL_INDIA quota

**Five combinations are READY_WITH_LIMITATIONS** (fixture-only or reference data).

**All 37 other combinations are NOT_READY.**

This is the evidence-based reality. No amount of config documentation changes this.