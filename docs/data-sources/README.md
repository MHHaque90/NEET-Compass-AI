# Data Sources — Official-Source Intelligence Layer

> Sprint 3.0. This layer is the **source-of-truth research registry** for every
> official data source behind the NEET UG (MBBS/BDS) counselling domain.

This directory documents **where the data comes from**. The ETL specification
(`docs/ETL_SPEC.md`) describes **how the ETL works**. The two must not be
merged: this layer owns source intelligence, ETL owns transformation.

## Purpose

- Single inventory of verified official sources (regulators, examiner, state
  counselling authorities, central institutions).
- Verifiable field ownership (who is authoritative for what).
- Honest verification state: nothing is filled from memory; nothing is silently
  substituted with a third-party source.
- Machine-readable mirror for the product: `config/data_sources.yaml`.

## Contents

| File | Purpose |
|------|---------|
| [source-registry.md](source-registry.md) | Authoritative source inventory (all sources, all fields) |
| [mcc.md](mcc.md) | Medical Counselling Committee (all-India quota counselling) |
| [nta.md](nta.md) | National Testing Agency (NEET UG examination) |
| [nmc.md](nmc.md) | National Medical Commission (MBBS college recognition/intake) |
| [dental-regulator.md](dental-regulator.md) | National Dental Commission (BDS regulator) |
| [state-counselling.md](state-counselling.md) | State counselling authorities and portals |
| [central-institutions.md](central-institutions.md) | AIIMS, BHU, JIPMER, other central/institutional sources |
| [source-priority.md](source-priority.md) | P0/P1 priority definitions and assignment |
| [source-conflicts.md](source-conflicts.md) | Field-ownership matrix and conflict strategy |
| [data-lineage.md](data-lineage.md) | Documented pipeline lineage (architecture only) |
| [historical-availability.md](historical-availability.md) | Year-by-year availability (2021–2026) |
| [mcc-historical-dataset-matrix.md](mcc-historical-dataset-matrix.md) | Per-year MCC archive verification matrix (2021–2026) |

## Machine-readable registry

`config/data_sources.yaml` mirrors this layer for tests and future tooling.

- It is a **research registry only**. It contains no scraping logic.
- Validation of the registry lives in `config/tests/test_source_registry.py`.

## Verification methodology

Every source record carries a `verification_status`:

| Status | Meaning |
|--------|---------|
| `VERIFIED` | URL confirmed and its purpose/dataset confirmed during research |
| `VERIFIED_URL_PURPOSE_NOT_FULLY_VERIFIED` | URL is real/official but exact purpose could not be fully verified |
| `NOT_VERIFIED` | Could not be verified; carries no URL |

Rules applied during research:

1. Use **only** sources actually verified. No URL is reconstructed from memory.
2. Never invent a URL. Never substitute a third-party site for an official one.
3. A current page existing does **not** imply historical data exists.
4. NMC approved/annual intake and MCC/state counselling seats are distinct and
   are **not** treated as automatically equivalent.
5. Candidate PII is out of scope and is never collected or documented.

Research / access date for all sources recorded in this layer: **2026-08-12**.
