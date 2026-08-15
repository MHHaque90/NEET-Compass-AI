# Source Priority

> Sprint 3.0. Priority definitions and assignment. Priorities live in the
> registry (`config/data_sources.yaml`, field `priority`) and are the driver
> for which sources must be covered first by ETL and data acquisition.

## Definitions

| Priority | Meaning |
|----------|---------|
| `P0` | Core product — required to answer the primary user question (admission chance / cutoffs / college intelligence). |
| `P1` | Important — enriches the answer (examination data, BDS regulation, institutional portals) but is not required for the core loop. |

## Assignment rationale

### P0 — core

- **MCC all-India quota** (`mcc_official_base`, `mcc_ug_counselling`): seat
  matrix and allotment/cutoff data are the backbone of cutoff-based
  predictions for AIQ seats.
- **NMC college list** (`nmc_college_list`, `nmc_medical_colleges`): the
  institution master (identity, recognition, approved intake, state,
  management) underpins every college-level answer.
- **State authorities** (all 11 verified `mcc_state_*`): state-quota seats are
  a large share of total MBBS/BDS seats; each supported state's authority is
  core once that state is in scope.

### P1 — secondary

- **NTA** (`nta_official_base`, `nta_neet_ug`): examination bulletin and result
  statistics are informative but not required for cutoff predictions.
- **NDC** (`ndc_official_base`, `ndc_dental_colleges`): BDS institution master;
  secondary while MBBS is the primary course.
- **NMC eligibility** (`nmc_eligibility`): eligibility criteria reference.
- **Central institutions** (`central_aiims_admissions`, `central_bhu`,
  `central_jipmer`, and the NOT_VERIFIED `central_*` entries): institutional
  portals are secondary to the MCC seat matrix that actually drives allotment.
- **MCC archive** (`mcc_ug_archive`): historical releases are P1 for training
  historical datasets; archive verified (2026-08-09) with seat
  matrices/allotments/vacancies/bulletins available for 2021–2025.
- **MCC participating institutes** (`mcc_ug_participating_institutes`): dynamic
  institute report (2025–2026) used to join institute codes to seat matrices;
  secondary to the NMC institution master.

## Priority table

| source_id | priority |
|-----------|----------|
| mcc_official_base | P0 |
| mcc_ug_counselling | P0 |
| mcc_ug_archive | P1 |
| mcc_ug_participating_institutes | P1 |
| nta_official_base | P1 |
| nta_neet_ug | P1 |
| nmc_college_list | P0 |
| nmc_medical_colleges | P0 |
| nmc_eligibility | P1 |
| ndc_official_base | P1 |
| ndc_dental_colleges | P1 |
| mcc_state_maharashtra | P0 |
| mcc_state_karnataka | P0 |
| mcc_state_tamil_nadu | P0 |
| mcc_state_uttar_pradesh | P0 |
| mcc_state_west_bengal | P0 |
| mcc_state_rajasthan | P0 |
| mcc_state_madhya_pradesh | P0 |
| mcc_state_gujarat | P0 |
| mcc_state_bihar | P0 |
| mcc_state_telangana | P0 |
| mcc_state_andhra_pradesh | P0 |
| central_aiims_admissions | P1 |
| central_bhu | P1 |
| central_jipmer | P1 |
| central_amu | P1 |
| central_esic | P1 |
| central_delhi_institutions | P1 |

This table mirrors `config/data_sources.yaml`; the YAML file is authoritative.
