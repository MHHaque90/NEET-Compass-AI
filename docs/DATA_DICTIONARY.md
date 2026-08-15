# Data Dictionary

> Complete column-level documentation for all 24 database tables in the
> NEET Compass AI database.

## Table Legend

| Symbol | Meaning |
|--------|---------|
| PK | Primary Key (UUID) |
| FK | Foreign Key |
| NN | NOT NULL constraint |
| IDX | Indexed |
| UK | Unique Key |
| CI | Created at (auto) |
| UP | Updated at (auto) |
| SD | Soft Delete (deleted_at) |

---

## 1. states

Indian states and union territories for NEET counselling jurisdiction.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | State identifier | `a1b2c3...` |
| code | VARCHAR(10) | NN | IDX,UK | State code | `MH` |
| name | VARCHAR(100) | NN | UK | State name | `Maharashtra` |
| is_ut | BOOLEAN | NN | — | Is Union Territory | `false` |
| neet_counselling_authority | VARCHAR(200) | Y | — | Counselling authority name | `Director of Medical Education` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete timestamp | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** MCC NEET counselling documentation; Ministry of Health & Family Welfare.

## 2. districts

Districts within states for granular counselling data.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | District identifier | `d1e2f3...` |
| state_id | UUID | NN | FK→states | Parent state | `a1b2c3...` |
| code | VARCHAR(20) | NN | — | District code | `MUM` |
| name | VARCHAR(100) | NN | — | District name | `Mumbai` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete timestamp | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Relationships:** Many-to-one with `states`.

**Official Source:** Election Commission of India district list.

## 3. categories

Reservation categories for NEET counselling.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Category identifier | `c1a2t3...` |
| code | VARCHAR(20) | NN | IDX,UK | Category code | `OBC` |
| name | VARCHAR(100) | NN | UK | Category name | `Other Backward Classes` |
| description | VARCHAR(500) | Y | — | Full description | `Non-creamy layer OBC` |
| reservation_percentage | NUMERIC(5,2) | Y | — | % reservation | `27.00` |
| is_vertical | BOOLEAN | NN | — | Vertical reservation | `true` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete timestamp | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** MCC NEET counselling policy; Supreme Court of India reservation orders.

## 4. quotas

Quota types for NEET counselling (AIQ, State, Deemed, etc.).

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Quota identifier | `q1u2o3...` |
| code | VARCHAR(20) | NN | IDX,UK | Quota code | `AIQ` |
| name | VARCHAR(100) | NN | UK | Quota name | `All India Quota` |
| description | VARCHAR(500) | Y | — | Full description | `MCC-administered seats` |
| is_all_india | BOOLEAN | NN | — | All-India quota flag | `true` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete timestamp | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** MCC counselling guidelines.

## 5. rounds

Counselling rounds for NEET counselling.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Round identifier | `r1o2u3...` |
| code | VARCHAR(20) | NN | IDX,UK | Round code | `ROUND_1` |
| name | VARCHAR(100) | NN | UK | Round name | `Round 1` |
| round_number | SMALLINT | NN | UK | Numeric round order | `1` |
| is_stray_round | BOOLEAN | NN | — | Stray vacancy round | `false` |
| description | VARCHAR(500) | Y | — | Round description | `Initial round` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete timestamp | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** MCC counselling schedule.

## 6. courses

NEET courses (MBBS, BDS).

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Course identifier | `c1o2u3...` |
| code | VARCHAR(10) | NN | IDX,UK | Course code | `MBBS` |
| name | VARCHAR(100) | NN | UK | Course name | `Bachelor of Medicine` |
| description | VARCHAR(500) | Y | — | Full description | `5.5 year MBBS programme` |
| duration_years | INTEGER | NN | — | Duration in years | `5` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete timestamp | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** MCC and NMC course definitions.

## 7. colleges

Institution master data for NEET counselling.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | College identifier | `col1...` |
| code | VARCHAR(20) | NN | UK,IDX | Institution code | `MCC001` |
| name | VARCHAR(255) | NN | — | College name | `AIIMS Delhi` |
| state | VARCHAR(40) | NN | IDX | State enum value | `DELHI` |
| city | VARCHAR(100) | NN | — | City | `New Delhi` |
| course | VARCHAR(10) | NN | IDX | Course enum | `MBBS` |
| ownership | VARCHAR(32) | NN | — | Ownership type | `CENTRAL` |
| annual_fee_inr | NUMERIC(12,2) | NN | — | Annual fee | `150000.00` |
| total_seats | INTEGER | NN | — | Total sanctioned seats | `100` |
| aiq_seats | INTEGER | NN | — | AIQ seats | `15` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Relationships:** One-to-many with `allotments`, `fees`, `seat_matrix`, `recommendations`, `prediction_history`.

