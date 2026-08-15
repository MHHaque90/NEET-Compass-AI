# Data Lineage

> Sprint 3.0. Documented pipeline lineage. **Architecture documentation only —
> the pipeline is not implemented in this sprint.**

## Lineage chain

```
Official Source
      ↓
Source Document
      ↓
Source File
      ↓
SHA-256
      ↓
Source Contract
      ↓
Adapter
      ↓
Canonical Model
      ↓
Database
      ↓
Historical Dataset
      ↓
Prediction Engine
```

## Stage responsibilities

| Stage | Responsibility |
|-------|----------------|
| Official Source | Authority that publishes the data (registry: `config/data_sources.yaml`) |
| Source Document | A specific publication from the source (e.g. a seat matrix PDF, a college list) |
| Source File | The downloaded artifact on disk |
| SHA-256 | File identity / deduplication checksum recorded in the `source_files` table |
| Source Contract | Declared structure of the source file (`etl/contracts`) |
| Adapter | Transforms the external representation to canonical form |
| Canonical Model | Source-independent data representation |
| Database | Persisted canonical data |
| Historical Dataset | Versioned, curated history used for prediction training |
| Prediction Engine | Consumes the historical dataset |

## Lineage rules

- Every record in the database must be traceable back to a source file and its
  SHA-256 checksum.
- A source file is not usable until it passes its contract validation.
- Adapters must never leak external field names into canonical models.
- Historical datasets are derived facts, not duplicated source rows.

## Relationships to existing modules

- **Registry → source_files:** the registry identifies the authority; the ETL
  `source_files` table tracks each downloaded artifact (`data_source_id`,
  `checksum_sha256`, `status`).
- **Contracts:** `etl/contracts` defines `SourceContract`, `ContractRegistry`,
  `ContractValidator`, and `SourceAdapter` as the contract/adapter stages above.
- **Canonical models:** `etl/contracts/canonical` hosts source-independent
  models and the SHA-256 `checksum` helper.
- **ETL:** `docs/ETL_SPEC.md` describes how ETL runs; this document describes
  where data comes from and how it flows. Do not merge the two.

## Scope note

This document is architecture only. No pipeline, adapter, scraper, or ETL job
is created as part of this sprint.
