# MCC Historical Dataset Matrix

> Sprint 3.0. Verification matrix of the MCC UG counselling archive
> (`https://mcc.nic.in/archive-ug/`) against the canonical document families
> per counselling year. This is the evidence base for any historical dataset
> built for the prediction engine.

## Status

| Item | Value |
|------|-------|
| Archive URL | https://mcc.nic.in/archive-ug/ |
| Access / archive-fetch date | 2026-08-09 (three-day crawl of the archive listing) |
| Archive verification | VERIFIED |
| Layer | MCC (`mcc_ug_archive`) — see source-registry.md |

## Verification legend

| Status | Meaning |
|--------|---------|
| `AVAILABLE` | Document family confirmed present in the archive for that year |
| `PARTIAL` | Present, but only part of the family (e.g. missing final/thematic variant) |
| `NOT FOUND` | Not present in the fetched archive listing for that year |
| `NOT VERIFIED` | No verification recorded |

## Matrix

| Document family | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|-----------------|------|------|------|------|------|------|
| Information bulletin | AVAILABLE | AVAILABLE | AVAILABLE (revised) | AVAILABLE | AVAILABLE | AVAILABLE (on live page) |
| Seat matrix | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE (Round 1) |
| Allotment result | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | NOT VERIFIED (in progress) |
| Vacancy / virtual-& clear-vacancy | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | NOT VERIFIED (in progress) |
| Joined / admitted candidates | AVAILABLE | NOT FOUND | NOT FOUND | AVAILABLE | AVAILABLE | NOT VERIFIED (in progress) |
| Round info / schedule | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE | AVAILABLE (schedules published) |
| Participating institutes | NOT FOUND | NOT FOUND | NOT FOUND | NOT FOUND | AVAILABLE | AVAILABLE |

Rows: each row is one verified document family, each cell is the archive
evidence found during the 2026-08-09 fetch.

## File formats served (Sprint 3.1A note)

* All archived allotment-result, vacancy, and joined/admitted documents are
  served as **PDF** (with some Excel variants reported for participating
  institutes). No per-round machine-readable allotment **CSV** has been
  confirmed on the official archive.
* Consequently the `allotments` contract is **contract-ready** (schema fixed,
  PII-excluded) but its **real source file is UNVERIFIED**.
* Re-verification on 2026-08-12 confirmed the archive page is live (HTTP 200
  on first contact) but automated downloads were rejected with HTTP 403 by
  the server's bot protection (`scripts/mcc_live_probe.py` +
  `data/raw/evidence/2026-08-12/mcc_live_evidence.json`), so the per-year
  link census was not re-fetched programmatically.

## Verified year detail

### 2021
- Bulletin: `UG Information Bulletin 2021` (uploads/2022/05/2022053192.pdf).
- Seat matrix: round-1 family matrices — DU-IP (Utkarsh), AMU, Jamia, Deemed,
  ESIC, B.Sc Nursing, AIIMS/JIPMER/BHU MBBS, AIQ MBBS/BDS.
- Allotment: Final result Round 1, Final result Round 2, Mop-up final, Stray
  vacancy final.
- Vacancy: Virtual vacancy round 2, Clear vacancy round 2, vacant seats for
  mop-up, stray round seats.
- Joined: `ROUND 1 AND ROUND 2 JOINED CANDIDATES LIST UG 2021`
  (uploads/2022/06/2022060614.pdf).
- Round data: extension notices; round structure observed R1 → R2 → Mop-up →
  Stray.

### 2022
- Bulletin: `UG Information Bulletin 2022` (uploads/2023/06/2023061295-1.pdf).
- Seat matrix: final round-1 matrices — B.Sc nursing, central universities BDS,
  Jamia BDS, deemed BDS, AIQ BDS, AIIMS MBBS, JIPMER, ESIC, deemed MBBS, central
  MBBS; plus 2nd mop-up and stray matrices.
- Allotment: Final result R1, Final result R2, Mop-up, 2nd mop-up (BDS/B.Sc),
  stray vacancy round.
- Vacancy: Virtual vacancy round 2, Clear vacancy round 2, mop-up vacant seats,
  2nd mop-up vacant seats.
- Joined: NOT FOUND in archive fetch.
- Round data: round/extension notices; structure observed R1 → R2 → Mop-up →
  2nd Mop-up (BDS/B.Sc) → Stray.

### 2023
- Bulletin: `Revised UG Information Bulletin -2023`
  (uploads/2023/07/2023080167.pdf).
- Seat matrix: final R1 matrices (ESIC, central universities, AIIMS, JIPMER,
  AIQ MBBS/BDS, deemed); newly-added seats R2/R3; seat-matrix R3; round 5
  BDS/B.Sc matrix.