**Official Source:** MCC college list; NMC recognized colleges list.

## 8. fees

Fee structures per college/course/year/category.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Fee record identifier | `f1e2e3...` |
| college_id | UUID | NN | FK→colleges | College reference | `col1...` |
| course | VARCHAR(10) | NN | — | Course enum | `MBBS` |
| category | VARCHAR(32) | NN | — | Category enum | `GENERAL` |
| ownership | VARCHAR(32) | NN | — | Ownership enum | `DEEMED` |
| academic_year | SMALLINT | NN | IDX | Academic year | `2024` |
| notification_date | DATE | Y | — | Fee notification date | `2024-06-01` |
| tuition_fee_inr | NUMERIC(12,2) | NN | — | Tuition fee | `250000.00` |
| hostel_fee_inr | NUMERIC(12,2) | NN | — | Hostel fee | `50000.00` |
| security_deposit_inr | NUMERIC(12,2) | NN | — | Security deposit | `10000.00` |
| miscellaneous_fee_inr | NUMERIC(12,2) | NN | — | Misc fees | `5000.00` |
| total_annual_fee_inr | NUMERIC(12,2) | NN | — | Total fee | `310000.00` |
| is_notified | BOOLEAN | NN | — | Fee notified flag | `true` |
| source_file_id | UUID | Y | FK→source_files | Source file | `sf1...` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Relationships:** Many-to-one with `colleges` (CASCADE) and `source_files` (SET NULL).

**Official Source:** College fee structures published by MCC/NMC.

## 9. seat_matrix

Sanctioned seat counts per college/course/quota/category/year.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Seat matrix identifier | `sm1...` |
| college_id | UUID | NN | FK→colleges,IDX | College reference | `col1...` |
| course | VARCHAR(10) | NN | — | Course enum | `MBBS` |
| quota_type | VARCHAR(16) | NN | — | Quota enum | `AIQ` |
| category | VARCHAR(32) | NN | — | Category enum | `OBC` |
| academic_year | SMALLINT | NN | IDX | Academic year | `2024` |
| notification_date | DATE | Y | — | Notification date | `2024-06-01` |
| seats_sanctioned | INTEGER | NN | — | Sanctioned seats | `100` |
| seats_filled | INTEGER | NN | — | Seats filled | `85` |
| is_notified | BOOLEAN | NN | — | Notified flag | `true` |
| source_file_id | UUID | Y | FK→source_files | Source file | `sf1...` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Relationships:** Many-to-one with `colleges` (CASCADE) and `source_files` (SET NULL).
**Official Source:** MCC seat matrix publication.

## 10. allotments

Historical counselling cut-off rows (analytic core).

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Allotment identifier | `a1o2t3...` |
| college_id | UUID | NN | FK→colleges,IDX,UK | College reference | `col1...` |
| college_code | VARCHAR(20) | NN | — | Denormalized code | `MCC001` |
| course | VARCHAR(10) | NN | — | Course enum | `MBBS` |
| counselling_year | SMALLINT | NN | IDX | Year | `2024` |
| counselling_date | DATE | Y | — | Date of counselling | `2024-06-15` |
| round_number | SMALLINT | NN | — | Round 1-5 | `1` |
| is_stray_round | BOOLEAN | NN | — | Stray flag | `false` |
| quota_type | VARCHAR(16) | NN | — | Quota enum | `AIQ` |
| category | VARCHAR(32) | NN | — | Category enum | `GENERAL` |
| gender | VARCHAR(16) | NN | — | Gender enum | `NEUTRAL` |
| is_pwd | BOOLEAN | NN | — | PwD flag | `false` |
| opening_rank | INTEGER | NN | — | Opening AIR | `85000` |
| closing_rank | INTEGER | NN | — | Closing AIR | `92000` |
| opening_marks | NUMERIC(5,2) | Y | — | Opening marks | `620.50` |
| closing_marks | NUMERIC(5,2) | Y | — | Closing marks | `610.00` |
| seats_offered | INTEGER | NN | — | Seats offered | `15` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Constraints:** Unique on (college_id, year, round, quota, category, gender, pwd).
**Official Source:** MCC and state counselling cut-off PDF releases.

## 11. candidates

