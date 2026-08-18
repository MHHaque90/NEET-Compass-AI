# ML Readiness Documentation — Sprint 3.6

This directory contains the machine learning readiness assessment for NEET Compass AI, established in Sprint 3.6.

## Objective

Determine whether NEET Compass AI has enough trustworthy historical data to eventually build a RELIABLE prediction system. The objective is NOT to produce an impressive model. The objective is to establish a scientifically defensible foundation for future modelling.

**Core Principle**: RELIABILITY > MODEL SOPHISTICATION.

## Documents

| Document | Phase | Description |
|----------|-------|-------------|
| [dataset-readiness.md](dataset-readiness.md) | 1-2 | Historical data inventory and readiness classification |
| [target-definition.md](target-definition.md) | 3 | Canonical modelling dataset definition (source facts, derived features, targets, provenance) |
| [target-definition-phase4.md](target-definition-phase4.md) | 4 | Target analysis and first modelling target selection |
| [leakage-policy.md](leakage-policy.md) | 5 | Temporal leakage policy (permanent project rule) |
| [temporal-validation.md](temporal-validation.md) | 6 | Chronological evaluation strategy |
| [baseline-strategy.md](baseline-strategy.md) | 7 | Non-ML baselines that future ML must beat |
| [evaluation-metrics.md](evaluation-metrics.md) | 8 | Reliability metrics (MAE, calibration, subgroup analysis) |
| [uncertainty-abstention.md](uncertainty-abstention.md) | 9 | Uncertainty quantification and abstention policy |
| [data-quality-gates.md](data-quality-gates.md) | 10 | Objective gates before data enters modelling |
| [dataset-versioning.md](dataset-versioning.md) | 11 | Reproducible dataset identity via existing provenance |
| [reliability-gates.md](reliability-gates.md) | 12 | Model lifecycle gates (RESEARCH_ONLY → PRODUCTION_READY) |

## Machine-Readable Registry

- `config/modelling_readiness.yaml` — Queryable readiness metadata

## Key Finding

**NO TARGET READY FOR MODELLING.**

Evidence-based assessment:
- Only MCC 2025 has READY data (seat matrix + allotments)
- All three states (Maharashtra, Karnataka, UP) only have 2026 test fixtures
- Zero historical data (2021-2025) for any state
- UP mappings are explicitly placeholders
- Minimum 3 years needed for temporal validation; only 1 year exists

The architecture is READY (Sprint 3.5 certified). The DATA is NOT.

## Next Steps (Sprint 3.7 Prerequisites)

Before any ML implementation:
1. Ingest MCC 2021-2024 allotments (seat matrix + allotments)
2. Ingest at least one state's historical allotments (2021-2025)
3. Verify UP category/quota mappings against real data
4. Implement vacancy canonical model + ingestion
5. Achieve minimum 4 consecutive years for temporal validation

## Constraints Respected

- No ML model trained or deployed
- No prediction API created
- No frontend prediction features
- No fifth state added
- No database redesign
- Migrations 0001/0002 untouched
- No secrets or restricted data committed