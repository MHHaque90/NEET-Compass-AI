# Data Quality Gates — Sprint 3.6

## Phase 10: Objective Gates Before Historical Data Enters Modelling

This document defines the mandatory quality gates that every historical dataset must pass before it can enter a modelling dataset. **NOT_VERIFIED data must never silently enter a production modelling dataset.**

---

### Gate Definitions

| # | Gate | Description | Implementation | Failure Action |
|---|------|-------------|----------------|----------------|
| 1 | **Schema Validity** | All records conform to canonical schema (SeatMatrix/Allotment) | ContractValidator.STRICT mode | REJECT dataset |
| 2 | **Required-Field Completeness** | No nulls in required fields (college_id, course_id, quota_id, category_id, total_seats/rank) | ContractValidator required rules | REJECT dataset |
| 3 | **Duplicate Detection** | No duplicate logical records (composite key: college+course+quota+category+year for seat_matrix; +round+rank for allotments) | ContractValidator unique_key rules | REJECT dataset |
| 4 | **Logical Uniqueness** | One record per college/course/quota/category/year (seat_matrix) or per college/course/quota/category/round/rank (allotments) | Unique constraint validation | REJECT dataset |
| 5 | **Category Validity** | All category_id values in canonical enum (gn, bc, ew, sc, st, *_pwd) | ContractValidator enum rules | REJECT dataset |
| 6 | **Quota Validity** | All quota_id values in canonical enum for this authority | ContractValidator enum rules | REJECT dataset |
| 7 | **Round Validity** | All round_id values in known rounds (round_1, round_2, round_3, stray_vacancy) | ContractValidator enum rules | REJECT dataset |
| 8 | **Year Validity** | effective_year in expected range (2021-2026+) and matches contract | ContractValidator range rules | REJECT dataset |
| 9 | **Rank Validity** | rank in [1, 900000], integer type | ContractValidator type+range rules | REJECT dataset |
| 10 | **Seat-Count Validity** | total_seats in [0, 5000], seat_count in [1, 100], integer type | ContractValidator type+range rules | REJECT dataset |
| 11 | **Cross-Source Consistency** | Same college has consistent name/code across seat_matrix and allotments for same year | Cross-reference validation | FLAG for review |
| 12 | **Provenance Completeness** | All 10 provenance fields present (source_id, authority, dataset, effective_year, publication_version, contract_version, retrieval_timestamp, source_file_id, file_checksum, parser_version, source_url) | SourceMetadata validation | REJECT dataset |
| 13 | **Source Verification** | source_id exists in config/data_sources.yaml with verification_status = VERIFIED | Registry lookup | REJECT dataset |
| 14 | **PII Exclusion** | Zero PII columns in canonical output (validated by adapter PII blocklist) | Adapter validate_source() | REJECT dataset |
| 15 | **Temporal Availability** | All features computable at prediction time (no future data leakage) | Temporal leakage audit | REJECT dataset |

---

### Gate Classification

Each dataset (source_id × dataset × year × round) receives a classification:

| Classification | Criteria |
|----------------|----------|
| **READY** | All 15 gates PASS |
| **READY_WITH_LIMITATIONS** | Gates 1-10 PASS, gates 11-15 have documented exceptions (e.g., cross-source consistency not applicable for single source) |
| **NOT_READY** | Any of gates 1-10 FAIL, or source verification (gate 13) FAIL |

**NOT_VERIFIED sources (gate 13) can NEVER be READY.**

---

### Gate Execution Order

```
1. Source Verification (gate 13) - FAIL FAST if NOT_VERIFIED
2. Schema Validity (gate 1)
3. Required-Field Completeness (gate 2)
4. PII Exclusion (gate 14) - FAIL FAST
5. Category/Quota/Round/Year Validity (gates 5-8)
6. Rank/Seat-Count Validity (gates 9-10)
7. Duplicate Detection (gate 3)
8. Logical Uniqueness (gate 4)
9. Provenance Completeness (gate 12)
10. Cross-Source Consistency (gate 11)
11. Temporal Availability (gate 15)
```

---

### Implementation: QualityGateRunner