Persisted candidate profiles (audit).

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Candidate identifier | `c1a2n3...` |
| air | INTEGER | NN | IDX | All-India Rank | `85000` |
| marks | INTEGER | NN | — | NEET score /720 | `620` |
| category | VARCHAR(32) | NN | — | Category enum | `OBC` |
| domicile_state | VARCHAR(40) | NN | — | State enum | `MAHARASHTRA` |
| gender | VARCHAR(16) | NN | — | Gender enum | `NEUTRAL` |
| is_pwd | BOOLEAN | NN | — | PwD flag | `false` |
| is_minority | BOOLEAN | NN | — | Minority flag | `false` |
| quota_type | VARCHAR(16) | NN | — | Quota enum | `AIQ` |
| budget_inr | NUMERIC(12,2) | Y | — | Budget | `150000.00` |
| preferred_states | JSON | NN | — | List of states | `["MH", "DL"]` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** User input during profile setup.

## 12. predictions

Prediction requests and results.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Prediction identifier | `p1r2e3...` |
| user_id | UUID | Y | FK→users,IDX | User reference | `u1...` |
| session_id | VARCHAR(100) | NN | IDX | Session correlation | `sess_abc123` |
| air | INTEGER | NN | — | NEET AIR | `85000` |
| marks | INTEGER | NN | — | NEET score | `620` |
| category | VARCHAR(32) | NN | — | Category enum | `OBC` |
| domicile_state_id | UUID | Y | FK→states | State reference | `s1...` |
| gender | VARCHAR(16) | NN | — | Gender enum | `NEUTRAL` |
| is_pwd | BOOLEAN | NN | — | PwD flag | `false` |
| is_minority | BOOLEAN | NN | — | Minority flag | `false` |
| quota_type | VARCHAR(16) | NN | — | Quota enum | `AIQ` |
| budget_inr | NUMERIC(12,2) | Y | — | Budget | `150000.00` |
| preferred_states | JSON | NN | — | Preferred states | `["MH"]` |
| counselling_year | SMALLINT | NN | IDX | Year | `2024` |
| target_round | SMALLINT | Y | — | Target round | `2` |
| engine_name | VARCHAR(50) | NN | — | Engine name | `rule_based` |
| engine_version | VARCHAR(50) | Y | — | Engine version | `1.0.0` |
| model_version_id | UUID | Y | FK→model_versions | Model version | `mv1...` |
| total_colleges_evaluated | INTEGER | NN | — | Colleges evaluated | `500` |
| total_recommendations | INTEGER | NN | — | Recommendations made | `10` |
| top_probability | NUMERIC(4,3) | Y | — | Top probability | `0.850` |
| prediction_status | VARCHAR(16) | NN | — | Status enum | `COMPLETED` |
| request_metadata | JSON | NN | — | Input metadata | `{"ip":"..."}` |
| response_metadata | JSON | NN | — | Output metadata | `{"took_ms":120}` |
| processing_time_ms | INTEGER | Y | — | Processing time | `120` |
| completed_at | TIMESTAMPTZ | Y | — | Completed timestamp | `2024-08-10...` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** Generated by prediction engine.

## 13. prediction_history

Individual college recommendations within a prediction.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | History record ID | `ph1...` |
| prediction_id | UUID | NN | FK→predictions,IDX | Parent prediction | `p1...` |
| college_id | UUID | Y | FK→colleges,IDX | College recommended | `col1...` |
| course | VARCHAR(10) | NN | — | Course enum | `MBBS` |
| probability | NUMERIC(4,3) | Y | — | Probability (0-1) | `0.750` |
| expected_round | SMALLINT | Y | — | Expected round | `2` |
| confidence | NUMERIC(4,3) | Y | — | Confidence (0-1) | `0.850` |
| status | VARCHAR(16) | NN | — | Status enum | `COMPLETED` |
| reasons | JSON | NN | — | Explanation blocks | `[{"type":"..."}]` |
| strategy | JSON | NN | — | Counselling strategy | `{"quota":"AIQ"}` |
| choice_filling_order | INTEGER | Y | — | Choice order index | `1` |
| quota_type | VARCHAR(16) | NN | — | Quota enum | `AIQ` |
| category | VARCHAR(32) | NN | — | Category enum | `GENERAL` |
| gender | VARCHAR(16) | NN | — | Gender enum | `NEUTRAL` |
| is_pwd | BOOLEAN | NN | — | PwD flag | `false` |
| historical_closing_rank | INTEGER | Y | — | Ref closing rank | `92000` |
| historical_closing_marks | NUMERIC(5,2) | Y | — | Ref closing marks | `610.00` |
| seats_available | INTEGER | Y | — | Seats available | `15` |
| feature_contributions | JSON | Y | — | ML attribution | `{"air":0.3,...}` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** Generated by prediction engine.

