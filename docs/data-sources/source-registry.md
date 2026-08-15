# Source Registry — Authoritative Source Inventory

> Sprint 3.0. This document is the authoritative human-readable inventory of
> official data sources. The machine-readable mirror is
> `config/data_sources.yaml` (validated by `config/tests/test_source_registry.py`).

## Verification legend

| Status | Meaning |
|--------|---------|
| `VERIFIED` | URL confirmed and purpose/dataset confirmed during research |
| `VERIFIED_URL_PURPOSE_NOT_FULLY_VERIFIED` | URL real/official; exact purpose not fully verified |
| `NOT_VERIFIED` | Could not be verified; no URL recorded |

Research / access date: **2026-08-12**.

## Fields

| Field | Description |
|-------|-------------|
| `source_id` | Unique stable identifier (lowercase, `a-z0-9_`) |
| `source_name` | Display name of the source |
| `authority` | Owning authority / body |
| `official_url` | Verified official URL (empty for `NOT_VERIFIED`) |
| `dataset` | What the source provides |
| `scope` | `NATIONAL` / `ALL_INDIA` / `STATE_QUOTA` / `INSTITUTIONAL` |
| `course` | `MBBS` / `BDS` / `MBBS+BDS` / `MBBS+BDS+NURSING` |
| `state` | State for state authorities, else empty |
| `year_support` | Verified year coverage (does not assume history) |
| `format` | `PDF` / `XLSX` / `CSV` / `HTML` / `MULTIPLE` / `NOT_VERIFIED` |
| `authority_level` | `REGULATORY` / `EXAMINATION` / `STATE_AUTHORITY` / `CENTRAL_INSTITUTION` |
| `priority` | `P0` (core product) / `P1` (secondary) — see source-priority.md |
| `verification_status` | See legend above |
| `publication_status` | `PUBLISHED` / `NOT_VERIFIED` |
| `notes` | Limitations, caveats, corrections |

## Registry

### MCC — Medical Counselling Committee (all-India quota)

| source_id | official_url | dataset | scope | course | priority | verification |
|-----------|--------------|---------|-------|--------|----------|--------------|
| `mcc_official_base` | https://mcc.nic.in/ | Base portal for AIQ counselling publications | ALL_INDIA | MBBS+BDS+NURSING | P0 | VERIFIED |
| `mcc_ug_counselling` | https://mcc.nic.in/ug-medical-counselling/ | Seat matrix, information bulletin, allotment result, vacancy, joined candidates, participating institutes, round info | ALL_INDIA | MBBS+BDS+NURSING | P0 | VERIFIED |
| `mcc_ug_archive` | https://mcc.nic.in/archive-ug/ | Historical releases 2021–2025 (bulletins, seat matrices, allotment results, vacancies, joined lists, schedules) | ALL_INDIA | MBBS+BDS+NURSING | P1 | VERIFIED |
| `mcc_ug_participating_institutes` | https://mcc.nic.in/ug-medical-counselling/ | Participating institutes (institute, code, state, management, course) — dynamic report; 2025 + 2026 verified | ALL_INDIA | MBBS+BDS+NURSING | P1 | VERIFIED |

### NTA — National Testing Agency (NEET UG examination)

| source_id | official_url | dataset | scope | course | priority | verification |
|-----------|--------------|---------|-------|--------|----------|--------------|
| `nta_official_base` | https://www.nta.ac.in/ | Agency portal, notices, exam information | NATIONAL | MBBS+BDS | P1 | VERIFIED |
| `nta_neet_ug` | https://neet.nta.nic.in/ | Information bulletin, result, notices, statistics | NATIONAL | MBBS+BDS | P1 | VERIFIED |

### NMC — National Medical Commission (MBBS regulation)

