"""Base source contract definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from etl.contracts.version import ContractVersion


class SourceType(Enum):
    """Types of external data sources."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    HTML = "html"


@dataclass(frozen=True)
class FieldMapping:
    """Maps external column names to canonical field names."""

    external_name: str
    canonical_name: str
    data_type: str = "str"
    nullable: bool = True
    description: str = ""


@dataclass(frozen=True)
class ValidationRule:
    """A validation rule for a field."""

    field_name: str
    rule_type: str  # "type", "range", "enum", "required", "pattern"
    params: dict[str, object] = field(default_factory=dict)
    message: str = ""


@dataclass(frozen=True)
class TransformationRule:
    """A transformation rule applied to data."""

    source_field: str
    target_field: str
    transform_type: str  # "map", "convert", "default", "strip"
    params: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceContract:
    """Contract defining expected structure from an external source.

    Each contract declares:
    - Source identity (source_id, source_name, authority)
    - Dataset identity (dataset, source_type)
    - Versioning (contract_version, effective_year, publication_version)
    - Structure (expected_columns, required/optional)
    - Mapping (field_mapping, validation_rules, transformation_rules)
    """

    source_id: str
    source_name: str
    authority: str
    dataset: str
    source_type: SourceType
    contract_version: ContractVersion
    effective_year: int
    publication_version: str
    supported_formats: tuple[str, ...] = ("csv",)
    expected_columns: tuple[str, ...] = ()
    required_columns: tuple[str, ...] = ()
    optional_columns: tuple[str, ...] = ()
    field_mapping: tuple[FieldMapping, ...] = ()
    validation_rules: tuple[ValidationRule, ...] = ()
    transformation_rules: tuple[TransformationRule, ...] = ()

    def get_canonical_name(self, external_name: str) -> str | None:
        """Look up canonical name for an external column."""
        for mapping in self.field_mapping:
            if mapping.external_name == external_name:
                return mapping.canonical_name
        return None

    def get_external_name(self, canonical_name: str) -> str | None:
        """Look up external name for a canonical field."""
        for mapping in self.field_mapping:
            if mapping.canonical_name == canonical_name:
                return mapping.external_name
        return None

    def is_required_column(self, column_name: str) -> bool:
        """Check if a column is required."""
        return column_name in self.required_columns

    def is_expected_column(self, column_name: str) -> bool:
        """Check if a column is expected (in required or optional)."""
        return column_name in self.required_columns or column_name in self.optional_columns

    def get_validation_rules_for_field(self, field_name: str) -> list[ValidationRule]:
        """Get all validation rules for a specific field."""
        return [rule for rule in self.validation_rules if rule.field_name == field_name]

    def supports_format(self, format_type: str) -> bool:
        """Check if the contract supports a given format."""
        return format_type.lower() in [f.lower() for f in self.supported_formats]