## 14. recommendations

Explainable recommendation snapshots (audit).

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Recommendation identifier | `rec1...` |
| candidate_id | UUID | Y | FK→candidates | Candidate reference | `c1...` |
| college_id | UUID | Y | FK→colleges | College reference | `col1...` |
| course | VARCHAR(10) | NN | — | Course enum | `MBBS` |
| probability | NUMERIC(4,3) | Y | — | Probability (0-1) | `0.750` |
| expected_round | SMALLINT | Y | — | Expected round | `2` |
| confidence | NUMERIC(4,3) | Y | — | Confidence (0-1) | `0.850` |
| engine_name | VARCHAR(50) | NN | — | Engine name | `rule_based` |
| engine_version | VARCHAR(50) | Y | — | Engine version | `1.0.0` |
| status | VARCHAR(16) | NN | — | Status enum | `COMPLETED` |
| reasons | JSON | NN | — | Explanation blocks | `[{"type":"..."}]` |
| strategy | JSON | NN | — | Counselling strategy | `{"quota":"AIQ"}` |
| choice_filling_order | JSON | NN | — | Ordered college IDs | `["col1","col2"]` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** Generated by the recommendation engine.

## 15. users

Platform users (candidates, admins).

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | User identifier | `u1...` |
| email | VARCHAR(255) | NN | UK,IDX | Email address | `user@example.com` |
| phone | VARCHAR(20) | Y | UK,IDX | Phone number | `+9198765...` |
| password_hash | VARCHAR(255) | NN | — | Hashed password | `$2b$12$...` |
| full_name | VARCHAR(255) | NN | — | Full name | `John Doe` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| is_verified | BOOLEAN | NN | — | Email verified | `true` |
| last_login_at | TIMESTAMPTZ | Y | — | Last login | `2024-08-10...` |
| air | INTEGER | Y | IDX | NEET AIR | `85000` |
| marks | INTEGER | Y | — | NEET score | `620` |
| category | VARCHAR(32) | Y | — | Category enum | `OBC` |
| domicile_state_id | UUID | Y | FK→states | State reference | `s1...` |
| gender | VARCHAR(16) | Y | — | Gender enum | `NEUTRAL` |
| is_pwd | BOOLEAN | NN | — | PwD flag | `false` |
| is_minority | BOOLEAN | NN | — | Minority flag | `false` |
| quota_type | VARCHAR(16) | Y | — | Quota enum | `AIQ` |
| budget_inr | NUMERIC(12,2) | Y | — | Budget | `150000.00` |
| preferred_states | JSON | NN | — | Preferred states | `["MH","DL"]` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** User registration and profile setup.

## 16. uploads

File upload tracking for ETL and user data.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Upload identifier | `upl1...` |
| user_id | UUID | Y | FK→users,IDX | Uploading user | `u1...` |
| source_file_id | UUID | Y | FK→source_files,IDX | Source file | `sf1...` |
| upload_type | VARCHAR(20) | NN | — | Type enum | `ETL_SOURCE` |
| status | VARCHAR(16) | NN | — | Status enum | `COMPLETED` |
| original_filename | VARCHAR(255) | NN | — | Original name | `cutoffs.xlsx` |
| stored_filename | VARCHAR(255) | NN | — | Stored name | `upload_abc.xlsx` |
| file_path | VARCHAR(500) | NN | — | File path | `/data/raw/...` |
| file_size_bytes | INTEGER | NN | — | File size | `102400` |
| mime_type | VARCHAR(100) | Y | — | MIME type | `application/...` |
| checksum_sha256 | VARCHAR(64) | NN | — | SHA256 hash | `a1b2c3...` |
| row_count | INTEGER | Y | — | Row count | `5000` |
| error_count | INTEGER | NN | — | Error count | `0` |
| error_details | JSON | Y | — | Error details | `[{"row":42}]` |
| started_at | TIMESTAMPTZ | Y | — | Started | `2024-08-10...` |
| completed_at | TIMESTAMPTZ | Y | — | Completed | `2024-08-10...` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** User uploads or ETL source downloads.

## 17. data_sources