| source_id | official_url | dataset | scope | course | priority | verification |
|-----------|--------------|---------|-------|--------|----------|--------------|
| `nmc_college_list` | https://www.nmc.org.in/information-desk/colleges-teaching-mbbs/ | MBBS college list per admission year (recognition, intake, management, university, state, status) | NATIONAL | MBBS | P0 | VERIFIED |
| `nmc_medical_colleges` | https://www.nmc.org.in/medical-colleges/ | Searchable list of medical colleges | NATIONAL | MBBS | P0 | VERIFIED |
| `nmc_eligibility` | https://www.nmc.org.in/information-desk/medical-college-department/ | MBBS eligibility criteria; MBBS college list link | NATIONAL | MBBS | P1 | VERIFIED |

### NDC — National Dental Commission (BDS regulation)

| source_id | official_url | dataset | scope | course | priority | verification |
|-----------|--------------|---------|-------|--------|----------|--------------|
| `ndc_official_base` | https://ndcindia.gov.in/ | Base portal for dental regulation | NATIONAL | BDS | P1 | VERIFIED |
| `ndc_dental_colleges` | https://ndcindia.gov.in/dental-colleges-list/ | BDS colleges — recognition, intake, status | NATIONAL | BDS | P1 | VERIFIED |

### State counselling authorities

| source_id | state | official_url | authority | priority | verification |
|-----------|-------|--------------|-----------|----------|--------------|
| `mcc_state_maharashtra` | Maharashtra | https://cetcell.mahacet.org/ | State CET Cell | P0 | VERIFIED |
| `mcc_state_karnataka` | Karnataka | https://cetonline.karnataka.gov.in/kea/ | Karnataka Examinations Authority | P0 | VERIFIED |
| `mcc_state_tamil_nadu` | Tamil Nadu | https://www.tnmedicalselection.net/ | DME Tamil Nadu | P0 | VERIFIED |
| `mcc_state_uttar_pradesh` | Uttar Pradesh | https://upneet.gov.in/ | DME Uttar Pradesh | P0 | VERIFIED |
| `mcc_state_west_bengal` | West Bengal | https://wbmcc.nic.in/ | WBMCC | P0 | VERIFIED |
| `mcc_state_rajasthan` | Rajasthan | https://rmeds.rajasthan.gov.in/ | RMEDS | P0 | VERIFIED |
| `mcc_state_madhya_pradesh` | Madhya Pradesh | https://dme.mponline.gov.in/ | DME MP | P0 | VERIFIED |
| `mcc_state_gujarat` | Gujarat | https://www.medadmgujarat.org/ | ACPMEC | P0 | VERIFIED |
| `mcc_state_bihar` | Bihar | https://bceceboard.bihar.gov.in/ | BCECE Board | P0 | VERIFIED |
| `mcc_state_telangana` | Telangana | https://knruhs.telangana.gov.in/ | KNRUHS | P0 | VERIFIED |
| `mcc_state_andhra_pradesh` | Andhra Pradesh | https://ntruhs.ap.nic.in/ | NTR UHS | P0 | VERIFIED |

All state entries: scope `STATE_QUOTA`, course `MBBS+BDS`, authority_level
`STATE_AUTHORITY`. See state-counselling.md for the full coverage statement
(11 of 36 states/UTs verified; the rest NOT YET VERIFIED).

### Central institutions

| source_id | official_url | institution | priority | verification |
|-----------|--------------|-------------|----------|--------------|
| `central_aiims_admissions` | https://www.aiimsexams.ac.in/ | AIIMS Admissions | P1 | VERIFIED |
| `central_bhu` | https://www.bhu.ac.in/ | Banaras Hindu University | P1 | VERIFIED |
| `central_jipmer` | https://jipmer.edu.in/ | JIPMER | P1 | VERIFIED |
| `central_amu` | — | Aligarh Muslim University | P1 | NOT_VERIFIED |
| `central_esic` | — | ESIC medical institutions | P1 | NOT_VERIFIED |
| `central_delhi_institutions` | — | Delhi institutions (MCC-administered) | P1 | NOT_VERIFIED |

## Counts

- Total sources: 28
- VERIFIED: 25
- NOT_VERIFIED: 3
- P0: 15
- P1: 13

These counts are derived from `config/data_sources.yaml` and are validated by
`config/tests/test_source_registry.py`; if the file changes, this section must
be updated in the same change.
