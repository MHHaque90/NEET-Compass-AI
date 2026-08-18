# Data Quality Validation Against Sprint 3.6 Gates — Sprint 3.7

## Phase 9: Quality Gate Evaluation for Historical Data

---

### Sprint 3.6 Quality Gates (15 Gates)

| # | Gate | Description | Pass Criteria |
|---|------|-------------|---------------|
| 1 | Schema Validity | All records conform to canonical schema | ContractValidator.STRICT passes |
| 2 | Required-Field Completeness | No nulls in required fields | All required fields present |
| 3 | Duplicate Detection | No duplicate logical records | Unique key validation passes |
| 4 | Logical Uniqueness | One record per logical key | Composite key uniqueness |
| 5 | Category Validity | All category_id in canonical enum | Enum validation passes |
| 6 | Quota Validity | All quota_id in canonical enum | Enum validation passes |
| 7 | Round Validity | All round_id in known rounds | Enum validation passes |
| 8 | Year Validity | effective_year in expected range | Range validation passes |
| 9 | Rank Validity | rank in [1, 900000], integer | Type + range validation |
| 10 | Seat-Count Validity | seats in valid range, integer | Type + range validation |
| 11 | Cross-Source Consistency | Same college consistent across datasets | Cross-reference validation |
| 12 | Provenance Completeness | All 10 provenance fields present | SourceMetadata complete |
| 13 | Source Verification | source_id VERIFIED in config | Registry lookup passes |
| 14 | PII Exclusion | Zero PII columns in canonical | Adapter PII blocklist |
| 15 | Temporal Availability | Features computable at prediction time | Leakage audit passes |

---

### Current Gate Status by Source/Year

| Source | Year | Dataset | Gates 1-10 | Gate 11 | Gate 12 | Gate 13 | Gate 14 | Gate 15 | Classification |
|--------|------|---------|------------|---------|---------|---------|---------|---------|----------------|
| MCC | 2025 | seat_matrix | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **READY** |
| MCC | 2025 | allotments | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **READY** |
| MCC | 2024 | seat_matrix | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2024 | allotments | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2023 | seat_matrix | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2023 | allotments | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2022 | seat_matrix | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2022 | allotments | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2021 | seat_matrix | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| MCC | 2021 | allotments | ❌ No contract | N/A | ❌ | ❌ | N/A | N/A | NOT_READY |
| Maharashtra | 2026 | seat_matrix | ✅ | N/A* | ✅ | ✅ | ✅ | ⚠️ | READY_WITH_LIMITATIONS |
| Maharashtra | 2026 | allotments | ✅ | N/A* | ✅ | ✅ | ✅ | ⚠️ | READY_WITH_LIMITATIONS |
| Karnataka | 2026 | seat_matrix | ✅ | N/A* | ✅ | ✅ | ✅ | ⚠️ | READY_WITH_LIMITATIONS |
| Karnataka | 2026 | allotments | ✅ | N/A* | ✅ | ✅ | ✅ | ⚠️ | READY_WITH_LIMITATIONS |
| UP | 2026 | seat_matrix | ❌ Gate 5/6 | N/A* | ✅ | ✅ | ✅ | ⚠️ | NOT_READY |
| UP | 2026 | allotments | ❌ Gate 5/6 | N/A* | ✅ | ✅ | ✅ | ⚠️ | NOT_READY |

*Gate 11 (Cross-Source) N/A for single-source test fixtures

---

### Classification Rules

| Classification | Criteria |
|----------------|----------|
| **READY** | All 15 gates PASS |
| **READY_WITH_LIMITATIONS** | Gates 1-10 PASS, gates 11-15 have documented exceptions |
| **NOT_READY** | Any of gates 1-10 FAIL, or gate 13 FAIL |

**NOT_VERIFIED sources (gate 13) can NEVER be READY.**

---

### Validation Protocol for Sprint 3.7 Historical Data

For each newly verified historical dataset:

1. **Run ContractValidator.STRICT** on actual/fixture data
2. **Check all 15 gates** programmatically
3. **Document** any gate failures with evidence
4. **Classify** per rules above
5. **Update** modelling_readiness.yaml

**No lowering of standards** — historical data must meet same gates as 2025/2026 data.