External data sources for ETL ingestion.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Source identifier | `ds1...` |
| code | VARCHAR(50) | NN | IDX,UK | Source code | `mcc_official` |
| name | VARCHAR(200) | NN | — | Source name | `MCC Official` |
| source_type | VARCHAR(30) | NN | — | Source type enum | `MCC_OFFICIAL` |
| status | VARCHAR(20) | NN | — | Status enum | `ACTIVE` |
| description | VARCHAR(1000) | Y | — | Description | `MCC cut-off data` |
| base_url | VARCHAR(500) | Y | — | Base URL | `https://mcc.nic.in` |
| api_endpoint | VARCHAR(500) | Y | — | API endpoint | `/api/cutoffs` |
| auth_config | JSON | Y | — | Auth config | `{"type":"api_key"}` |
| schedule_cron | VARCHAR(100) | Y | — | Cron schedule | `0 2 * * *` |
| timezone | VARCHAR(50) | NN | — | Timezone | `Asia/Kolkata` |
| rate_limit_rpm | INTEGER | Y | — | Rate limit | `60` |
| retry_config | JSON | Y | — | Retry config | `{"retries":3}` |
| last_successful_run_at | TIMESTAMPTZ | Y | — | Last success | `2024-08-10...` |
| last_failed_run_at | TIMESTAMPTZ | Y | — | Last failure | `2024-08-09...` |
| consecutive_failures | INTEGER | NN | — | Failure count | `0` |
| success_rate | NUMERIC(5,4) | Y | — | Success rate | `0.9800` |
| schema_version | VARCHAR(50) | NN | — | Schema version | `1.0` |
| data_version | VARCHAR(50) | Y | — | Data version | `2024.08` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** MCC website, state counselling authority websites.

> For the authoritative inventory of official data sources (authority, URL,
> dataset, priority, verification state), see
> `docs/data-sources/source-registry.md` and `config/data_sources.yaml`.

## 18. source_files

Individual files from data sources — tracks download, validation, and load status.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Source file identifier | `sf1...` |
| data_source_id | UUID | NN | FK→data_sources,IDX | Parent source | `ds1...` |
| file_name | VARCHAR(255) | NN | — | File name | `cutoff_2024.xlsx` |
| file_version | VARCHAR(50) | NN | — | File version | `1` |
| academic_year | SMALLINT | NN | IDX | Academic year | `2024` |
| counselling_round | VARCHAR(50) | Y | — | Counselling round | `ROUND_1` |
| remote_url | VARCHAR(500) | Y | — | Remote URL | `https://...` |
| local_path | VARCHAR(500) | Y | — | Local path | `/data/raw/...` |
| file_size_bytes | INTEGER | Y | — | File size | `1048576` |
| mime_type | VARCHAR(100) | Y | — | MIME type | `application/vnd...` |
| checksum_sha256 | VARCHAR(64) | Y | IDX | SHA256 hash | `a1b2c3...` |
| row_count | INTEGER | Y | — | Row count | `5000` |
| column_names | JSON | Y | — | Column names | `["college_code","rank"]` |
| status | VARCHAR(20) | NN | — | Status enum | `LOADED` |
| error_message | VARCHAR(1000) | Y | — | Error message | `Invalid column` |
| validation_result | JSON | Y | — | Validation result | `{"passed":true}` |
| discovered_at | TIMESTAMPTZ | NN | — | Discovered time | `2024-08-10...` |
| downloaded_at | TIMESTAMPTZ | Y | — | Downloaded time | `2024-08-10...` |
| validated_at | TIMESTAMPTZ | Y | — | Validated time | `2024-08-10...` |
| loaded_at | TIMESTAMPTZ | Y | — | Loaded time | `2024-08-10...` |
| source_version | VARCHAR(50) | Y | — | Source version | `2024.08.01` |
| etl_version | VARCHAR(50) | Y | — | ETL version | `1.0.0` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Constraints:** Unique on (data_source_id, academic_year, file_name, file_version).
**Official Source:** Downloaded from data source URLs.

## 19. etl_runs

