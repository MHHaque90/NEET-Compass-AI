# Validation

## Purpose

Validation ensures data quality before it reaches PostgreSQL. Validation occurs at the contract layer, not in the database.

## Validation Modes

### STRICT

- Missing required fields → failure
- Invalid types → failure
- Unknown columns → failure

### COMPATIBLE

- Additional columns may be accepted
- Required fields remain mandatory
- Types remain validated

The mode must be explicit and configurable.

## Validation Rules

### Required Fields

Fields marked as required must be present and non-null.

### Type Validation

Fields must match expected data types: `str`, `int`, `float`, `bool`.

### Range Validation

Numeric fields must fall within specified min/max bounds.

### Enum Validation

Fields must match one of the allowed values.

### Unique Key Validation

Records must be unique based on specified key fields.

## Validation Result

```python
@dataclass
 ValidationResult:
    source_id: str
    dataset: str
    contract_version: str
    effective_year: int
    publication_version: str
    validation_timestamp: str
    status: str  # "passed" or "failed"
    records_checked: int
    records_valid: int
    records_invalid: int
    warnings: list[ValidationError]
    errors: list[ValidationError]
```

## Structured Errors

Each validation error identifies:

- **error_code**: Machine-readable code (e.g., `MISSING_REQUIRED_COLUMN`)
- **source_id**: Source identifier
- **dataset**: Dataset name
- **contract_version**: Contract version
- **field**: Field name (if applicable)
- **row**: Row number (if applicable)
- **received_value**: Value received (where safe)
- **expected**: Expected type/rule
- **message**: Human-readable message

## Error Codes

| Code | Description |
|------|-------------|
| `MISSING_REQUIRED_COLUMN` | Required column not present |
| `UNKNOWN_COLUMN` | Column not in contract (STRICT mode) |
| `INVALID_TYPE` | Value does not match expected type |
| `NULL_NOT_ALLOWED` | Required field is null |
| `OUT_OF_RANGE` | Value outside allowed range |
| `INVALID_ENUM_VALUE` | Value not in allowed set |
| `DUPLICATE_RECORD` | Duplicate record detected |
