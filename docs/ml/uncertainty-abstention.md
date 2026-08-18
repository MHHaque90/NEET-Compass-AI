# Uncertainty and Abstention Policy — Sprint 3.6

## Phase 9: How the Future System Behaves When Evidence Is Weak

This document defines the uncertainty quantification and abstention requirements for any future prediction system. **Reliability is the primary goal** - the system MUST have the ability to abstain rather than produce misleadingly confident predictions.

---

### Confidence Levels (Mandatory Output)

Every prediction MUST include a confidence level from this taxonomy:

| Level | Label | Meaning | Action |
|-------|-------|---------|--------|
| **HIGH** | HIGH_CONFIDENCE | Strong evidence, narrow uncertainty, well-calibrated | Show prediction with narrow interval |
| **MEDIUM** | MEDIUM_CONFIDENCE | Moderate evidence, wider uncertainty, acceptable calibration | Show prediction with wide interval, flag as uncertain |
| **LOW** | LOW_CONFIDENCE | Weak evidence, very wide uncertainty, or calibration issues | Show prediction ONLY if user explicitly requests, heavy warning |
| **NONE** | INSUFFICIENT_EVIDENCE | No reliable basis for prediction | **ABSTAIN** - show "Insufficient historical data for reliable prediction" |

---

### Abstention Triggers (Mandatory)

The system MUST abstain (return INSUFFICIENT_EVIDENCE) when ANY of:

| Trigger | Threshold | Rationale |
|---------|-----------|-----------|
| **Insufficient historical data** | < 2 prior years for same college/course/quota/category/round | Cannot compute stable baseline |
| **New college** | No historical records for this college code | No basis for college-specific prediction |
| **New category/quota combo** | < 5 historical records for this combo | Pool-level fallback may apply |
| **Extrapolation** | Student rank outside historical range (below min or above max observed) | Predicting beyond evidence |
| **Calibration failure** | ECE > 0.1 on validation for this subgroup | Probabilities unreliable |
| **Seat matrix change** | > 20% seat count change from prior year | Historical relationship broken |
| **Policy change** | Known counselling rule change (e.g., new quota, category) | Historical patterns invalid |
| **Data quality gate failure** | Any Phase 10 gate fails for this prediction's input data | Garbage in, garbage out |

---

### Uncertainty Quantification Requirements

**For Numeric Predictions (Closing Rank):**
- MUST provide prediction interval (e.g., 90% PI)
- Interval width MUST reflect true uncertainty (validated via coverage)
- If coverage < 85% for nominal 90% → downgrade confidence

**For Probability Predictions (Admission Likelihood):**
- MUST be calibrated (ECE < 0.05)
- MUST provide confidence interval for probability (e.g., via bootstrap)
- If calibration fails → downgrade to LOW or abstain

**For Ranking Predictions:**
- MUST provide confidence bounds on rank positions
- If NDCG@10 on validation < 0.3 → LOW confidence

---

### Confidence Decision Logic

```
function determine_confidence(prediction_context):
    # Hard abstention gates
    if any(abstention_trigger_active):
        return INSUFFICIENT_EVIDENCE
    
    # Evidence strength
    n_historical = count_prior_years(prediction_context.group_key)
    seat_stability = seat_change_pct(prediction_context)
    calibration = calibration_error(prediction_context.subgroup)
    
    # Score components (0-1)
    evidence_score = min(n_historical / 5, 1.0)  # 5+ years = max
    stability_score = 1.0 - min(seat_stability / 0.5, 1.0)  # <20% change = max
    calibration_score = 1.0 - min(calibration / 0.1, 1.0)  # ECE<0.05 = max
    
    composite = 0.4 * evidence_score + 0.3 * stability_score + 0.3 * calibration_score
    
    if composite >= 0.8:
        return HIGH_CONFIDENCE
    elif composite >= 0.5:
        return MEDIUM_CONFIDENCE
    elif composite >= 0.3:
        return LOW_CONFIDENCE
    else:
        return INSUFFICIENT_EVIDENCE
```

---

### User-Facing Communication

| Confidence | Display | Example Text |
|------------|---------|--------------|
| HIGH | ✅ Green badge | "Predicted closing rank: 12,450 (90% PI: 11,200–13,800)" |
| MEDIUM | ⚠️ Yellow badge | "Predicted closing rank: 12,450 (90% PI: 9,800–16,200) — Moderate confidence" |
| LOW | 🟠 Orange badge | "Predicted closing rank: 12,450 (90% PI: 5,000–25,000) — Low confidence, interpret cautiously" |
| NONE | ❌ Red badge | "Insufficient historical data for reliable prediction. Showing general trends only." |

**Never show a single number without its uncertainty and confidence level.**

---

### Implementation Requirements

1. **Abstention is a first-class output**, not an error
2. **Confidence level computed per-prediction**, not global
3. **Triggers logged** for audit (why did we abstain?)
4. **Fallback to baselines**: If ML abstains, try baselines (Phase 7). If baselines abstain, show INSUFFICIENT_EVIDENCE.
5. **No "confidence hacking"**: Cannot lower thresholds to reduce abstention rate

---

### Acceptance Criteria

A prediction system passes reliability review ONLY if:
- [ ] Abstention rate reported and justified
- [ ] Calibration holds within each confidence level
- [ ] Coverage of prediction intervals matches nominal within each confidence level
- [ ] No HIGH confidence predictions on abstention-trigger cases
- [ ] User study confirms confidence labels match perceived reliability

---

### Current Feasibility

**With current data (MCC 2025 only):**
- ALL predictions would be INSUFFICIENT_EVIDENCE
- No prior years for any college
- No calibration possible
- No seat stability assessment possible

**This is correct behavior.** The system should honestly say "I don't know" rather than hallucinate.