ETL pipeline execution runs — complete audit trail.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Run identifier | `er1...` |
| data_source_id | UUID | Y | FK→data_sources,IDX | Source | `ds1...` |
| source_file_id | UUID | Y | FK→source_files,IDX | File | `sf1...` |
| pipeline_name | VARCHAR(100) | NN | IDX | Pipeline name | `allotment` |
| run_type | VARCHAR(20) | NN | — | Run type enum | `INCREMENTAL` |
| status | VARCHAR(20) | NN | — | Status enum | `COMPLETED` |
| config_snapshot | JSON | NN | — | Config used | `{"batch_size":1000}` |
| academic_year | SMALLINT | Y | IDX | Year | `2024` |
| counselling_round | VARCHAR(50) | Y | — | Round | `ROUND_1` |
| total_files | INTEGER | NN | — | Files to process | `3` |
| processed_files | INTEGER | NN | — | Files processed | `3` |
| total_rows | INTEGER | NN | — | Total rows | `15000` |
| loaded_rows | INTEGER | NN | — | Rows loaded | `15000` |
| skipped_rows | INTEGER | NN | — | Rows skipped | `0` |
| error_rows | INTEGER | NN | — | Error rows | `0` |
| started_at | TIMESTAMPTZ | Y | — | Started | `2024-08-10...` |
| completed_at | TIMESTAMPTZ | Y | — | Completed | `2024-08-10...` |
| duration_seconds | INTEGER | Y | — | Duration | `120` |
| error_count | INTEGER | NN | — | Error count | `5` |
| last_error | VARCHAR(1000) | Y | — | Last error | `Row 42: invalid` |
| error_summary | JSON | Y | — | Error summary | `{"type":"..."}` |
| quality_score | NUMERIC(5,4) | Y | — | Quality score | `0.9800` |
| validation_passed | INTEGER | NN | — | Valid rows | `15000` |
| validation_failed | INTEGER | NN | — | Invalid rows | `0` |
| etl_version | VARCHAR(50) | NN | — | ETL version | `1.0.0` |
| code_version | VARCHAR(50) | Y | — | Git commit | `abc1234` |
| triggered_by | VARCHAR(100) | Y | — | Trigger source | `admin` |
| trigger_type | VARCHAR(50) | Y | — | Trigger type | `manual` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** ETL pipeline execution.

## 20. etl_errors

Granular ETL error tracking for debugging and alerting.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Error identifier | `ee1...` |
| etl_run_id | UUID | NN | FK→etl_runs | Parent run | `er1...` |
| source_file_id | UUID | Y | FK→source_files | Source file | `sf1...` |
| stage | VARCHAR(20) | NN | — | Stage enum | `VALIDATE` |
| severity | VARCHAR(10) | NN | — | Severity enum | `ERROR` |
| error_code | VARCHAR(50) | NN | IDX | Error code | `INVALID_VALUE` |
| error_message | VARCHAR(2000) | NN | — | Error message | `Rank out of range` |
| error_details | JSON | Y | — | Error details | `{"column":"rank"}` |
| row_number | INTEGER | Y | — | Row number | `42` |
| column_name | VARCHAR(100) | Y | — | Column name | `closing_rank` |
| raw_value | VARCHAR(500) | Y | — | Raw value | `0` |
| expected_value | VARCHAR(500) | Y | — | Expected | `>=1` |
| is_resolved | BOOLEAN | NN | — | Resolved flag | `false` |
| resolved_at | TIMESTAMPTZ | Y | — | Resolved time | `2024-08-11...` |
| resolved_by | VARCHAR(100) | Y | — | Resolved by | `admin` |
| resolution_notes | VARCHAR(1000) | Y | — | Notes | `Fixed in source` |
| stack_trace | TEXT | Y | — | Stack trace | `Traceback...` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Official Source:** ETL pipeline error handling.

## 21. model_versions

