# Prediction Specification

## Overview

The prediction engine produces personalized college recommendations for NEET
candidates. Every prediction is explainable, auditable, and reproducible.

## Prediction Lifecycle

1. Candidate submits profile
2. API receives prediction request
3. ML engine evaluates each college
4. Recommendations ranked by probability
5. Strategy and choice-filling order generated
6. Results stored in predictions + prediction_history
7. Response returned with explanations

## Prediction Inputs (Required)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `air` | integer | NEET All-India Rank | 85000 |
| `marks` | integer | NEET score (out of 720) | 620 |
| `category` | enum | Reservation category | OBC |
| `domicile_state` | string | Domicile state | MAHARASHTRA |
| `gender` | enum | NEUTRAL, MALE, FEMALE | NEUTRAL |
| `quota_type` | enum | AIQ or STATE | AIQ |
| `counselling_year` | integer | Year of counselling | 2025 |

## Prediction Inputs (Optional)

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `is_pwd` | boolean | Person with disability | false |
| `is_minority` | boolean | Minority reservation | false |
| `budget_inr` | numeric | Max budget | unlimited |
| `target_round` | integer | Target counselling round | Round 1 |

## Prediction Outputs

| Field | Type | Description |
|-------|------|-------------|
| `college_id` | UUID | College recommended |
| `probability` | float (0-1) | Chance of getting this college |
| `expected_round` | integer | Which round to expect |
| `confidence` | float (0-1) | Model confidence |
| `reasons` | list | Explanation blocks |
| `strategy` | dict | Counselling strategy |

## Explanation Format

Each reason is JSON:

```json
{
  "type": "historical_rank_match",
  "message": "Your AIR is within historical range for this college",
  "data": {"your_air": 85000, "historical_low": 75000, "confidence": 0.85}
}
```

## Engine Architecture

### Port (Interface)

```python
class RecommendationEngine(ABC):
    name: str
    version: str
    def predict(candidate, colleges) -> Sequence[Recommendation]: ...
```

### Default: UnavailableEngine

Refuses to fabricate scores. Raises `PredictionUnavailable` when no real
engine is configured.

### Engine Selection

Configured via `ML_RECOMMENDATION_ENGINE` env var:
- `unavailable` (default) — refuses to predict
- `rule_based` — closing-rank analysis (Phase 4)
- `ml_boosting` — gradient boosting (Phase 4)
- `ml_ensemble` — ensemble model (Phase 4)

## Reproducibility

Every prediction is stored with full provenance in `predictions` table
linked to `model_versions.model_version_id`, `engine_name`,
`engine_version`. To reproduce, load the same source data and model version.

## Audit Trail

| Table | Records |
|-------|---------|
| `predictions` | One row per prediction request |
| `prediction_history` | One row per college recommendation |
| `model_versions` | Model registry with metrics |
| `logs` | All prediction-related events |
