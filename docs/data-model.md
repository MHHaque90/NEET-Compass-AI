# Data model

## Overview

Four tables form the core schema (see `backend/alembic/versions/0001_initial_schema.py`).

```
colleges ──< allotments >── (historical cut-offs)
colleges ──< recommendations >── candidates
```

## Tables

### `colleges`

Institution master data. One row per course (an institute running both MBBS
and BDS has two rows with distinct `code` values).

| column | type | notes |
| --- | --- | --- |
| id | uuid PK | `gen_random_uuid()` |
| code | varchar(20) UNIQUE | stable institution code (e.g. NMC code) |
| name | varchar(255) | |
| state | varchar(40) | enum value of `IndiaState` |
| city | varchar(100) | |
| course | varchar(10) | `MBBS` / `BDS` |
| ownership | varchar(32) | `GOVERNMENT`, `GOVERNMENT_AIDED`, `CENTRAL`, `DEEMED`, `PRIVATE` |
| annual_fee_inr | numeric(12,2) | tuition + hostel |
| total_seats | int | sanctioned seats |
| aiq_seats | int | seats in All India Quota |
| created_at / updated_at | timestamptz | |

Indexes: `state`, `course`.

### `candidates`

Persisted snapshot of each applicant (audit + ML feature source).

| column | type | notes |
| --- | --- | --- |
| id | uuid PK | |
| air | int | All-India Rank, indexed |
| marks | int | NEET score /720 |
| category | varchar(32) | `GENERAL`, `GENERAL_EWS`, `OBC`, `SC`, `ST` |
| domicile_state | varchar(40) | |
| gender | varchar(16) | `NEUTRAL`, `MALE`, `FEMALE` |
| is_pwd | bool | |
| is_minority | bool | |
| quota_type | varchar(16) | `AIQ`, `STATE` |
| budget_inr | numeric(12,2) NULL | NULL = unlimited |
| preferred_states | jsonb | array of state enum values |

### `allotments`

The analytic core — one row per published cut-off/allotment line.

| column | type | notes |
| --- | --- | --- |
| id | uuid PK | |
| college_id | uuid FK→colleges | `ON DELETE CASCADE` |
| college_code | varchar(20) | denormalized for fast browsing |
| course | varchar(10) | |
| counselling_year | smallint | NEET counselling began 2013 |
| counselling_date | date NULL | |
| round_number | smallint | 1–5 |
| is_stray_round | bool | stray-vacancy round |
| quota_type | varchar(16) | `AIQ` / `STATE` |
| category | varchar(32) | |
| gender | varchar(16) | |
| is_pwd | bool | |
| opening_rank / closing_rank | int | ranks are the primary signal |
| opening_marks / closing_marks | numeric(5,2) NULL | some states publish marks only |
| seats_offered | int | |

Constraints:
- **UNIQUE (college_id, counselling_year, round_number, quota_type, category,
  gender, is_pwd)** — makes ETL idempotent and de-duplicates releases.
- Index `(college_id, counselling_year, round_number)` — per-college history.
- Index `(quota_type, category, gender, is_pwd, counselling_year)` — cohort
  filter for ML feature queries.

### `recommendations`

Immutable audit log of every generated recommendation.

| column | type | notes |
| --- | --- | --- |
| id | uuid PK | |
| candidate_id | uuid FK→candidates NULL | `SET NULL` if candidate purged |
| college_id | uuid FK→colleges NULL | `CASCADE` |
| course | varchar(10) | |
| probability | numeric(4,3) NULL | NULL until a real engine runs |
| expected_round | smallint NULL | |
| confidence | numeric(4,3) NULL | |
| engine_name / engine_version | varchar(50) | provenance |
| status | varchar(16) | `PENDING`, `COMPLETED`, `DEGRADED`, `FAILED` |
| reasons | jsonb | ordered `{type, message, data}` blocks |
| strategy | jsonb | quota/budget/state advisory + future risk analysis |
| choice_filling_order | jsonb | ordered college ids |

Index: `(candidate_id, created_at)` for "latest recommendation" lookups.

## Enum vocabulary

All enums live in `backend/app/domain/enums.py`:

- `Category`: GENERAL, GENERAL_EWS, OBC, SC, ST
- `QuotaType`: AIQ, STATE
- `Gender`: NEUTRAL, MALE, FEMALE
- `PwdStatus`: NONE, PWD
- `MinorityStatus`: NONE, MINORITY
- `Course`: MBBS, BDS
- `CollegeOwnership`: GOVERNMENT, GOVERNMENT_AIDED, CENTRAL, DEEMED, PRIVATE
- `CounsellingRound`: ROUND_1 … ROUND_5, STRAY
- `IndiaState`: 28 states + 8 UTs
- `RecommendationStatus`: PENDING, COMPLETED, DEGRADED, FAILED

> Storage note: enums are stored as VARCHAR with Pydantic boundary validation
> (`native_enum=False`). See [ARCHITECTURE.md §8](ARCHITECTURE.md#8-enum-strategy).