ML model registry — tracks every model version with metrics and artifacts.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Model identifier | `mv1...` |
| model_name | VARCHAR(100) | NN | IDX,UK | Model name | `rank_predictor` |
| version | VARCHAR(50) | NN | UK | Version string | `1.0.0` |
| model_type | VARCHAR(30) | NN | — | Type enum | `RULE_BASED` |
| status | VARCHAR(20) | NN | — | Status enum | `PRODUCTION` |
| is_production | BOOLEAN | NN | IDX | In production | `true` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| training_data_version | VARCHAR(50) | Y | — | Training data version | `2024.08` |
| training_started_at | TIMESTAMPTZ | Y | — | Training started | `2024-08-01...` |
| training_completed_at | TIMESTAMPTZ | Y | — | Training completed | `2024-08-02...` |
| training_duration_seconds | INTEGER | Y | — | Duration | `3600` |
| training_config | JSON | NN | — | Training config | `{"lr":0.01}` |
| training_metrics | JSON | NN | — | Training metrics | `{"acc":0.85}` |
| validation_metrics | JSON | Y | — | Validation metrics | `{"acc":0.82}` |
| validation_data_version | VARCHAR(50) | Y | — | Validation data version | `2024.08` |
| validated_at | TIMESTAMPTZ | Y | — | Validated time | `2024-08-03...` |
| validated_by | VARCHAR(100) | Y | — | Validated by | `ml_team` |
| deployed_at | TIMESTAMPTZ | Y | — | Deployed time | `2024-08-04...` |
| deployed_by | VARCHAR(100) | Y | — | Deployed by | `ml_team` |
| deployment_config | JSON | Y | — | Deployment config | `{"batch":32}` |
| model_path | VARCHAR(500) | Y | — | Model file path | `/models/rank_v1.pkl` |
| artifact_path | VARCHAR(500) | Y | — | Artifact path | `/artifacts/v1.tar.gz` |
| feature_names | JSON | Y | — | Feature names | `["air","marks"]` |
| target_name | VARCHAR(100) | Y | — | Target name | `admission_probability` |
| min_accuracy | NUMERIC(4,3) | Y | — | Min accuracy threshold | `0.800` |
| min_precision | NUMERIC(4,3) | Y | — | Min precision | `0.750` |
| min_recall | NUMERIC(4,3) | Y | — | Min recall | `0.750` |
| max_latency_ms | INTEGER | Y | — | Max latency | `100` |
| parent_model_id | UUID | Y | FK→model_versions | Parent model | `mv0...` |
| experiment_id | VARCHAR(100) | Y | — | Experiment ID | `exp_001` |
| run_id | VARCHAR(100) | Y | — | Run ID | `run_abc123` |
| description | VARCHAR(1000) | Y | — | Description | `V1 model...` |
| tags | JSON | Y | — | Tags | `["final","baseline"]` |
| deprecated_at | TIMESTAMPTZ | Y | — | Deprecated time | `2024-08-05...` |
| deprecated_by | VARCHAR(100) | Y | — | Deprecated by | `ml_team` |
| deprecation_reason | VARCHAR(500) | Y | — | Reason | `Superseded` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Constraints:** Unique on (model_name, version).
**Official Source:** ML training pipeline.

## 22. feature_flags

Feature flag definitions with multi-source value resolution.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Flag identifier | `ff1...` |
| key | VARCHAR(100) | NN | IDX,UK | Flag key | `ml.rule_engine` |
| name | VARCHAR(200) | NN | — | Flag name | `Rule Engine` |
| description | VARCHAR(1000) | Y | — | Description | `Enable rule-based...` |
| flag_type | VARCHAR(10) | NN | — | Type enum | `BOOLEAN` |
| default_value | TEXT | NN | — | Default value | `false` |
| default_value_parsed | JSON | Y | — | Parsed default | `false` |
| current_value | TEXT | NN | — | Current resolved value | `true` |
| current_value_parsed | JSON | Y | — | Parsed current | `true` |
| current_source | VARCHAR(20) | NN | — | Winning source | `ENV` |
| targeting_rules | JSON | Y | — | Targeting rules | `{"audience":"..."}` |
| rollout_percentage | INTEGER | NN | — | Rollout % (0-100) | `100` |
| is_enabled | BOOLEAN | NN | IDX | Enabled flag | `true` |
| is_system | BOOLEAN | NN | — | System flag | `false` |
| tags | JSON | Y | — | Tags | `["ml","experimental"]` |
| owner | VARCHAR(100) | Y | — | Owner | `ml-team` |
| team | VARCHAR(100) | Y | — | Team | `ml` |
| version | INTEGER | NN | — | Version number | `1` |
| last_modified_by | VARCHAR(100) | Y | — | Modified by | `admin` |
| last_modified_source | VARCHAR(20) | Y | — | Source | `DATABASE` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Constraints:** Unique on `key`.
**Official Source:** Application configuration (`config/flags.yaml`).

## 23. system_settings

System configuration settings with versioning.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Setting identifier | `ss1...` |
| scope | VARCHAR(20) | NN | IDX | Scope enum | `GLOBAL` |
| key | VARCHAR(100) | NN | IDX | Setting key | `max_results_per_page` |
| value | TEXT | NN | — | Value (JSON string) | `50` |
| value_type | VARCHAR(10) | NN | — | Type enum | `INTEGER` |
| version | INTEGER | NN | — | Version | `1` |
| description | VARCHAR(500) | Y | — | Description | `Max page size` |
| is_sensitive | BOOLEAN | NN | — | Sensitive flag | `false` |
| is_active | BOOLEAN | NN | — | Active flag | `true` |
| feature_flag_id | UUID | Y | FK→feature_flags | Linked flag | `ff1...` |
| validation_rules | JSON | Y | — | Validation rules | `{"min":1}` |
| allowed_values | JSON | Y | — | Allowed values | `[10,25,50,100]` |
| deleted_at | TIMESTAMPTZ | Y | SD | Soft delete | `NULL` |
| created_at | TIMESTAMPTZ | NN | CI | Record creation | `2024-01-01...` |
| updated_at | TIMESTAMPTZ | NN | UP | Last update | `2024-01-01...` |

