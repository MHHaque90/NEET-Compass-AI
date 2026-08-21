# Modelling Engine Architecture — Sprint 4.0

## Overview

The modelling engine is a production-grade foundation for future ML modelling in NEET Compass AI. It enforces reliability gates, temporal validation, and leakage prevention at the architecture level.

**Current State**: `RESEARCH_ONLY` — Training blocked, no production model.

---

## Architecture Components

```
modelling/
├── contracts/
│   ├── dataset.py          # ModellingDatasetContract, ModellingRecord, SourceFacts, DerivedFeatures, Targets, Provenance, TemporalMetadata
│   └── versioning.py       # DatasetVersion, FeatureVersion, TransformationVersion, QualityGateVersion
├── features/
│   ├── types.py            # TemporalAvailability, LeakageStatus, FeatureDefinition
│   ├── engine.py           # FeatureEngine (temporal boundary enforcement)
│   ├── registry.py         # FeatureRegistry (default features)
│   └── provenance.py       # FeatureProvenance, FeatureProvenanceSet
├── leakage/
│   └── checker.py          # LeakageChecker (fails closed)
├── targets/
│   └── engine.py           # TargetEngine (NO_TARGET_READY enforcement)
├── splits/
│   └── engine.py           # TemporalSplitter (chronological, fails closed)
├── baselines/
│   └── engine.py           # BaselineEngine (4 baselines, gated)
├── evaluation/
│   └── engine.py           # EvaluationEngine (reliability metrics)
├── uncertainty/
│   └── engine.py           # UncertaintyEngine (confidence + abstention)
├── reliability/
│   └── gates.py            # ReliabilityGate (lifecycle stages)
├── registry/
│   └── interface.py        # ModelRegistry (metadata only)
├── experiments/
│   └── tracker.py          # ExperimentTracker (reproducibility)
├── training/
│   └── guard.py            # TrainingGuard (impossible to bypass)
├── quality/
│   └── gates.py            # ModellingQualityGates (13 gates)
└── config/
    └── modelling_readiness.py  # Reads config/modelling_readiness.yaml
```

---

## Data Flow

```
Historical ETL Data (SeatMatrix + Allotment)
         ↓
Quality Gates (13 gates) → ModellingQualityGates
         ↓
FeatureEngine.compute_features()
  - Temporal boundaries enforced
  - Only data from years < prediction_year
  - Only rounds < prediction_round
         ↓
LeakageChecker.check_record()
  - Fails closed on ANY violation
         ↓
TemporalSplitter.split()
  - Chronological: TRAIN → VALIDATION → TEST
  - Fails closed if < 3 verified years
         ↓
TrainingGuard.check_training_allowed()
  - Blocks if: temporal blocked, insufficient years, target not ready,
               leakage failed, quality gates failed, provenance incomplete
         ↓
[FUTURE] Model Training
         ↓
ReliabilityGate checks (RESEARCH_ONLY → MODEL_CANDIDATE → RELIABILITY_REVIEW → PRODUCTION_READY)
         ↓
ModelRegistry.register()
```

---

## Key Design Principles

### 1. FAIL CLOSED
Every gate/check defaults to BLOCKED/REJECTED. Must explicitly pass.

### 2. TEMPORAL BOUNDARIES ENFORCED
- Features only use data from years < prediction_year
- Features only use rounds < prediction_round within prediction_year
- Expanding window for historical statistics (never includes prediction year)

### 3. NO TARGET READY
Per target-definition-phase4.md: `NO_TARGET_READY` until:
- MCC 2021-2024 allotments ingested
- ≥1 state historical allotments ingested
- ≥4 years for temporal validation

### 4. DETERMINISTIC IDENTITY
Dataset version = SHA256(source_file_ids + transformation_version + feature_version + quality_gate_version)[:16]
Same inputs → Same identity.

### 5. FULL PROVENANCE
Every record carries: source_file_id, checksum, URL, parser/adapter/transformation/feature/quality versions, timestamps.

### 6. ABSTENTION OVER PREDICTION
When uncertainty too high → ABSTAIN. Never force a prediction.

---

## Configuration

Reads from `config/modelling_readiness.yaml`:
- Verified modelling-ready years per authority
- Target readiness status
- Temporal validation status
- Minimum years for temporal validation (default 3)

---

## Testing

Run all modelling tests:
```bash
pytest tests/unit/modelling/ -v
```

Run with existing tests:
```bash
pytest tests/unit/modelling/ tests/unit/etl/test_sprint3.6/ tests/unit/etl/test_sprint3.8/ -v
```