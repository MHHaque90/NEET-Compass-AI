# Dataset Versioning — Sprint 3.6

## Phase 11: Reproducible Dataset Identity

This document defines how future modelling dataset versions are traced to their sources. Reuse the existing provenance system - no third-party data versioning infrastructure.

---

### Dataset Version Identity

A modelling dataset version is a deterministic hash of its constituent parts:

```
dataset_version = SHA256(
    sorted(source_file_ids) + "|" +
    transformation_version + "|" +
    feature_version + "|" +
    quality_gate_version
)[:16]  # 16-char prefix for readability
```

---

### Components

#### 1. Source File Identities (from existing provenance)

Each source file ingested has a deterministic `source_file_id`:
```
source_file_id = f"{source_id}_{dataset}_{effective_year}_{checksum[:12]}"
```

Where `checksum` = SHA-256 of raw file bytes (from `etl.contracts.canonical.checksum`).

**This already exists in the provenance system.**

#### 2. Transformation Version

Version of the dataset construction logic (aggregation, joining, feature computation):
```
transformation_version = "modelling_dataset_v1"
```
Increment on ANY change to:
- Aggregation logic (e.g., how closing rank computed from allotments)
- Join logic (e.g., seat_matrix + allotments join keys)
- Missing value handling
- Derived feature computation

#### 3. Feature Version

Version of the feature engineering pipeline:
```
feature_version = "features_v1"
```
Increment on ANY change to:
- Feature definitions (new features, removed features, changed computation)
- Feature encoding (e.g., category encoding changes)
- Scaling/normalization changes

#### 4. Quality Gate Version

Version of the quality gate thresholds and logic:
```
quality_gate_version = "quality_gates_v1"
```
Increment on ANY change to:
- Gate thresholds
- Gate logic
- Classification criteria (READY/READY_WITH_LIMITATIONS/NOT_READY)

---

### Dataset Metadata Record

Every modelling dataset version produces a metadata record:

```python
@dataclass
class ModellingDatasetMetadata:
    dataset_version: str           # SHA256 prefix
    created_timestamp: str         # UTC ISO
    source_file_ids: list[str]     # All source_file_ids included
    source_checksums: dict[str, str]  # source_file_id -> SHA256
    transformation_version: str
    feature_version: str
    quality_gate_version: str
    quality_gate_results: dict     # Per-source gate results
    row_count: int
    column_count: int
    year_range: tuple[int, int]    # (min_year, max_year)
    authorities: list[str]         # e.g., ["MCC", "MAH"]
    target_variables: list[str]    # e.g., ["closing_rank"]
    schema_hash: str               # SHA256 of column names + types
```

---

### Reproducibility Guarantee

**Same inputs → Same dataset_version**

Because:
1. `source_file_id` is deterministic from file bytes (SHA-256)
2. Transformation/feature/quality versions are explicit
3. Dataset construction is pure function (no randomness, no external state)

---

### Integration with Existing Provenance

**Reuse, don't rebuild:**

| Existing System | Reused For |
|-----------------|------------|
| `etl.contracts.canonical.checksum.compute_file_checksum` | Source file SHA-256 |
| `etl.contracts.sources.*.provenance.build_source_file_id` | Source file identity |
| `etl.contracts.canonical.SourceMetadata` | Per-record provenance |
| `etl.contracts.registry.ContractRegistry` | Contract version lookup |
| `etl.contracts.sources.*.pipeline.FileRegistry` | File-level idempotency |

The modelling dataset builder:
1. Queries FileRegistry for all ingested source files matching criteria
2. Retrieves SourceMetadata for each record
3. Builds dataset with full provenance chain
4. Computes dataset_version from components
5. Stores ModellingDatasetMetadata

---

### Versioning Example

```
# Ingest MCC 2025 seat matrix (file A) and allotments (file B)
# source_file_id_A = "mcc_seat_matrix_2025_a1b2c3d4e5f6"
# source_file_id_B = "mcc_allotments_2025_f6e5d4c3b2a1"

# Build dataset with transformation v1, features v1, quality v1
# dataset_version = SHA256(
#     "mcc_seat_matrix_2025_a1b2c3d4e5f6|mcc_allotments_2025_f6e5d4c3b2a1|modelling_dataset_v1|features_v1|quality_gates_v1"
# )[:16]
# = "k7m9x2p4q8r1w3z5"
```

If file A changes (new download), checksum changes → source_file_id changes → dataset_version changes.

If feature engineering changes → feature_version changes → dataset_version changes.

**Perfect traceability.**

---

### Storage

ModellingDatasetMetadata stored in:
- Database table `modelling_dataset_versions` (new table, future migration)
- JSON file in `data/exports/modelling_datasets/{dataset_version}.json`

**Not in this sprint** - this is the specification for future implementation.

---

### Key Principle

**No DVC, no MLflow, no third-party data versioning.** The existing SHA-256 + provenance + contract versioning system is sufficient and already proven.