**Constraints:** Unique on (scope, key, version).
**Official Source:** Application configuration.

## 24. logs

Structured application logs — append-only, no updates, no deletes.

| Column | Type | Nullable | Keys | Description | Example |
|--------|------|----------|------|-------------|---------|
| id | UUID | NN | PK | Log entry identifier | `log1...` |
| created_at | TIMESTAMPTZ | NN | IDX | Log timestamp | `2024-08-10...` |
| level | VARCHAR(10) | NN | — | Log level | `INFO` |
| logger_name | VARCHAR(200) | NN | — | Logger name | `app.core.database` |
| message | VARCHAR(2000) | NN | — | Log message | `Query executed` |
| trace_id | VARCHAR(50) | Y | IDX | Trace ID | `abc123...` |
| span_id | VARCHAR(50) | Y | — | Span ID | `def456...` |
| user_id | UUID | Y | FK→users | User reference | `u1...` |
| request_id | VARCHAR(50) | Y | — | Request ID | `req_abc...` |
| session_id | VARCHAR(100) | Y | — | Session ID | `sess_xyz...` |
| exception_type | VARCHAR(200) | Y | — | Exception type | `ValueError` |
| exception_message | VARCHAR(1000) | Y | — | Exception message | `Invalid input` |
| stack_trace | TEXT | Y | — | Stack trace | `Traceback...` |
| extra | JSON | NN | — | Structured data | `{"duration_ms":5}` |

**Notes:** Append-only table. No `updated_at` or `deleted_at`. Consider
partitioning by date for high-volume production deployments (Phase 3).

**Official Source:** Application runtime logging.

---

## Index Summary

### Per-Table Indexes

| Table | Index Name | Columns |
|-------|-----------|---------|
| states | ix_states_code | code |
| districts | ix_districts_state | state_id |
| categories | ix_categories_code | code |
| quotas | ix_quotas_code | code |
| rounds | ix_rounds_code | code |
| rounds | ix_rounds_number | round_number |
| courses | ix_courses_code | code |
| colleges | ix_colleges_state | state |
| colleges | ix_colleges_course | course |
| candidates | ix_candidates_air | air |
| allotments | ix_allotments_college_year_round | college_id, counselling_year, round_number |
| allotments | ix_allotments_cohort | quota_type, category, gender, is_pwd, counselling_year |
| users | ix_users_email | email |
| users | ix_users_phone | phone |
| users | ix_users_air | air |
| data_sources | ix_data_sources_type_status | source_type, status |
| source_files | ix_source_files_source_status | data_source_id, status |
| source_files | ix_source_files_academic_year | academic_year |
| source_files | ix_source_files_checksum | checksum_sha256 |
| etl_runs | ix_etl_runs_source_status | data_source_id, status |
| etl_runs | ix_etl_runs_started | started_at |
| etl_runs | ix_etl_runs_pipeline | pipeline_name |
| etl_errors | ix_etl_errors_run_severity | etl_run_id, severity |
| etl_errors | ix_etl_errors_stage | stage |
| etl_errors | ix_etl_errors_code | error_code |
| model_versions | ix_model_versions_name_status | model_name, status |
| model_versions | ix_model_versions_production | is_production, model_name |
| feature_flags | ix_feature_flags_enabled | is_enabled |
| feature_flags | ix_feature_flags_type | flag_type |
| system_settings | ix_system_settings_scope_key | scope, key |
| system_settings | ix_system_settings_feature | feature_flag_id |
| uploads | ix_uploads_user | user_id |
| uploads | ix_uploads_source_file | source_file_id |
| uploads | ix_uploads_status_type | status, upload_type |
| predictions | ix_predictions_user_created | user_id, created_at |
| predictions | ix_predictions_session | session_id |
| predictions | ix_predictions_engine_version | engine_name, engine_version |
| prediction_history | ix_prediction_history_prediction | prediction_id |
| prediction_history | ix_prediction_history_college | college_id |
| prediction_history | ix_prediction_history_rank | prediction_id, probability |
| logs | ix_logs_level_created | level, created_at |
| logs | ix_logs_logger_created | logger_name, created_at |
| logs | ix_logs_trace | trace_id |
| logs | ix_logs_user_created | user_id, created_at |
