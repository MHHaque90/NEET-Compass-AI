# Maharashtra (MAH CET Cell) ETL Pipeline — Operational Notes

> Sprint 3.2. Contract-driven state-counselling ingestion path for the
> Maharashtra MAH CET Cell, PII-free seat-matrix and allotment datasets.

## Pipeline shape

```
Maharashtra source file (CSV)
        |  parsers.parse_csv
        v
   raw rows (external columns)
        |  ContractValidator.validate_columns  (STRICT/COMPATIBLE)
        v
Maharashtra*Adapter.transform  ->  canonical records (+ provenance metadata)
        |  ContractValidator.validate_records  (type, range, enum, unique)
        v
   Loader.upsert  (dedup by composite key)   +   FileRegistry.register(checksum)
```

* `etl.contracts.sources.maharashtra.contracts` — seat_matrix_2026_contract,
  allotments_2026_contract
* `etl.contracts.sources.maharashtra.adapters` — MaharashtraSeatMatrixAdapter,
  MaharashtraAllotmentsAdapter
* `etl.contracts.sources.maharashtra.pipeline` — orchestration, FileRegistry /
  Loader ports and their in-memory implementations.
* `etl.contracts.sources.maharashtra.provenance` — SHA-256 checksums,
  deterministic source_file_id, full provenance metadata.

## Official URLs (from `config/data_sources.yaml`)

| Registry ID | URL | Status (2026-08-12) |
|-------------|-----|----------------------|
| `mcc_state_maharashtra` | https://cetcell.mahacet.org/ | VERIFIED, live (HTTP 200, text/html on first contact) |

Only these URLs are verified in the registry. Individual deep-link file URLs
were not separately verified and must not be used as trusted links yet.

## Live download reality (Sprint 3.2 hardening)

The controlled live check found:

1. **First contact:** GET to `cetcell.mahacet.org` returned **HTTP 200, `text/html`**
   — the page is the live official authority page, reachable from this network.
2. **Automated full download:** repeat GETs from the same session were **not**
   blocked by bot protection (unlike the MCC experience), but the pipeline
   contracts are designed so that any file handed to them is validated regardless
   of download source — the contract framework is unaffected by download
   availability.

Worksheet for a future interactive download: after retrieving a file, run it
through the pipeline and record: `url, checksum (sha256), size, content_type,
retrieval_timestamp`.

## Network discipline for tests

* No test in the suite performs a network call; CSV fixtures use `file://`.
* The pipeline contracts validate whatever file is handed to them — they are
  agnostic to download method.