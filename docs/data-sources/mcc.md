# MCC — Medical Counselling Committee

> Sprint 3.0. Official sources for the all-India quota (AIQ) NEET UG counselling
> process.

## Verified sources

| Registry ID | Official URL | What it provides | Verification |
|-------------|--------------|------------------|--------------|
| `mcc_official_base` | https://mcc.nic.in/ | Base portal for all-India quota counselling publications | VERIFIED |
| `mcc_ug_counselling` | https://mcc.nic.in/ug-medical-counselling/ | NEET UG counselling — seat matrix, information bulletin, allotment result, vacancy, joined candidates, participating institutes, round info | VERIFIED |
| `mcc_ug_archive` | https://mcc.nic.in/archive-ug/ | Historical releases (2021–2025) — bulletins, seat matrices, allotment results, vacancies, joined lists, schedules | VERIFIED |
| `mcc_ug_participating_institutes` | https://mcc.nic.in/ug-medical-counselling/ | Participating institutes report (dynamic); 2025 + 2026 verified | VERIFIED |

## What was verified (access date 2026-08-12)

- `mcc.nic.in` is the official Medical Counselling Committee portal (statutory
  body under the Ministry of Health and Family Welfare).
- The UG counselling page at `mcc.nic.in/ug-medical-counselling/` is live and
  was observed (2026-08-09) publishing:
  - **NEET UG Counselling 2026 Round 1** registration open.
  - **Seat Matrix NEET UG MBBS BDS & BSc Nursing Round 1** (PDF).
  - **UG Information Bulletin 2026**.
- The archive at `mcc.nic.in/archive-ug/` was verified (2026-08-09, three-day
  crawl): seat matrices, allotment results, vacancy documents, and information
  bulletins are present for **every** year 2021–2025. Joined/admitted candidate
  lists were found for 2021, 2024 and 2025 (not for 2022–2023).
  See `mcc-historical-dataset-matrix.md` for the year-by-year matrix.

## Live verification (Sprint 3.1A, access date 2026-08-12)

A controlled re-check (`scripts/mcc_live_probe.py`, evidence manifest
`data/raw/evidence/2026-08-12/mcc_live_evidence.json`) confirmed:

- **Reachable:** first-contact GETs to `mcc.nic.in/` and
  `mcc.nic.in/archive-ug/` both returned **HTTP 200** with `text/html`.
- **Automated download blocked:** repeat full downloads from the same session
  were rejected with **HTTP 403 (Forbidden)** by the server's bot protection.
  Treat automated bulk download of MCC resources as blocked/unverified; fetch
  through an interactive session or a verified mirror, or place the file
  manually with its checksum recorded (see `docs/etl/mcc.md`).

## Publication types (MCC standard outputs)

MCC publishes the following document families on the UG counselling page and
archive. The families listed are **individually** verified for 2021–2025 via
the archive (bulletins, seat matrices, allotment results, vacancies, joined
lists for 2021/2024/2025, schedules). Participating-institute reports are
verified for 2025 (archive link) and 2026 (live report).

- Seat matrix (per round)
- Information bulletin
- Allotment result
- Vacancy
- Joined candidates
- Participating institutes
- Round information / schedule

### Provisional vs final vs revised

MCC does publish multiple versions of documents (e.g. provisional allotment,
final allotment, revised/final seat matrix). The archive contains both
provisional and final versions for most years (e.g. 2021/2024/2025 stray
rounds published provisional then final). Still, only rely on a document that
the official source itself labels (e.g. "Final Result"); treat anything else
as provisional.

## Course applicability

MBBS, BDS, and BSc Nursing (the 2026 Round 1 seat matrix includes BSc Nursing).

## Counselling scope

ALL_INDIA — the 15% all-India quota and all centrally administered seats
(AIIMS, JIPMER, ESIC, AMU, BHU and other central/deemed categories that MCC
administers).

## Historical availability

See historical-availability.md for the year-by-year matrix. Archive verified
2026-08-09: seat matrix, allotment result, vacancy, and bulletin document
families are available for every year 2021–2025; joined/admitted lists for
2021, 2024, 2025; participating institute reports for 2025–2026. The 2026
cycle is partially available (Round 1 seat matrix, bulletin, schedules).

## Notes / limitations

- MCC seat counts are **counselling seats**, not NMC-approved intake.
- `mcc_nic` records are the single authority for AIQ allotment and seat matrix
  (see source-conflicts.md).
- Allotment deliverables are published as human-readable PDF (and some Excel)
  reports; a true machine-readable per-round allotment **CSV** has not been
  confirmed from the official archive. The `allotments` source contract targets
  the well-known MCC allotment-CSV schema but its **real source file is
  UNVERIFIED** (server blocked automated downloads on 2026-08-12).
- Allotment result / joined-candidate files contain candidate PII — keep them
  out of any dataset (see mcc-historical-dataset-matrix.md).
