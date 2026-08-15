# Provenance model for sourced data

> Sprint 3.1A. Every real source record carries a complete, auditable
> provenance chain; file identity is content-driven; the URL is recorded as
> provenance, never used as identity.

## Why content identity, not URL identity

MCC republishes and supersedes documents (provisional -> final -> revised).
Two different URLs, or the same URL fetched on different days, can serve the
same or changed bytes. Identity must therefore derive from **bytes**, not from
the URL:

* `sha256(content)` -> deterministic `source_file_id`
  (`{source_id}_{dataset}_{effective_year}_{checksum[:12]}`).
* The same bytes always produce the same `source_file_id`, regardless of when
  or from where they were retrieved — re-ingestion is detected by checksum
  before any row is transformed.
* The URL is recorded alongside as `source_url` so an auditor can see *where*
  the bytes came from, without the URL participating in identity decisions.

This is why the MCC pipeline can re-run the identical file three times and
write zero duplicate rows, yet still treat a *changed* file at the same URL as a
new source (see `docs/etl/idempotency.md`).

## The full taxonomy

`etl.contracts.canonical.SourceMetadata` (canonical model; `source_url` added
in Sprint 3.1A, backwards compatible) carries:

| Field | Meaning | Populated by |
|-------|---------|--------------|
| `source_id` | Registry id of the authority (e.g. `mcc`) | contract |
| `authority` | Human-readable body (e.g. `MCC / DGHS`) | contract |
| `dataset` | e.g. `seat_matrix`, `allotments` | contract |
| `effective_year` | Counselling cycle the file belongs to | contract |
| `publication_version` | The round (e.g. `Round 1`, `Round 3`) — this field *is* the round | contract |
| `contract_version` | Version of the source contract applied (e.g. `1.1.0`) | contract, stringified |
| `source_url` | URL the file was retrieved from | pipeline caller (`ingest_*(..., source_url=...)`) |
| `file_checksum` | SHA-256 of the file bytes | provenance |
| `source_file_id` | Deterministic file identity derived from the checksum | provenance |
| `parser_version` | Parser/adapter generation that produced the records | provenance (`mcc_etl_v1`) |
| `retrieval_timestamp` | UTC ISO-8601 ingestion time | provenance |

Guarantee enforced by tests (`test_provenance_taxonomy_is_complete`): a source
record is never accepted with any of the above missing.

## Round representation

There is no separate `round` column on source metadata: `publication_version`
carries it (`"Round 3"`). Per-row round is a canonical record field
(`Allotment.round_id`), distinct from the round of the file that supplied it.

## Full-chain example

```
ingest_allotments(path.csv, registry, loader, source_url="https://mcc.nic.in/archive-ug/...")
  -> SourceMetadata(
       source_id="mcc", dataset="allotments", effective_year=2025,
       publication_version="Round 3", contract_version="1.1.0",
       source_url="https://mcc.nic.in/archive-ug/...",
       file_checksum="7f3c…", source_file_id="mcc_allotments_2025_7f3c…",
       parser_version="mcc_etl_v1", retrieval_timestamp="2026-08-12T15:13:25Z")
```

## Reading a checksum back

* File: `etl.contracts.sources.mcc.provenance.file_checksum(path)`.
* Bytes: `bytes_checksum(data)`.

Both must agree for the same content, which is what the pipeline asserts
implicitly by short-circuiting on the registry's checksum.