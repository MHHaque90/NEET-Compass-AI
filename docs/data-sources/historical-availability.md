# Historical Availability

> Sprint 3.0. Year-by-year availability for each important source/dataset where
> evidence exists. A current page existing does **not** imply historical data
> exists.

## Status legend

| Status | Meaning |
|--------|---------|
| `AVAILABLE` | Evidence confirms the dataset is published for that year |
| `PARTIAL` | Only part of the dataset/cycle is available or verified |
| `NOT AVAILABLE` | Confirmed not available |
| `NOT VERIFIED` | No verification performed / no evidence recorded |

Research / access date: **2026-08-12**.

## Matrix

| Source / dataset | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|------------------|------|------|------|------|------|------|
| MCC — seat matrix (AIQ) | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE (Round 1) |
| MCC — information bulletin | AVAILABLE | AVAILABLE | AVAILABLE (revised) | AVAILABLE | AVAILABLE | AVAILABLE |
| MCC — allotment result | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | NOT VERIFIED (counselling in progress) |
| MCC — vacancy / clear-vacancy | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | NOT VERIFIED (in progress) |
| MCC — joined / admitted candidates | AVAILABLE | NOT FOUND | NOT FOUND | AVAILABLE | AVAILABLE | NOT VERIFIED (in progress) |
| MCC — participating institutes | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | AVAILABLE | AVAILABLE |
| MCC — archive (2021–2025) | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | — |
| NTA — NEET UG bulletin/result | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | PARTIAL (portal live; datasets not verified) |
| NMC — MBBS college list | NOT VERIFIED | NOT VERIFIED | AVAILABLE (2023-24 list) | AVAILABLE (2024-25 list) | NOT VERIFIED | NOT VERIFIED |
| NDC — dental colleges list | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| State authorities (11 verified) | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | PARTIAL (portals live; per-year datasets not verified) |
| Central institutions (AIIMS/BHU/JIPMER) | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |

## Notes

- **MCC archive:** verified 2026-08-09 via `mcc.nic.in/archive-ug/` (three-day
  crawl). Seat matrices, allotment results, vacancy documents, and information
  bulletins are present for every year 2021–2025. See
  `mcc-historical-dataset-matrix.md` for the per-year evidence.
- **MCC joined/admitted lists:** found for 2021 (`round 1 and 2 joined
  candidates list`), 2024 (`all admitted candidates list`) and 2025 (`admitted
  joined candidates list up to round 3`). Not found in the archive fetch for
  2022 and 2023.
- **MCC participating institutes:** 2025 report linked from the archive; 2026
  report generated dynamically on the live page. Not found for earlier years.
- **NMC college list:** the "List of Medical Colleges Teaching MBBS" page
  publishes one list per admission year. Lists for **2023-24** and **2024-25**
  were verified. Earlier-year lists were not verified.
- **MCC 2026:** the 2026 Round 1 seat matrix, the UG information bulletin, and
  round schedules were verified. Allotment/vacancy/joined documents for 2026
  are NOT VERIFIED (counselling in progress as of 2026-08-12).
- **States:** 11 state portals were verified as live; none of their per-year
  seat matrices or allotment datasets were individually verified.
- **Everything else is NOT VERIFIED** — do not populate a historical dataset
  from assumptions.

## Consequence for prediction

A historical dataset covering 2021–2025 **can** now be constructed from the
verified MCC archive for seat matrices, allotments, vacancies, and bulletins
(plus joined lists for 2021/2024/2025). Any such dataset must record its year
coverage and per-document verification state. Candidate PII (names, roll
numbers, scores/ranks) is out of scope — use only institute/course/quota/
category-level aggregations.
