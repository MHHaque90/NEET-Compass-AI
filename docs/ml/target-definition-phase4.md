# Target Analysis and First Modelling Target Selection — Sprint 3.6

## Phase 4: Evaluate Possible Future Targets

This document evaluates candidate prediction targets based on data availability, label availability, prediction-time availability, leakage risk, and suitability. The selection must be based on data availability and reliability, NOT perceived product appeal.

---

### Candidate Targets Evaluation

#### Target 1: Closing-Rank Forecasting

| Aspect | Assessment |
|--------|------------|
| **Exact Definition** | Predict the closing rank (last admitted rank) for a given college × course × quota × category × round × year |
| **Required Data** | Allotment records with rank, aggregated to closing rank per group |
| **Label Availability** | ✅ MCC 2025: Allotment records have rank per seat. Can compute closing rank per group by taking max(rank) per college/course/quota/category/round |
| **Prediction-Time Availability** | ✅ At prediction time (before round), we know: college, course, quota, category, round, year. We do NOT know the closing rank (that's the target) |
| **Leakage Risk** | HIGH if using future rounds. Must only use rounds < target round, or prior years. Using Round 3 data to predict Round 1 is LEAKAGE. |
| **Historical Coverage** | ❌ ONLY MCC 2025 available. 1 year = insufficient for temporal validation |
| **Expected Granularity** | Per college × course × quota × category × round × year (~thousands of groups) |
| **Limitations** | - Single year (2025) only<br>- No state historical data<br>- Opening rank not available<br>- Seat matrix changes year to year |
| **Suitability** | LOW - Insufficient historical coverage for reliable modelling |

---

#### Target 2: College/Seat Outcome Prediction (Admission Likelihood)

| Aspect | Assessment |
|--------|------------|
| **Exact Definition** | Given a student's NEET rank, category, quota preference, predict probability of admission to each college/course/quota/category combination |
| **Required Data** | Allotment records + student rank distribution + preference data |
| **Label Availability** | ❌ NO - We have allotment records (who GOT seats), but NOT student preference lists or full applicant pool. Cannot compute P(admit \| rank) without knowing who applied and their preferences. |
| **Prediction-Time Availability** | Student rank known at prediction time. College/course/quota/category known. But historical admission probabilities require applicant pool data. |
| **Leakage Risk** | EXTREME - Using final allotment to predict earlier rounds leaks information about seat availability and competition |
| **Historical Coverage** | ❌ Only MCC 2025 allotments. No applicant pool data ever. |
| **Expected Granularity** | Per student rank × college × course × quota × category × round |
| **Limitations** | - No student preference data (PII)<br>- No applicant pool counts<br>- Cannot distinguish "didn't apply" from "applied but didn't get"<br>- Survivorship bias in allotment data |
| **Suitability** | NOT SUITABLE - Fundamentally unidentifiable without applicant pool data |

---

#### Target 3: Student-to-College Ranking (Preference Matching)

| Aspect | Assessment |
|--------|------------|
| **Exact Definition** | Rank colleges by predicted admission probability for a given student profile |
| **Required Data** | Same as Target 2 + student preference ordering |
| **Label Availability** | ❌ NO - No student preference data available (PII protected by design) |
| **Prediction-Time Availability** | Student provides preferences at prediction time, but historical preferences unavailable |
| **Leakage Risk** | HIGH - Same as Target 2 |
| **Historical Coverage** | ❌ Zero historical preference data |
| **Expected Granularity** | Per student × college ranking |
| **Limitations** | - PII constraints prevent collecting preference data<br>- Cannot train on historical preferences<br>- Would require synthetic or proxy preferences |
| **Suitability** | NOT SUITABLE - No training data possible under PII constraints |

---

#### Target 4: Admission Likelihood (Binary: Will I get a seat?)

| Aspect | Assessment |
|--------|------------|
| **Exact Definition** | Binary classification: Given student rank, category, quota, round - will they get ANY seat in the system? |
| **Required Data** | Allotment records showing which ranks got seats |
| **Label Availability** | ⚠️ PARTIAL - From MCC 2025 allotments, we can see which (rank, category, quota, round) combinations received seats. But this is "did get seat" not "will get seat" - the latter requires knowing seat availability at prediction time. |
| **Prediction-Time Availability** | At prediction time (before round), we know: student rank, category, quota, round. We know total seats from seat matrix. We DON'T know how many higher-ranked applicants will choose those seats. |
| **Leakage Risk** | HIGH - Using final allotment status leaks information about seat competition |
| **Historical Coverage** | ❌ Only MCC 2025 |
| **Expected Granularity** | Per rank × category × quota × round × year |
| **Limitations** | - Single year<br>- Doesn't account for preference heterogeneity<br>- Seat matrix changes annually<br>- "Any seat" is not actionable for counselling |
| **Suitability** | LOW - Insufficient coverage, limited actionability |

---

#### Target 5: Opening Rank Forecasting

| Aspect | Assessment |
|--------|------------|
| **Exact Definition** | Predict the opening rank (first admitted rank) for a given college × course × quota × category × round × year |
| **Required Data** | Allotment records with rank, aggregated to min(rank) per group |
| **Label Availability** | ❌ NO - Current canonical Allotment has single rank per record (the allotted candidate's rank). We don't know if it's opening or closing. Would need to aggregate per group. |
| **Prediction-Time Availability** | Same as closing rank |
| **Leakage Risk** | Same as closing rank |
| **Historical Coverage** | ❌ Only MCC 2025 |
| **Limitations** | - Same as closing rank but even less information (only 1 data point per group) |
| **Suitability** | LOWER than closing rank |

---

### Summary Comparison

| Target | Label Available | Prediction-Time Features | Leakage Risk | Historical Years | Suitability |
|--------|-----------------|-------------------------|--------------|------------------|-------------|
| Closing Rank | ✅ MCC 2025 | ✅ Seat matrix + prior years | HIGH (manageable) | 1 (2025) | LOW |
| Admission Likelihood | ❌ No applicant pool | ⚠️ Partial | EXTREME | 0 | NONE |
| College Ranking | ❌ No preferences | ⚠️ Partial | EXTREME | 0 | NONE |
| Binary Admission | ⚠️ Partial (MCC 2025) | ⚠️ Partial | HIGH | 1 | LOW |
| Opening Rank | ❌ Not in canonical | ⚠️ Partial | HIGH | 1 | NONE |

---

### First Modelling Target Selection

**DECISION: NO TARGET READY FOR MODELLING**

**Justification based on evidence:**

1. **Insufficient Historical Coverage**: Only ONE year (MCC 2025) of allotment data exists in the repository with full contract/adapter/validation coverage. Temporal validation requires at minimum 3 years (train/validate/test), preferably 5+.

2. **No State Historical Data**: Maharashtra, Karnataka, and Uttar Pradesh have ZERO historical allotment data in the repository. Any multi-state model would be trained on MCC only.

3. **Single Year Cannot Support Temporal Validation**: The validation strategy (Phase 6) requires OLDER YEARS → TRAIN, NEXT YEAR → VALIDATE, NEWEST → TEST. With 1 year, this is impossible.

4. **Closing Rank Aggregation Gap**: While MCC 2025 allotments have per-record ranks, the canonical model doesn't expose aggregated closing ranks per college/course/quota/category/round. This would need to be computed as a derived feature, but still only for 1 year.

5. **No Applicant Pool Data**: Admission likelihood targets require knowing the denominator (how many applied), which is never published and would be PII.

6. **UP Mappings Unverified**: Even if UP data were downloaded, the category/quota mappings are explicitly documented as placeholders.

---

### What Would Be Needed to Enable Modelling

| Requirement | Current State | Needed |
|-------------|---------------|--------|
| MCC Historical Allotments | 2025 only | 2021-2024 downloaded, parsed, validated |
| State Historical Allotments | NONE | 2021-2025 for each state |
| Minimum Years for Temporal Val | 1 | 4+ (e.g., 2021-2024 train, 2025 val, 2026 test) |
| Verified UP Mappings | Placeholder | Verified against real UP source |
| Vacancy Data | None | Vacancy canonical model + ingestion |
| Opening Rank | Not in canonical | Aggregate from allotments |

---

### Explicit Statement

**NO TARGET READY FOR MODELLING.**

This is an acceptable and scientifically honest Sprint 3.6 outcome. The evidence says we do NOT have enough trustworthy historical data to build a reliable NEET prediction system. The first modelling target cannot be selected until:
- MCC 2021-2024 allotments are ingested and validated
- At least one state's historical allotments are ingested and validated
- Minimum 4 years of data exist for temporal validation

The repository architecture is READY (Sprint 3.5 certified). The DATA is NOT.