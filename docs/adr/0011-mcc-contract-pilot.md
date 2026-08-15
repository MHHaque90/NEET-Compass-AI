# ADR-0011 — MCC contract pilot: seat matrix & allotments (Sprint 3.1)

- **Status:** Accepted
- **Date:** 2025-08-12
- **Deciders:** NEET Compass AI — ETL track
- **Tags:** etl, contract, mcc, pii, idempotency

## Context

The NEET Compass AI backend has no live ingestion path for official NEET
counselling data. The `etl/contracts/` framework (Sprint 2.5) defines
`SourceContract`, `SourceAdapter`, `ContractValidator`, and canonical
dataclasses, but `etl/contracts/sources/__init__.py` explicitly deferred
real adapters ("DO NOT implement live adapters here"). Sprint 3.1 changes
that: it must stand up the first production-shaped ETL for the two
highest-priority MCC 2025 datasets.

Constraints discovered during exploration:

1. **Two abbreviation schemes, one concept.** The MCC seat-matrix PDFs use
   `OP`/`BC`/`EW`/`SC`/`ST` with a `PH` disability suffix and full-name
   quotas (`All India`, `Open Seat Quota`). The allotment files use `GN`/
   `BC`/`EW`/`SC`/`ST` with a `PwD` suffix and two-letter quota codes
   (`AI`, `SO`, ...). The canonical `SeatMatrix`/`Allotment` dataclasses use
   string `quota_id`/`category_id` (per `etl/contracts/canonical/__init__.py`).
2. **Candidate PII risk.** The human-readable allotment report carries
   candidate name, percentile, contact, aadhaar, etc. The canonical
   `Allotment` record only needs `rank`/`score`/`seat_count` plus cohort
   identifiers; candidate PII must never enter the canonical layer.
3. **No PostgreSQL in the build/test environment**, yet tests must exercise
   the persistence and idempotency story, not just transform logic.
4. **Seat-matrix source is a PDF table**, not a CSV; the allotment source is a
   (separate) machine-readable CSV. The contract layer consumes *rows*, so a
   PDF-table extractor and a CSV parser both feed the same adapter.

## Decision

1. Implement `etl/contracts/sources/mcc/` as a self-contained pilot with two
   datasets: `seat_matrix` and `allotments`, both contract version `1.1.0`,
   effective year `2025`.
2. Normalise both source vocabularies onto canonical string IDs via
   `mappings.py` (`gn`/`bc`/`ew`/`sc`/`st`, `_pwd` suffix for disability;
   `ai`/`so`/`am`/...). The enum-to-string bridge happens at the SQLAlchemy
   ORM boundary in Sprint 3.2, not in the contract.
3. Exclude PII by contract, not by scrubbing: the `allotments` contract
   declares only the 9 non-PII columns, the adapter emits only canonical
   fields, and a pipeline note is raised if any
   `ALLOTMENT_PRIVACY_BLOCKLIST` column is present.
4. Abstract persistence and file-deduplication behind `Loader` and
   `FileRegistry` protocols in `pipeline.py`, with `InMemory*` fakes, so the
   full pipeline (validate -> transform -> upsert -> dedup) is unit-tested
   without PostgreSQL.
5. Ground every fixture on the real MCC 2025 artefacts: the seat-matrix test
   rows are the actual rows extracted from
   `seatmatrix_aiq_r1_2025.pdf` / `seatmatrix_aiims_bhu_jipmer_r1_2025.pdf`,
   and the quota/category maps are derived from the abbreviation tables on
   page 0 of `allotment_r3_2025.pdf`.

## Consequences

- **Positive:** The contract/adapter/parser is shared and dataset-specific
  only through small contract + mapping tables; adding an NMC or state source
  follows the same shape. Idempotency and PII protection are regression-tested.
  The `etl` package gains a real, importable, type-checked and lint-clean
  sub-package (mypy strict + ruff clean on the new code).
- **Negative / deferred:** No real-database round-trip is performed here
  (PostgreSQL unavailable); the production `Loader` that upserts into
  `seat_matrix`/`allotment` tables is a Sprint 3.2 task. The seat-matrix
  category rows (`BC NO`/`BC PH`) carry a PwD dimension the current DB
  `SeatMatrixModel` lacks — resolving that enum-to-string mapping is also
  deferred to Sprint 3.2 to avoid touching the ORM in this sprint.
- **Test surface:** 46 new unit tests; the real-PDF extraction test is
  env-gated (`MCC_SAMPLE_SEATMATRIX_PDF`) and skips in CI when the sample is
  absent.

## References

- `etl/contracts/sources/mcc/` (implementation)
- `tests/unit/etl/contracts/sources/mcc/` (tests)
- `docs/sprints/sprint-003.1.md`
- `etl/contracts/canonical/__init__.py` (canonical dataclasses)
- `backend/app/domain/enums.py` (DB enum vocabulary, Sprint 3.2 bridge)