- Allotment: Final result R1, Final result R3, stray vacancy round result,
  round 5 BDS/B.Sc final, 2nd mop-up BDS.
- Vacancy: Virtual vacancy round 3, Clear vacancy round 3, clear stray vacancy,
  round 5/6 vacancies.
- Joined: NOT FOUND in archive fetch.
- Round data: delay/schedule notices; structure observed R1 → R2 → R3 → Stray →
  R5 (BDS/B.Sc) → 2nd Mop-up (BDS), plus Special Stray MBBS.

### 2024
- Bulletin: `UG information Bulletin 2024` (uploads/2024/08/2024081939.pdf).
- Seat matrix: final R1 matrices (AIQ MBBS/BDS, central universities MBBS/BDS,
  deemed, B.Sc nursing, AIIMS, ESIC, JIPMER); special-stray round matrices.
- Allotment: Final result R1, Final result R2, Final result R3, stray vacancy
  final allotment, special stray provisional + final.
- Vacancy: Clear vacancy round 2, Virtual vacancy round 2, clear stray vacancy,
  vacant seats for special stray, JIPMER vacant seat.
- Joined: `All Admitted candidates list for UG 2024`
  (uploads/2024/12/2024120658.pdf).
- Round data: special-stray schedules (I, II, III); structure observed
  R1 → R2 → R3 → Stray → Special Stray I/II/III.

### 2025
- Bulletin: `Information Bulletin UG Counselling 2025`
  (uploads/2025/07/202509181307981517.pdf).
- Seat matrix: six final R1 matrices (AIIMS/BHU/JIPMER; AIQ except
  deemed/central; central universities; deemed; ESIC; B.Sc nursing), matrix
  verification notice, stray-round matrix, special-stray MBBS matrix, round 5
  matrix.
- Allotment: Final result R1, Final result R2, Final allotment R3, stray
  provisional + final, special stray final, R5/R6 BDS/B.Sc results.
- Vacancy: Clear vacancy R2/R3/R5, Virtual vacancy R2/R3.
- Joined: `ADMITTED JOINED CANDIDATES LIST UPTO ROUND 3 UG COUNSELLING 2025`
  (uploads/2025/11/202511031508909973.pdf).
- Round data: schedule of round 5 & 6; UG/state/AIQ schedules.
- Participating institutes: `Participating Institute Details UG 2025` (external
  report link on the archive page).
- Structure observed R1 → R2 → R3 → Stray → R5/R6 (BDS/B.Sc) → Special Stray.

### 2026
- Bulletin: `UG Information Bulletin 2026` (on the live UG counselling page).
- Seat matrix: `Seat Matrix NEET UG MBBS BDS & BSc Nursing Round 1` (live page;
  PDF verified).
- Round data: NEET UG 2026 Round 1 registration open; AIQ and state schedules
  published; `Participating Institute Details UG 2026` report accessible.
- Allotment / vacancy / joined: NOT VERIFIED — counselling in progress at access
  date 2026-08-12.

## Candidate PII boundary

- Allotment results and joined/admitted lists contain candidate-level personal
  data (candidate name, roll number, and — in some result views — rank/score).
- Candidate PII is **out of scope** (see README.md rule 5). Only the
  *institute/course/quota/category-level* aggregations may seed a dataset. Never
  store candidate names, roll numbers, or scores.
- Joined/admitted lists are a **joined** (admission) fact, distinct from the
  **allotment** fact; do not conflate the two when aggregating.

## Schema observations (verified fields)

- **Seat matrix** columns (as labelled in the 2025 stray-round embedded sheet):
  `StateName`, `Institute`, `Quota`, `Branch`, `Category`, `TotalSeats`. Same
  shape is used by the 2026 Round 1 matrix (state, college, quota, course,
  category, total seats). Institute *code* is not part of the seat matrix; it is
  supplied by the participating-institute report / NMC list.
- **Vacancy documents** reuse the seat-matrix schema (state, institute, quota,
  branch, category, vacant seats). Virtual vs clear vacancy differ in whether
  the seats are finalised; both were observed for most years.
- **Allotment result** fields (as reported by MCC result tables and verified
  third-party coverage): rank/AIR, candidate name, roll number, allotted quota,
  allotted institute, allotted course, allotted category, category remarks/PwD
  status. Name/roll/rank are PII → exclude.
- **Institute fields** (recognition, management, university, NMC code) come from
  the NMC list / participating-institute report, not from the seat matrix.

## Consequence for prediction

- Historical seat matrices and allotment results are now **verified available**
  for 2021–2025, which is the minimum span a probability model needs for
  year-over-year features. Joined lists exist for 2021, 2024, 2025 (partial).
- 2026 is in progress; only Round 1 seat matrix and bulletin are verified so far.
- Any dataset built from these documents must record `year_support` and its
  per-document verification state (see source-registry.md fields).