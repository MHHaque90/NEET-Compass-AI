# MCC ETL pipeline — operational notes

> Sprint 3.1A. How the contract-driven MCC ingestion path behaves in practice,
> which official URLs exist, and the reality of downloading from the live MCC
> server. The contract framework itself is documented in Sprint 3.1
> (`../sprints/sprint-003.1.md`).

## Pipeline shape

```
MCC source file (PDF table / CSV)
        |  parsers.parse_csv  |  parsers.extract_seat_matrix_rows
        v
   raw rows (external columns)
        |  ContractValidator.validate_columns  (STRICT/COMPATIBLE)
        v
   MCC*Adapter.transform  ->  canonical records (+ provenance metadata)
        |  ContractValidator.validate_records  (type, range, enum, unique)
        v
   Loader.upsert  (dedup by composite key)   +   FileRegistry.register(checksum)
```

* `etl.contracts.sources.mcc.pipeline` — orchestration, `FileRegistry` /
  `Loader` ports and their in-memory implementations.
* `etl.contracts.sources.mcc.download` — stdlib-only downloader with
  Content-Type validation, HTTP status semantics and a metadata `probe`
  (Sprint 3.1A hardening, see `docs/etl/provenance.md`).
* `etl.contracts.sources.mcc.provenance` — SHA-256 checksums, deterministic
  `source_file_id`, full provenance metadata.

## Official MCC URLs (from `config/data_sources.yaml`)

| Registry ID | URL | Status (2026-08-12) |
|-------------|-----|----------------------|
| `mcc_official_base` | https://mcc.nic.in/ | VERIFIED, live (HTTP 200, text/html on first contact) |
| `mcc_ug_counselling` | https://mcc.nic.in/ug-medical-counselling/ | VERIFIED, live |
| `mcc_ug_archive` | https://mcc.nic.in/archive-ug/ | VERIFIED, live (HTTP 200 on first contact) |

Only these three MCC URLs are verified in the registry. Individual
allotment-result, vacancy and joined-candidate file URLs were **not**
separately verified and must not be used as trusted deep links yet.

## Live download reality (evidence, Sprint 3.1A)

The controlled live check (`scripts/mcc_live_probe.py`, exact evidence manifest
in `data/raw/evidence/2026-08-12/mcc_live_evidence.json`) found:

1. **First contact:** two lightweight GETs to `mcc.nic.in/` and
   `mcc.nic.in/archive-ug/` returned **HTTP 200, `text/html`** — the pages are
   the live official MCC pages, reachable from this network.
2. **Automated full download:** repeat GETs from the same session were rejected
   with **HTTP 403 (Forbidden)** by the server's bot protection. The hardened
   downloader fails fast on 4xx (permanent condition) — no retry storm.

**Consequence:** automated bulk download of MCC files from this environment is
**BLOCKED/unverified**. Any real MCC allotment/seat-matrix file must be
reached either (a) through an interactive session that satisfies the
anti-bot check, (b) a verified mirror, or (c) manual placement of the file into
`data/raw/` with checksum recorded. The pipeline *contracts* are unaffected —
they validate whatever file is handed to them — but the **real source file for
the 2025 allotments contract is currently UNVERIFIED**.

Worksheet for a future interactive download: after retrieving a file, run it
through the pipeline and record:
`url, checksum (sha256), size, content_type, retrieval_timestamp` — matching
the fields the manifest records (see `docs/etl/provenance.md`).

## Network discipline for tests

* No test in the suite performs a network call; HTTP is mocked with
  `FakeResponse` fixtures and local files use `file://`.
* The one allowed live interaction is the manual, one-shot
  `scripts/mcc_live_probe.py` — hardcoded to the three verified URLs, no link
  crawling, no scheduling. Do not turn it into a CI dependency.