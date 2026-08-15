# Contract Versioning

## Semantic Versioning

Contracts use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking contract change (columns removed, types changed)
- **MINOR**: Backward-compatible extension (new optional columns)
- **PATCH**: Non-breaking correction (description updates)

## Compatibility Rules

A contract version `X.Y.Z` is compatible with required version `A.B.C` if:

1. `X == A` (same major version)
2. `Y >= B` (minor version meets or exceeds requirement)

PATCH version is ignored for compatibility.

## Examples

| Contract | Required | Compatible? |
|----------|----------|-------------|
| 1.0.0 | 1.0.0 | Yes |
| 1.2.0 | 1.0.0 | Yes |
| 1.0.0 | 1.2.0 | No |
| 2.0.0 | 1.0.0 | No |

## Version Independence

Contract versions are independent from application versions. A contract at version `1.0.0` can work with application versions `0.2.5`, `0.3.0`, etc.

## Breaking Changes

Examples of breaking changes (MAJOR bump):

- Removing a required column
- Changing a column's data type
- Renaming a column
- Changing validation rules to be stricter

## Non-Breaking Changes

Examples of non-breaking changes (MINOR bump):

- Adding an optional column
- Adding new validation rules for optional fields
- Extending allowed enum values

## Patch Changes

Examples of patch changes:

- Fixing documentation
- Correcting description text
- Updating metadata fields
