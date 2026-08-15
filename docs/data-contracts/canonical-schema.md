# Canonical Schema

## Purpose

Canonical models provide source-independent data representations. External source formats MUST NEVER become the internal canonical schema.

## Canonical Models

### College

| Field | Type | Description |
|-------|------|-------------|
| college_id | str | Unique identifier |
| college_name | str | College name |
| state_id | Optional[str] | State reference |
| district_id | Optional[str] | District reference |
| authority | Optional[str] | Governing authority |
| college_type | Optional[str] | Type of college |

### Course

| Field | Type | Description |
|-------|------|-------------|
| course_id | str | Unique identifier |
| course_name | str | Course name |
| course_type | Optional[str] | Type of course |
| duration_years | Optional[int] | Duration in years |

### SeatMatrix

| Field | Type | Description |
|-------|------|-------------|
| college_id | str | College reference |
| course_id | str | Course reference |
| quota_id | str | Quota reference |
| category_id | str | Category reference |
| total_seats | int | Total seats available |
| effective_year | int | Year of validity |

### Allotment

| Field | Type | Description |
|-------|------|-------------|
| allotment_id | Optional[str] | Unique identifier |
| college_id | str | College reference |
| course_id | str | Course reference |
| quota_id | str | Quota reference |
| category_id | str | Category reference |
| round_id | str | Round reference |
| rank | Optional[int] | Candidate rank |
| score | Optional[float] | Candidate score |
| seat_count | int | Seats allotted |
| effective_year | int | Year of validity |
| publication_version | str | Publication version |
| source_file_id | Optional[str] | Source file reference |

### HistoricalCutoff

| Field | Type | Description |
|-------|------|-------------|
| college_id | str | College reference |
| course_id | str | Course reference |
| year | int | Year |
| round_id | str | Round reference |
| quota_id | str | Quota reference |
| category_id | str | Category reference |
| cutoff_rank | Optional[int] | Cutoff rank |
| cutoff_score | Optional[float] | Cutoff score |
| source_file_id | Optional[str] | Source file reference |

### Other Models

- **Fee**: Fee structure per college/course/quota
- **Quota**: Quota types (AIQ, State, etc.)
- **Category**: Category types (General, OBC, SC, ST, etc.)
- **Round**: Counselling rounds
- **State**: State reference data
- **District**: District reference data
- **SourceMetadata**: Provenance metadata

## Design Principles

1. **Source Independence**: Canonical fields do not depend on external source column naming
2. **Referential Integrity**: All references use consistent IDs
3. **Provenance Tracking**: Source metadata preserved for audit
4. **Extensibility**: New fields can be added via optional columns
