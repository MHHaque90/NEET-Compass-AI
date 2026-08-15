# Compatibility

## Contract Compatibility

Contracts are compatible when:

1. Same MAJOR version
2. MINOR version meets or exceeds requirement

## Backward Compatibility

A new contract version is backward compatible if:

- Existing code can process data conforming to the new contract
- No required fields were removed
- No field types were changed
- No validation rules were made stricter

## Forward Compatibility

A contract is forward compatible if:

- New code can process data from older contract versions
- New fields are optional
- New validation rules only apply to new fields

## Migration Strategy

When a breaking change is required:

1. Bump MAJOR version
2. Create new contract version
3. Register both versions in registry
4. Update adapters to handle new format
5. Deprecate old version (but keep registered)

## Version Negotiation

The registry supports version negotiation:

```python
# Get any compatible version
contract = registry.get_compatible_contract(
    source_id="mcc",
    dataset="allotments",
    required_version=ContractVersion(1, 0, 0)
)
```

This returns the latest version compatible with the required version.

## Unknown Contracts

Unknown contracts MUST fail explicitly. Do not silently fall back to another contract version.
