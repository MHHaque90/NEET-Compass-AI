# Source Adapters

## Purpose

Adapters transform external data representations to canonical format. They operate at the infrastructure boundary.

## Adapter Interface

```python
class SourceAdapter(ABC):
    @abstractmethod
    def transform(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
        metadata: SourceMetadata,
    ) -> AdapterResult:
        """Transform external data to canonical format."""
        ...

    @abstractmethod
    def validate_source(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
    ) -> list[str]:
        """Validate that source data can be transformed."""
        ...
```

## Adapter Rules

Adapters MUST:

- Transform external representation to canonical representation
- Use contract field mappings for column translation
- Preserve source metadata for provenance

Adapters MUST NOT:

- Write directly to PostgreSQL
- Contain domain business logic
- Contain prediction logic

## Built-in Adapters

### IdentityAdapter

Pass-through adapter for already-canonical data. No transformation applied.

### ColumnMappingAdapter

Maps external column names to canonical names using contract field mappings.

## Sprint 3 Sources

Sprint 3 will implement adapters for:

- `mcc` — Medical Counselling Committee
- `nmc` — National Medical Commission
- `state_up` — Uttar Pradesh
- `state_mp` — Madhya Pradesh
- `state_rajasthan` — Rajasthan

These are architecture placeholders only. No live adapters are implemented in Sprint 2.5.
