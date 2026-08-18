# Temporal Leakage Policy — Sprint 3.6

## Phase 5: Formal Leakage Policy

This document establishes the permanent project rule for temporal leakage prevention. Every future prediction MUST obey the information availability boundary.

---

### The Fundamental Rule

```
PREDICTION TIME
    ↓
INFORMATION AVAILABLE AT THAT TIME
    ↓
FEATURES
    ↓
PREDICTION
    ↓
FUTURE OUTCOME
```

**Information that becomes available AFTER prediction time MUST NOT be used as a feature.**

This is a PERMANENT PROJECT RULE. No exceptions. No "just this once". No "it improves accuracy".

---

### Explicit Leakage Categories (FORBIDDEN)

| Leakage Category | Description | Example |
|------------------|-------------|---------|
| **Future Counselling Rounds** | Using data from rounds that haven't occurred yet at prediction time | Predicting Round 1 using Round 2/3/Stray vacancy data |
| **Final Closing Ranks** | Using the final closing rank of a round to predict that same round | Using Round 1 final closing rank to predict Round 1 opening |
| **Future Vacancies** | Using vacancy data from later rounds or final vacancy | Predicting Round 1 using Round 2 vacancy report |
| **Later Allotment Results** | Using allotment results from future rounds | Using Round 2 allotments to predict Round 1 |
| **Future Seat Matrices** | Using seat matrix from future years | Using 2025 seat matrix to predict 2024 (impossible but must be explicit) |
| **Future-Year Statistics** | Using statistics computed from future years | Computing "median closing rank 2021-2025" to predict 2024 |
| **Aggregate Statistics with Future Data** | Any aggregation that includes observations from after prediction time | "Average closing rank for this college" computed using 2025 data to predict 2024 |

---

### Concrete Examples

#### Example 1: Predicting MCC Round 1, 2025
**Prediction Time**: Before Round 1 registration opens (typically June 2025)
**ALLOWED Features**:
- 2021-2024 seat matrices (all rounds)
- 2021-2024 allotment results (all rounds) - ONLY if aggregated per round
- 2021-2024 vacancy reports (all rounds)
- 2025 seat matrix Round 1 (published before registration)
- 2025 information bulletin
- Historical statistics computed ONLY from 2021-2024 data

**FORBIDDEN Features**:
- 2025 Round 2/3/Stray seat matrices
- 2025 Round 2/3/Stray allotment results
- 2025 Round 2/3/Stray vacancy reports
- Any statistic computed using 2025 Round 2+ data
- 2025 final closing ranks (Round 3 final)

#### Example 2: Predicting Maharashtra Round 2, 2026
**Prediction Time**: After Round 1 results declared, before Round 2 registration
**ALLOWED Features**:
- All 2021-2025 data (all rounds, all authorities)
- Maharashtra 2026 Round 1 seat matrix
- Maharashtra 2026 Round 1 allotment results
- Maharashtra 2026 Round 1 vacancy report
- Statistics computed from 2021-2025 + Maharashtra 2026 Round 1

**FORBIDDEN Features**:
- Maharashtra 2026 Round 2/3 seat matrix
- Maharashtra 2026 Round 2/3 allotment results
- Maharashtra 2026 Round 2/3 vacancy reports
- Any 2026 data beyond Round 1

#### Example 3: Computing "Historical Median Closing Rank" Feature
**CORRECT**: For predicting 2025, median computed from 2021, 2022, 2023, 2024 only
**LEAKAGE**: For predicting 2025, median computed from 2021, 2022, 2023, 2024, 2025

**RULE**: Rolling window features MUST use expanding window that EXCLUDES the prediction year.

---

### Implementation Requirements

1. **Dataset Construction**: The modelling dataset builder MUST enforce temporal boundaries. Each row's features must only use data from strictly earlier time periods.

2. **Feature Store**: Any pre-computed features (medians, percentiles, etc.) must be versioned by the latest year included. Feature `historical_median_closing_rank_v2024` includes up to 2024. Feature `historical_median_closing_rank_v2025` includes up to 2025 and CANNOT be used to predict 2025.

3. **Validation**: The temporal validation strategy (Phase 6) MUST verify no leakage by checking that test set features don't contain information from test year.

4. **Code Review**: Any ML pipeline code MUST be reviewed for temporal leakage. Leakage is a blocking issue.

5. **Documentation**: Every feature must document its "latest allowed year" for a given prediction year.

---

### Leakage Detection Checklist (for future ML implementation)

- [ ] No feature uses target year data
- [ ] No feature uses future round data within target year
- [ ] Rolling statistics use expanding window (not including current year)
- [ ] Seat matrix features only from rounds ≤ prediction round
- [ ] Allotment features only from rounds < prediction round (or same round if predicting after declaration)
- [ ] Vacancy features only from rounds < prediction round
- [ ] No "final" or "aggregate" statistics that include future data
- [ ] Cross-validation splits are temporal (not random)
- [ ] Feature store versions match prediction-time availability

---

### Enforcement

This policy is enforced by:
1. **Architecture**: Modelling dataset builder enforces temporal boundaries
2. **Tests**: Deterministic tests verify no future data in features (Phase 15)
3. **Code Review**: Mandatory leakage check in ML pipeline reviews
4. **Documentation**: Every feature documents its temporal validity

**Violations are architecture-level bugs, not model performance issues.**