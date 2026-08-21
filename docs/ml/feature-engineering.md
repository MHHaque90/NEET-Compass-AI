# Feature Engineering Reference — Sprint 4.0

## Feature Categories

### Core Features (SAFE, Always Available)
| Feature | Definition | Source Fields | Leakage |
|---------|------------|---------------|---------|
| `round_number` | Ordinal: 1, 2, 3, 4 (stray) | round | SAFE |
| `is_first_round` | round == round_1 | round | SAFE |
| `category_quota_combo` | category + "_" + quota | category, quota | SAFE |
| `institute_type` | govt/private/deemed/central | institute_type | SAFE |
| `state_quota_indicator` | quota in {so, mm, du, am} | quota | SAFE |
| `year_index` | counselling_year - min_year | counselling_year | SAFE |
| `seat_count_log` | log(total_seats + 1) | total_seats | SAFE |

### Historical Features (CONDITIONAL, Require Prior Years)
| Feature | Definition | Source Fields | Temporal Availability | Leakage |
|---------|------------|---------------|----------------------|---------|
| `historical_closing_rank_median` | Median closing rank over prior years | closing_rank, counselling_year, institute_code, course, quota, category, round | AFTER_COUNSELLING_YEAR | CONDITIONAL |
| `historical_closing_rank_p10` | 10th percentile over prior years | (same) | AFTER_COUNSELLING_YEAR | CONDITIONAL |
| `historical_closing_rank_p90` | 90th percentile over prior years | (same) | AFTER_COUNSELLING_YEAR | CONDITIONAL |
| `prior_year_closing_rank` | Closing rank at year = prediction_year - 1 | (same) | AFTER_COUNSELLING_YEAR | CONDITIONAL |
| `prior_year_seat_count` | Total seats at year = prediction_year - 1 | total_seats, counselling_year, institute_code, course, quota, category | AFTER_COUNSELLING_YEAR | CONDITIONAL |
| `seat_count_change_pct` | (seats - prior_seats) / prior_seats * 100 | (same) | AFTER_COUNSELLING_YEAR | CONDITIONAL |

### Forbidden Features
| Feature | Reason |
|---------|--------|
| `seat_availability_ratio` | Applicants unknown at prediction time |

---

## Temporal Availability Enum

```python
class TemporalAvailability(str, Enum):
    ALWAYS_AVAILABLE = "always_available"
    AFTER_ROUND_1 = "after_round_1"
    AFTER_ROUND_2 = "after_round_2"
    AFTER_ROUND_3 = "after_round_3"
    AFTER_COUNSELLING_YEAR = "after_counselling_year"
    NOT_ALLOWED = "not_allowed"
```

---

## Leakage Status Enum

```python
class LeakageStatus(str, Enum):
    SAFE = "safe"           # No temporal risk
    CONDITIONAL = "conditional"  # Requires temporal boundary check
    FORBIDDEN = "forbidden"      # Never allowed
    UNKNOWN = "unknown"          # NOT_ALLOWED (fails closed)
```

---

## Feature Definition

```python
@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    definition: str
    source_fields: list[str]
    transformation: str
    temporal_availability: TemporalAvailability
    version: str
    provenance: FeatureProvenance | None
    leakage_status: LeakageStatus
    latest_allowed_year_for_prediction: int | None = None
    latest_allowed_round_for_prediction: RoundType | None = None
```

**UNKNOWN leakage status → NOT_ALLOWED (fails closed)**

---

## FeatureEngine Usage

```python
from modelling.features.registry import FeatureRegistry
from modelling.features.engine import FeatureEngine
from modelling.contracts.dataset import SourceFacts, RoundType

registry = FeatureRegistry.create_default_registry()
engine = FeatureEngine(registry=registry)

features = engine.compute_features(
    source_facts=source_facts,
    historical_data=historical_data,
    prediction_year=2025,
    prediction_round=RoundType.ROUND_1,
)
```

**Temporal boundary enforcement**: Engine only uses data from `years < prediction_year` and `rounds < prediction_round` within `prediction_year`.

---

## Feature Registry

```python
registry = FeatureRegistry.create_default_registry()

# Get all feature names
names = registry.get_feature_names()

# Get feature definition
feat = registry.get_feature("historical_closing_rank_median")

# Validate temporal availability at prediction time
allowed = registry.validate_all_temporal_availability(prediction_year=2025, prediction_round=RoundType.ROUND_1)
```

---

## Feature Versioning

```python
from modelling.contracts.versioning import FeatureVersion

feature_version = FeatureVersion.create(
    version="features_v1",
    feature_definitions={...},
    feature_computation_code_hash="abc123",
    changed_from_previous=["added_new_feature"],
    deprecated_features=["old_feature"],
)
```

**Rule**: Any feature change → new version. Silent changes forbidden.

---

## Feature Provenance

```python
from modelling.features.provenance import FeatureProvenance

prov = FeatureProvenance.create(
    feature_name="historical_closing_rank_median",
    feature_version="features_v1",
    source_record_ids=["rec_1", "rec_2", ...],
    source_file_ids=["file_1", "file_2", ...],
    transformation_logic="median(closing_rank) for years < prediction_year",
    computed_by="FeatureEngine",
)
```

**Integrity verification**:
```python
prov.verify_integrity(expected_logic="median(closing_rank) for years < prediction_year")
```

---

## Leakage Prevention

The `LeakageChecker` validates:
1. **UNKNOWN temporal availability** → REJECTED
2. **FORBIDDEN leakage status** → REJECTED
3. **Future year data** in historical aggregations → REJECTED
4. **Future round data** → REJECTED
5. **Target-derived fields** (closing_rank, opening_rank, etc.) → REJECTED (except CONDITIONAL historical features)
6. **Future seat matrix** → REJECTED
7. **Aggregate with future data** → REJECTED

**Rule**: UNKNOWN temporal availability = NOT_ALLOWED = REJECTED

---

## Adding a New Feature

1. Define `FeatureDefinition` with all metadata
2. Set `leakage_status` appropriately (SAFE/CONDITIONAL/FORBIDDEN)
3. Set `temporal_availability` correctly
4. Register in `FeatureRegistry`
4. Increment `feature_version` in `FeatureVersion.create()`
5. Add deterministic test in `tests/unit/modelling/features/`

---

## Example: Custom Feature

```python
from modelling.features.types import FeatureDefinition, TemporalAvailability, LeakageStatus
from modelling.features.registry import FeatureRegistry

custom_feature = FeatureDefinition(
    name="rank_to_seat_ratio",
    definition="Closing rank divided by total seats",
    source_fields=["closing_rank", "total_seats"],
    transformation="closing_rank / total_seats if total_seats > 0 else None",
    temporal_availability=TemporalAvailability.AFTER_COUNSELLING_YEAR,
    version="features_v2",
    provenance=None,
    leakage_status=LeakageStatus.CONDITIONAL,
    latest_allowed_year_for_prediction=None,  # Uses expanding window
    latest_allowed_round_for_prediction=None,
)

registry = FeatureRegistry.create_default_registry()
registry.register(custom_feature)

# Increment feature version
# FeatureVersion.create(version="features_v2", ...)
```