```python
class QualityGateRunner:
    def __init__(self, contract_registry, source_registry):
        self.contract_registry = contract_registry
        self.source_registry = source_registry
    
    def run_gates(self, records, source_id, dataset, year, round):
        results = {}
        
        # Gate 13: Source Verification
        source = self.source_registry.get(source_id)
        results['gate_13'] = source.verification_status == 'VERIFIED'
        if not results['gate_13']:
            return QualityResult(READY=False, classification='NOT_READY', gates=results)
        
        # Gate 1: Schema Validity
        contract = self.contract_registry.get(source_id, dataset, year)
        validator = ContractValidator(contract, mode='STRICT')
        validation = validator.validate_records(records)
        results['gate_1'] = validation.valid
        
        # Gate 2: Required-Field Completeness
        results['gate_2'] = all(r.is_valid for r in validation.required_checks)
        
        # Gate 14: PII Exclusion
        results['gate_14'] = not validation.pii_leaks
        
        # Gates 5-10: Enum/Range/Type
        results['gate_5'] = all(r.is_valid for r in validation.category_checks)
        results['gate_6'] = all(r.is_valid for r in validation.quota_checks)
        results['gate_7'] = all(r.is_valid for r in validation.round_checks)
        results['gate_8'] = all(r.is_valid for r in validation.year_checks)
        results['gate_9'] = all(r.is_valid for r in validation.rank_checks)
        results['gate_10'] = all(r.is_valid for r in validation.seat_count_checks)
        
        # Gate 3: Duplicate Detection
        results['gate_3'] = not validation.duplicates
        
        # Gate 4: Logical Uniqueness
        results['gate_4'] = not validation.logical_duplicates
        
        # Gate 12: Provenance Completeness
        results['gate_12'] = all(has_provenance(r) for r in records)
        
        # Gate 11: Cross-Source Consistency
        results['gate_11'] = check_cross_source_consistency(records, source_id, year)
        
        # Gate 15: Temporal Availability
        results['gate_15'] = check_temporal_availability(records, year)
        
        # Classification
        critical_gates = ['gate_1', 'gate_2', 'gate_3', 'gate_4', 'gate_5', 'gate_6', 
                          'gate_7', 'gate_8', 'gate_9', 'gate_10', 'gate_12', 'gate_13', 'gate_14', 'gate_15']
        
        if all(results[g] for g in critical_gates):
            classification = 'READY'
        elif all(results[g] for g in ['gate_1', 'gate_2', 'gate_3', 'gate_4', 'gate_5', 'gate_6', 
                                       'gate_7', 'gate_8', 'gate_9', 'gate_10', 'gate_13', 'gate_14']):
            classification = 'READY_WITH_LIMITATIONS'
        else:
            classification = 'NOT_READY'
        
        return QualityResult(
            READY=(classification == 'READY'),
            classification=classification,
            gates=results
        )
```

---

### Current Gate Status (Sprint 3.6 Reality)

| Source | Year | Dataset | Gate 13 (Verified) | Classification |
|--------|------|---------|-------------------|----------------|
| MCC | 2025 | seat_matrix | ✅ VERIFIED | READY (gates 1-15 pass in tests) |
| MCC | 2025 | allotments | ✅ VERIFIED | READY (gates 1-15 pass in tests) |
| Maharashtra | 2026 | seat_matrix | ✅ VERIFIED | READY_WITH_LIMITATIONS (fixture only, gate 11 N/A, gate 15 untested) |
| Maharashtra | 2026 | allotments | ✅ VERIFIED | READY_WITH_LIMITATIONS (fixture only) |
| Karnataka | 2026 | seat_matrix | ✅ VERIFIED | READY_WITH_LIMITATIONS (fixture only) |
| Karnataka | 2026 | allotments | ✅ VERIFIED | READY_WITH_LIMITATIONS (no fixture) |
| Uttar Pradesh | 2026 | seat_matrix | ✅ VERIFIED | NOT_READY (gate 5/6 - mappings unverified) |
| Uttar Pradesh | 2026 | allotments | ✅ VERIFIED | NOT_READY (gate 5/6 - mappings unverified) |
| All | 2021-2024 | any | ❌ NOT_VERIFIED (no contracts) | NOT_READY |

---

### Enforcement

- **Modelling dataset builder MUST run QualityGateRunner** on every source dataset before inclusion
- **NOT_READY datasets are EXCLUDED** (not imputed, not flagged, EXCLUDED)
- **READY_WITH_LIMITATIONS datasets included** but flagged in provenance
- **Gate results logged** with dataset version for audit

This is not optional. It is the quality boundary.