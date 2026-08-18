# Baseline Strategy — Sprint 3.6

## Phase 7: Non-ML Baselines

This document defines the non-ML baselines that any future ML model MUST beat. The principle: **If a simple baseline is more reliable than a complex ML model, the simple baseline wins.**

---

### Baseline Philosophy

Before investing in ML complexity, we establish what's achievable with simple, transparent, interpretable methods. These baselines:
- Use only prediction-time available information
- Are fully reproducible
- Have clear failure modes
- Serve as the "null hypothesis" for ML value

---

### BASELINE 1: Previous Comparable Historical Outcome

**Definition**: For predicting target in year Y, use the actual outcome from year Y-1 for the same college/course/quota/category/round.

**Applicability**: Closing rank forecasting, opening rank forecasting.

**Implementation**:
```python
def baseline_previous_year(group_key, target_year, historical_data):
    """group_key = (college, course, quota, category, round)"""
    prior_year = target_year - 1
    if prior_year in historical_data[group_key]:
        return historical_data[group_key][prior_year]
    return None  # Abstain if no prior year
```

**Strengths**: Captures institutional stability, simple, interpretable
**Weaknesses**: Fails for new colleges, seat matrix changes, policy shifts
**Prediction-Time Available**: ✅ Yes - prior year data is historical

---

### BASELINE 2: Multi-Year Median / Quantile

**Definition**: For predicting target in year Y, use the median (or p10/p90 for intervals) of available prior years for the same group.

**Applicability**: Closing rank forecasting with uncertainty intervals.

**Implementation**:
```python
def baseline_multiyear_quantile(group_key, target_year, historical_data, q=0.5):
    prior_years = [y for y in historical_data[group_key] if y < target_year]
    if len(prior_years) >= 2:  # Minimum 2 years for median
        values = [historical_data[group_key][y] for y in prior_years]
        return np.quantile(values, q)
    return None  # Abstain if insufficient history
```

**Strengths**: Robust to single-year outliers, provides uncertainty via quantiles
**Weaknesses**: Requires ≥2 prior years, slow to adapt to trends
**Prediction-Time Available**: ✅ Yes

---

### BASELINE 3: Simple Statistical / Ranking Approach

**Definition**: Use seat matrix + rank-to-seat ratio heuristics.

**For Closing Rank Prediction**:
```python
def baseline_seat_ratio(college, course, quota, category, round, year, seat_matrix, prior_allotments):
    # Get seats available
    seats = seat_matrix.get(college, course, quota, category, year)
    if not seats:
        return None
    
    # Estimate competition from prior years
    prior_closing = baseline_multiyear_quantile((college, course, quota, category, round), year, prior_allotments)
    
    # Simple heuristic: closing_rank ≈ prior_closing * (seats_this_year / seats_prior_year)
    # Or use rank-to-seat ratio from prior years
    ratios = []
    for y in prior_allotments.get((college, course, quota, category, round), {}):
        s = seat_matrix.get(college, course, quota, category, y)
        r = prior_allotments[(college, course, quota, category, round)][y]
        if s and r:
            ratios.append(r / s)
    
    if ratios:
        median_ratio = np.median(ratios)
        return int(median_ratio * seats)
    return None
```

**For Admission Likelihood (Binary)**:
```python
def baseline_admission_likelihood(student_rank, college, course, quota, category, round, year, seat_matrix, prior_allotments):
    # Get prior closing ranks
    prior_closings = [prior_allotments.get((college, course, quota, category, round), {}).get(y) 
                      for y in prior_allotments.get((college, course, quota, category, round), {}) 
                      if y < year]
    
    if not prior_closings:
        return None
    
    # Probability = fraction of prior years where student_rank ≤ closing_rank
    successes = sum(1 for c in prior_closings if student_rank <= c)
    return successes / len(prior_closings)
```

**Strengths**: Uses domain knowledge (seat counts), interpretable
**Weaknesses**: Assumes stable rank-to-seat ratio, ignores preference changes
**Prediction-Time Available**: ✅ Yes - seat matrix published before counselling

---

### BASELINE 4: Category/Quota Pool Aggregation (Fallback)

**Definition**: When college-level history is insufficient, aggregate to category/quota/round level.

```python
def baseline_pool_level(category, quota, round, year, prior_allotments, seat_matrix):
    # Aggregate all colleges for this category/quota/round
    all_closings = []
    for college in prior_allotments:
        for y in prior_allotments[college]:
            if y < year:
                all_closings.append(prior_allotments[college][y])
    
    if len(all_closings) >= 5:
        return np.median(all_closings)
    return None
```

**Use Case**: New colleges, sparse data
**Trade-off**: Less specific but more data

---

### Baseline Comparison Protocol

Any future ML model MUST be evaluated against ALL applicable baselines:

| Metric | ML Model | Baseline 1 | Baseline 2 | Baseline 3 | Baseline 4 |
|--------|----------|------------|------------|------------|------------|
| MAE | ? | ✓ | ✓ | ✓ | ✓ |
| Median AE | ? | ✓ | ✓ | ✓ | ✓ |
| Calibration | ? | N/A | N/A | ✓ | N/A |
| Coverage (if intervals) | ? | N/A | ✓ | N/A | N/A |

**Decision Rule**: ML model advances to RELIABILITY_REVIEW only if it **beats the best baseline on the primary metric (MAE for numeric, Brier/LogLoss for probability) with statistical significance** AND meets reliability gates (Phase 12).

---

### Baseline Implementation Requirements

1. **Deterministic**: Same inputs → same outputs (no randomness)
2. **Temporal**: Only uses data from years < target year
3. **Abstention**: Returns None (not a prediction) when insufficient data
4. **Versioned**: Baseline logic version tracked with dataset version
5. **Tested**: Unit tests for each baseline with known inputs/outputs

---

### Current Baseline Feasibility

**With current data (MCC 2025 only):**
- Baseline 1: ❌ No prior year
- Baseline 2: ❌ Need ≥2 prior years
- Baseline 3: ❌ No prior allotments for ratio
- Baseline 4: ❌ No prior allotments for pool

**ZERO baselines are computable with current repository data.**

This reinforces: **NO TARGET READY FOR MODELLING.**