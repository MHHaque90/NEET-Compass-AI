# Data Contracts Overview

Sprint 2.5 — External Data Contracts & Source Compatibility Layer

## Purpose

Data contracts isolate external counselling sources from the internal system. External sources may change PDF structure, Excel headers, CSV headers, column names, category labels, quota names, round names, course names, college names, file formats, and publication versions. These changes MUST NOT require changes to domain models, database architecture, prediction engine, or application services.

## Architecture

```
External Source
      ↓
Source Adapter
      ↓
Data Contract
      ↓
Contract Validation
      ↓
Canonical Data Model
      ↓
Existing ETL Infrastructure
      ↓
PostgreSQL
```

The external source format MUST NEVER become the internal canonical schema.

## Key Components

- **SourceContract**: Defines expected structure from an external source
- **ContractRegistry**: Registration and lookup of contracts
- **ContractValidator**: Validates data against contracts (STRICT/COMPATIBLE modes)
- **SourceAdapter**: Transforms external data to canonical format
- **Canonical Models**: Source-independent data representations

## Directory Structure

```
etl/contracts/
    __init__.py
    base.py          # SourceContract, FieldMapping, ValidationRule
    version.py       # ContractVersion (semantic versioning)
    registry.py      # ContractRegistry
    errors.py        # ValidationError, ValidationResult, ContractError
    models/
        __init__.py
    sources/
        __init__.py  # Sprint 3 will implement actual adapters
    canonical/
        __init__.py  # Canonical models (College, Course, etc.)
        checksum.py  # SHA-256 file identity
    validators/
        __init__.py  # ContractValidator
    adapters/
        __init__.py  # SourceAdapter interface
```

## See Also

- [Contract Versioning](contract-versioning.md)
- [Source Adapters](source-adapters.md)
- [Canonical Schema](canonical-schema.md)
- [Validation](validation.md)
- [Compatibility](compatibility.md)
