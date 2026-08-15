# NMC — National Medical Commission

> Sprint 3.0. Official sources for MBBS college identity, recognition, intake,
> management, university, state, and status.

## Verified sources

| Registry ID | Official URL | What it provides | Verification |
|-------------|--------------|------------------|--------------|
| `nmc_college_list` | https://www.nmc.org.in/information-desk/colleges-teaching-mbbs/ | List of Medical Colleges Teaching MBBS per NEET UG admission year (PDF) | VERIFIED |
| `nmc_medical_colleges` | https://www.nmc.org.in/medical-colleges/ | Searchable list of medical colleges (recognition, management, university, state, status) | VERIFIED |
| `nmc_eligibility` | https://www.nmc.org.in/information-desk/medical-college-department/ | MBBS admission eligibility criteria; link to the MBBS college list | VERIFIED |

## What was verified (access date 2026-08-12)

- `nmc.org.in` is the official National Medical Commission portal (apex
  regulatory body for medical education in India, MoHFW).
- The "List of Medical Colleges Teaching MBBS" page publishes lists for
  admission years 2023-24 and 2024-25. Verified example PDF:
  `media.nmc.org.in/public/uploads/medical-college-list/NEET UG MBBS
  adm_2024-25 College List.pdf`.
- The medical-college search page and the medical-college department page
  (amended MBBS eligibility criteria) are live.

## Fields NMC is authoritative for

- College identity (name, code as used by NMC)
- Medical course recognition (MBBS)
- **Annual / approved intake**
- Management type
- University affiliation
- State
- College status

## Critical distinction — NMC intake vs counselling seats

**NMC annual/approved intake** and **MCC/state counselling seats** are different
quantities and MUST NOT be treated as automatically equivalent:

- NMC intake = the sanctioned/approved annual MBBS seats at a college.
- MCC/state seats = seats offered in a specific counselling round (can differ
  due to seat matrix cuts, non-participating colleges, institutional quota
  carve-outs, etc.).

Ownership: NMC for approved intake; MCC/state authority for counselling seats
(see source-conflicts.md).

## Course applicability

MBBS (undergraduate medical education).

## Historical availability

See historical-availability.md. Published lists verified for 2023-24 and
2024-25; earlier years NOT VERIFIED (do not assume earlier PDFs exist from the
current page).

## Notes / limitations

- NMC list is the institution master; it is not a per-round seat matrix.
- The search page is best viewed in Chrome (NMC recommendation).
