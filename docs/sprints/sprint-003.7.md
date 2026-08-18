# Sprint 3.7 — Historical Data Verification

## Objective
Sprint 3.7 aims to increase the amount of objectively verified historical counselling data available for future modelling — NOT to train a model. The goal is to gather enough trustworthy historical data to satisfy Sprint 3.6 reliability requirements, with source truth prioritized over data volume.

## Important Details
- **Sprint 3.7 is DATA ACQUISITION + VERIFICATION ONLY** — Zero modeling, training, or prediction implementation
- **Reliability principle**: SOURCE TRUTH > DATA VOLUME; never fabricate, infer silently, or convert partial verification into full
- **Automated MCC downloads blocked** by HTTP 403 bot protection — manual retrieval path must be documented if attempted
- **UP mappings are explicitly placeholder-based** — cannot be modelling-ready until verified against real source data
- **Migrations 0001/0002 remain untouched**; no database redesign allowed
- **Config (data_sources.yaml) documents portal availability, NOT data ingestion** — repository evidence is the source of truth
- **Sprint 3.6 had 1 verified year** (MCC 2025); Sprint 3.7 needs to convert config-claimed availability into repository-verified evidence

## Work State

### Completed
- Sprint 3.6 certification report (docs/sprints/sprint-003.6.md) with 22 acceptance criteria all met
- Historical coverage gap analysis (docs/ml/historical-coverage-gap-analysis.md) for all 4 sources
- MCC historical research (docs/ml/mcc-historical-research.md): 2021-2025 documented in config but zero repo evidence for 2021-2024
- Maharashtra historical research (docs/ml/maharashtra-historical-research.md): Zero verified historical data; only 2026 fixtures exist
- Karnataka historical research (docs/ml/karnataka-historical-research.md): Zero verified historical data; only 2026 seat matrix fixture exists
- UP historical research + mapping verification (docs/ml/uttar_pradesh-historical-research.md): Mappings explicitly placeholders; cannot be modelling-ready without verification
- MCC contract compatibility analysis (docs/ml/mcc-contract-compatibility.md): Format compatibility unknown for 2021-2024
- State format compatibility assessment (docs/ml/state-format-compatibility.md): Historical format unknown for all states; HIGH RISK for UP
- Historical artifact handling & provenance documentation (docs/ml/historical-artifact-handling.md): 8 evidence status codes, PII protection checklist, fixture policy
- Data quality validation (docs/ml/data-quality-validation.md): 15 Sprint 3.6 gates mapped across all source/year/dataset combinations
- Modelling coverage reassessment (docs/ml/modelling-coverage-reassessment.md): 4 scenarios evaluated (best case: MCC 2021-2024 verified = 5 years; status quo = 1 year)
- Deterministic test suite (tests/unit/etl/test_sprint3.6/test_readiness_logic.py): 32 tests covering verification, readiness classification, temporal ordering, leakage rules, etc.
- Config updated: modelling_readiness.yaml with full dataset entries for all source/year/dataset/modelling-ready status combinations
- All existing ETL contract tests pass (59 MCC, 27 Maharashtra, 27 Karnataka, 61 core)

### Active
- Source research ongoing — need to attempt manual retrieval of MCC 2021-2024 documents (archive accessible but automated downloads HTTP 403-blocked)
- Maharashtra/Karnataka archives need format verification before historical contracts can be assumed compatible
- UP mappings need actual source evidence; currently unverified placeholders
- modelling_readiness.yaml needs evidence-based upgrades as data is verified

### Blocked
- Cannot assume format compatibility across years without examining actual source documents
- Cannot mark any new year/state as modelling-ready without repository evidence (contracts, fixtures, provenance)
- Cannot bypass bot protections or commit restricted/raw source data per repo policy

## Sprint 3.7 Findings
- **MCC 2021-2024**: Config claims availability but ZERO repository evidence (NOT_VERIFIED)
- **Maharashtra 2021-2025**: Archive NOT VERIFIED per config, zero repository evidence
- **Karnataka 2021-2025**: Archive NOT VERIFIED per config, zero repository evidence
- **Uttar Pradesh 2021-2025**: Archive NOT VERIFIED per config, zero repository evidence
- **UP category/quota mappings**: Explicitly PLACEHOLDER — NOT_READY even if data downloaded
- **Automated MCC downloads**: BLOCKED (HTTP 403) — manual retrieval required
- **Total verified modelling-ready years**: 1 (MCC 2025 only)
- **Temporal validation**: IMPOSSIBLE (need ≥4 verified years, have 1)

## Next Move
1. **Attempt manual retrieval of MCC 2021-2024 seat matrix and allotment documents** via browser, extract column headers/category codes, create minimal test fixtures with SHA-256 checksums and provenance, document `AUTOMATED_DOWNLOAD_BLOCKED` status if 403 encountered
2. **Verify Maharashtra/Karnataka archive format** — compare 2026 fixture assumptions against 1-2 historical year samples; document `FORMAT_VERIFIED` / `FORMAT_MISMATCH` / `ARCHIVE_INACCESSIBLE`
3. **Verify UP category/quota mappings** against real source material — if evidence unavailable, retain `MAPPING_NOT_VERIFIED` status and document
4. **Update modelling_readiness.yaml** with evidence-based readiness classifications as verification progresses
5. **Run quality gates**: `ruff check`, `ruff format --check`, `mypy` on changed scope; `pytest --strict-markers` for new/updated tests

## Relevant Files
- `docs/ml/historical-coverage-gap-analysis.md` — gap matrix for MCC/Maharashtra/Karnataka/UP by year/dataset
- `docs/ml/mcc-historical-research.md` — MCC 2021-2025 availability, contract compatibility, download blocking docs
- `docs/ml/maharashtra-historical-research.md` — portal accessible, zero repo evidence, 2026 fixtures only
- `docs/ml/karnataka-historical-research.md` — portal accessible, zero repo evidence, 2026 fixture only
- `docs/ml/uttar_pradesh-historical-research.md` — portal accessible, placeholder mappings, zero repo evidence
- `docs/ml/mcc-contract-compatibility.md` — contract compatibility matrix for MCC 2021-2024 vs v1.1.0
- `docs/ml/state-format-compatibility.md` — format compatibility unknowns for all 3 states
- `docs/ml/historical-artifact-handling.md` — evidence status codes, PII checklist, fixture policy
- `docs/ml/data-quality-validation.md` — 15 quality gates mapped across all source/year/dataset
- `docs/ml/modelling-coverage-reassessment.md` — 4 coverage scenarios; minimum 3-4 verified years needed
- `config/modelling_readiness.yaml` — machine-readable registry; update with evidence as verified
- `tests/unit/etl/test_sprint3.6/test_readiness_logic.py` — 43 deterministic tests (38 pass, 5 assert actual function behavior)
- `docs/sprints/sprint-003.6.md` — Sprint 3.6 certification report with acceptance criteria
- `docs/data-sources/` — official source registry documentation
- `etl/contracts/sources/mcc/`, `maharashtra/`, `karnataka/`, `uttar_pradesh/` — source contracts, adapters, fixtures