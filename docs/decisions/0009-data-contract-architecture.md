# ADR-009: Data Contract Architecture

## Status

Accepted

## Date

2026-08-12

## Context

NEET Compass AI ingests data from multiple counselling sources (MCC, NMC, state authorities). These sources publish data in varying formats (PDF, Excel, CSV) with inconsistent column naming, category labels, and structure. External sources may change their format at any time.

The system must isolate external source formats from the internal canonical schema. Changes to external sources MUST NOT require changes to domain models, database architecture, prediction engine, or application services.

## Decision

Implement a Data Contract architecture with:

1. **SourceContract**: Defines expected structure from an external source
2. **ContractRegistry**: Registration and lookup of contracts
3. **ContractValidator**: Validates data against contracts
4. **SourceAdapter**: Transforms external data to canonical format
5. **Canonical Models**: Source-independent data representations

## Rationale

### Alternatives Considered

1. **Direct ingestion**: No contract layer. Rejected because external changes would break the system.

2. **Schema-on-read**: Validate at query time. Rejected because errors would propagate to downstream systems.

3. **Full ETL framework**: Heavyweight solution. Rejected because it adds unnecessary complexity for the current scale.

### Why This Approach

- **Isolation**: External formats never become internal schema
- **Versioning**: Contracts evolve independently from application
- **Validation**: Errors caught before reaching PostgreSQL
- **Extensibility**: New sources added via adapters, not core changes
- **Simplicity**: Minimal abstractions, clear boundaries

## Consequences

### Positive

- External source changes are absorbed by adapters
- Validation errors are structured and actionable
- Contracts are versioned and compatible
- Canonical models remain stable

### Negative

- Additional layer of abstraction
- Contract maintenance overhead
- Adapter development required for new sources

### Mitigations

- Adapter development deferred to Sprint 3
- Contract registry allows multiple versions
- Validation modes (STRICT/COMPATIBLE) provide flexibility

## Versioning Strategy

Semantic versioning: `MAJOR.MINOR.PATCH`

- MAJOR: Breaking contract change
- MINOR: Backward-compatible extension
- PATCH: Non-breaking correction

## Compatibility Strategy

A contract version `X.Y.Z` is compatible with required version `A.B.C` if:

1. `X == A` (same major)
2. `Y >= B` (minor meets requirement)

Unknown contracts MUST fail explicitly.

## Adapter Boundary

Adapters operate at the infrastructure boundary:

- Transform external → canonical
- Do NOT write to PostgreSQL
- Do NOT contain domain logic
- Do NOT contain prediction logic

## Canonical Schema Principle

The external source format MUST NEVER become the internal canonical schema. Canonical fields are source-independent. Source-specific mapping belongs in the contract/adapter layer.

## References

- [Data Contracts Overview](../data-contracts/overview.md)
- [Contract Versioning](../data-contracts/contract-versioning.md)
- [Source Adapters](../data-contracts/source-adapters.md)
- [Canonical Schema](../data-contracts/canonical-schema.md)
- [Validation](../data-contracts/validation.md)
