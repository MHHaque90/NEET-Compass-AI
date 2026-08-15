# Sprint Report: Sprint 3.1A

## Sprint Goal

Verification and hardening pass for the MCC national-quota path: confirm the
verified MCC official URLs are live from this sandbox, prove the ingestion
pipeline is idempotent across repeated runs against a *real* source identity,
harden the downloader (Content-Type and HTTP-status semantics so a surrogate
PDF can never be ingested as a CSV, and a retry storm can never follow a 403),
carry `source_url` through provenance end-to-end, and give an honest,
evidence-based account of the PostgreSQL integration status.

No architectural rewrite: no new canonical models, no changes to the domain
`app.domain.*` models, and no new repository interfaces. Everything below
hardenes the existing `etl.contracts.sources.mcc` contract pilot from Sprint
3.1 and documents reality.

## Objective-by-objective evidence (tour of the sandbox)

### 1. Database integration — honest status: BLOCKED (auth), SQL verified by compilation

Gathered:

* PostgreSQL **17 is running** on `localhost:5432` (service
  `postgresql-x64-17`), port open; `psycopg 3.3.4` and `sqlalchemy 2.0.51`
  installed.
* The **credentials on file**
  (`postgresql+psycopg://neet:neet_dev_password@localhost:5432/neet_compass`,
  in `app/core/config.py`, `.env.example` and `docker-compose.yml`) are
  **rejected** by that server:
  `FATAL: password authentication failed for user "neet"`.
* There is **no `.env`** override in the checkout.
* The backend integration suite (`backend/tests/integration/`) **hangs** in
  this environment rather than passing; its conftest silently falls back to
  in-memory SQLite, which could **mask** a missing/denied PostgreSQL.

Resolution without changing credentials or starting Docker DB: the production
`AllotmentLoader` upsert is verified at the SQL layer. A new hermetic test
compiles the loader's statement on the PostgreSQL dialect and asserts
`INSERT INTO allotments ... ON CONFLICT ON CONSTRAINT
uq_allotments_college_round_cohort DO NOTHING`
(`tests/unit/infrastructure/etl/test_allotment_loader_sql.py`). Real
round-trip integration remains **BLOCKED** pending a working `DATABASE_URL`.

### 2. Controlled download of one small official MCC resource — BLOCKED by server (honest result)

`scripts/mcc_live_probe.py` (hardcoded to the two verified MCC URLs) ran the
hardened downloader against the live server:

* First contact: both `https://mcc.nic.in/` and `https://mcc.nic.in/archive-ug/`
  returned **HTTP 200, `text/html`** — URLs VERIFIED live, network open.
* Follow-up automated downloads from the same session: **HTTP 403 Forbidden**
  (server bot protection). The downloader failed fast on the 4xx (no retry
  storm, as per the hardened semantics).

Evidence: `data/raw/evidence/2026-08-12/mcc_live_evidence.json`. Outcome
recorded in the registry (`config/data_sources.yaml`) and data-source docs:
**automated bulk download of MCC files from this sandbox is
BLOCKED/unverified**; the three MCC URLs remain VERIFIED as live pages.

### 3. Allotment CSV — CONTRACT READY, REAL SOURCE UNVERIFIED

The official archive serves allotment-result and vacancy documents as **PDF**
(with some Excel). A machine-readable per-round allotment **CSV** could not be
confirmed from the official archive; file-level census is additionally
blocked by the 403. The `allotments` source contract (schema fixed, PII
excluded) remains the well-known MCC allotment-CSV schema; the real source
file for the 2025 allotments dataset is **UNVERIFIED** until meeting either an
interactive-session download, a verified mirror, or a manually placed file
(with checksum recorded).

### 4. Downloader hardening (no rewrite)

`etl/contracts/sources/mcc/download.py` now supports:

* `expected_content_types` — Content-Type validation; a mismatch (or a missing
  header) raises `DownloadRejectedError` **without writing the surrogate file**
  to disk.
* HTTP status semantics — 4xx (incl. 403) fails **immediately** (permanent);
  5xx and `URLError`/`OSError` retry with backoff.
