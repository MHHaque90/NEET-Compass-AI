# Central Institutions

> Sprint 3.0. Officially verified central/institutional sources. This document
> is the **source-of-truth research layer**. These institutions are **not**
> hard-coded into application business logic — the registry is the reference.

## Verified sources (access date 2026-08-12)

| Registry ID | Institution | Official URL | What it provides | Verification |
|-------------|-------------|--------------|------------------|--------------|
| `central_aiims_admissions` | AIIMS Admissions | https://www.aiimsexams.ac.in/ | AIIMS admissions portal | VERIFIED |
| `central_bhu` | Banaras Hindu University | https://www.bhu.ac.in/ | BHU university portal | VERIFIED |
| `central_jipmer` | JIPMER | https://jipmer.edu.in/ | JIPMER institute portal | VERIFIED |

## Notes on the verified institutions

- **AIIMS** — AIIMS MBBS UG seats are now filled through **NEET UG + MCC
  counselling**. The admissions portal covers the institutional process; the
  seat allotment authority is MCC.
- **BHU** — BHU Institute of Medical Sciences MBBS seats are filled through
  NEET UG + MCC counselling.
- **JIPMER** — JIPMER MBBS seats are filled through NEET UG + MCC counselling.

## MCC-administered central/institutional categories

MCC administers counselling for central government institutions and certain
deemed/deemed-to-be universities. Categories that were verified to exist under
the MCC umbrella (from the MCC UG counselling page): all-India quota,
AIIMS-like central institutions, and Delhi-based institutions. The following
specific institutional sources could **not** be verified this pass and remain
**NOT VERIFIED** at the registry level:

| Registry ID | Institution | Verification |
|-------------|-------------|--------------|
| `central_amu` | Aligarh Muslim University (AMU) | NOT_VERIFIED |
| `central_esic` | ESIC medical institutions | NOT_VERIFIED |
| `central_delhi_institutions` | Delhi institutions (MCC-administered) | NOT_VERIFIED |

## Course applicability

MBBS (UG) via NEET UG.

## Scope

INSTITUTIONAL — these are institution-specific sources, distinct from the
all-India quota (MCC) and state-quota sources.

## Historical availability

See historical-availability.md. Not verified for any specific year.

## Design rule

Do **not** embed this institutional list into application code. Application
behaviour must be driven by the registry (`config/data_sources.yaml`) and the
docs in this directory, which are the single reference layer.