* `probe()` — single-request metadata capture (status / content-type /
  content-length / final URL) used by the evidence script and by
  `is_downloadable`.
* Verified default per-attempt timeout (30 s) preserved.

### 5. Idempotency across three runs — proven at the port layer, SQL verified

New test `test_three_runs_same_source_url_changed_bytes`:

* Run 1: ingest file -> 8 rows.
* Run 2: identical bytes, same URL -> short-circuits on checksum; **zero**
  duplicate writes.
* Run 3: *changed* bytes at the **same URL** -> new checksum -> new
  `source_file_id`; 7 rows merge in place, the republished category adds 1 key
  (store 8 -> 9); no duplicates, no lost ingestion.

Production SQL verified with the compiled `ON CONFLICT DO NOTHING` (objective
1). See `docs/etl/idempotency.md`.

### 6. Provenance completeness

`source_url` now flows end-to-end: canonical `SourceMetadata.source_url`
(optional, backwards compatible), `provenance.build_metadata(..., source_url=)`,
and `ingest_seat_matrix/ingest_allotments(..., source_url=)`. A taxonomy test
asserts a source record always carries source_id, dataset, year, round
(`publication_version`), contract_version, `source_url`, checksum,
`source_file_id`, parser_version and retrieval timestamp. See
`docs/etl/provenance.md`.

### 7. Repository validation

`source_url` added to a canonical model; no **new** canonical models, no
`app.domain.*` changes, no repository edits. New tests: 13 downloader tests
(HTTP semantics), provenance tests, the 3-run idempotency test, and the
loader SQL-compile test. Full metrics below.

## Deliverables

| Item | Status |
|------|--------|
| `etl/contracts/sources/mcc/download.py` hardening | Done |
| `source_url` through `canonical.SourceMetadata` + `provenance` + `pipeline` | Done |
| Downloader tests (content-type, status/retry, timeout, probe) | Done (13) |
| Provenance taxonomy + source_url tests | Done |
| 3-run same-URL/checksum idempotency test | Done |
| Production loader SQL-compile test (ON CONFLICT DO NOTHING) | Done |
| `scripts/mcc_live_probe.py` + evidence manifest | Done |
| Docs: `docs/etl/{mcc,provenance,idempotency}.md` | Done |
| Docs updated: `docs/data-sources/mcc.md`, `mcc-historical-dataset-matrix.md`, `config/data_sources.yaml` | Done |

## Key Outcomes

| Metric | Sprint 3.1 | Sprint 3.1A |
| --- | --- | --- |
| MCC contract-protected datasets | 2 | 2 |
| New downloader tests | 4 | 17 |
| Provenance completeness (source_url) | absent | carried + asserted |
| 3-run source-identity test | absent | present |
| Live MCC verification | n/a | 200 first-contact / 403 automation-block, evidenced |
| Real PostgreSQL round-trip | not exercised | BLOCKED (auth), SQL verified by compilation |

## Risks & Mitigations

1. **Automated MCC downloads blocked (HTTP 403).** The real allotment source
   file for 2025 is UNVERIFIED. Mitigation: documented interactive-session /
   verified-mirror / manual-file workflow with checksum recording
   (`docs/etl/mcc.md`) + the registry updated to stop treating file URLs as
   verified.
2. **PostgreSQL credentials rejected; integration suite hangs and can fall
   back to SQLite invisibly.** Mitigation: BLOCKED recorded honestly, loader
   SQL verified by compilation, sqlite fallback flagged in docs.
3. **No `__main__.py` in the repo.** The "contract-version check" was done on
   the code path instead: `contract_version=1.1.0` asserted as part of the
   provenance taxonomy test, and `ingest_*` embeds the contract version in
   every batch's metadata.

## Sprint Retrospective

The honest verification paid off twice: the live probe proved both that the
MCC pages are truly live and that automated download of the *actual* data is
blocked — which is the difference between "URL verified" and "dataset
ingested", and it stops us building on a fabricated source. The downloader
hardening (`DownloadRejectedError`, 4xx-fail-fast) was validated against the
real 403 in the same session. The idempotency 3-run test crystallised the
content-identity-vs-URL-identity rule that the metric engine's year-over-year
features will depend on.