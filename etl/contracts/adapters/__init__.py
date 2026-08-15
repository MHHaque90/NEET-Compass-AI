"""Adapter boundary interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from etl.contracts.base import SourceContract
from etl.contracts.canonical import SourceMetadata


@dataclass
class AdapterResult:
    """Result of adapter transformation."""

    records: list[dict[str, Any]]
    metadata: SourceMetadata
    records_transformed: int = 0
    records_skipped: int = 0


class SourceAdapter(ABC):
    """Base adapter interface for transforming external data.

    Adapters must:
    - Transform external representation to canonical
    - NOT write directly to PostgreSQL
    - NOT contain domain business logic
    - NOT contain prediction logic
    """

    @abstractmethod
    def transform(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
        metadata: SourceMetadata,
    ) -> AdapterResult:
        """Transform external data to canonical format.

        Args:
            raw_data: Raw records from external source
            contract: Source contract defining expected structure
            metadata: Source metadata for provenance

        Returns:
            AdapterResult with transformed records

        """
        ...

    @abstractmethod
    def validate_source(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
    ) -> list[str]:
        """Validate that source data can be transformed.

        Returns:
            List of validation error messages (empty if valid)

        """
        ...


class IdentityAdapter(SourceAdapter):
    """Pass-through adapter for already-canonical data."""

    def transform(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
        metadata: SourceMetadata,
    ) -> AdapterResult:
        """Transform by passing data through unchanged."""
        return AdapterResult(
            records=raw_data,
            metadata=metadata,
            records_transformed=len(raw_data),
            records_skipped=0,
        )

    def validate_source(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
    ) -> list[str]:
        """Validate source data is not empty."""
        errors: list[str] = []
        if not raw_data:
            errors.append("Source data is empty")
        return errors


class ColumnMappingAdapter(SourceAdapter):
    """Adapter that maps external column names to canonical names."""

    def transform(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
        metadata: SourceMetadata,
    ) -> AdapterResult:
        """Transform by mapping columns according to contract."""
        transformed: list[dict[str, Any]] = []

        for row in raw_data:
            mapped_row: dict[str, Any] = {}
            for external_name, value in row.items():
                canonical_name = contract.get_canonical_name(external_name)
                target_name = canonical_name if canonical_name else external_name
                mapped_row[target_name] = value
            transformed.append(mapped_row)

        return AdapterResult(
            records=transformed,
            metadata=metadata,
            records_transformed=len(transformed),
            records_skipped=0,
        )

    def validate_source(
        self,
        raw_data: list[dict[str, Any]],
        contract: SourceContract,
    ) -> list[str]:
        """Validate source data has required columns."""
        errors: list[str] = []
        if not raw_data:
            errors.append("Source data is empty")
            return errors

        first_row = raw_data[0]
        return [
            f"Expected column not found: {m.external_name}"
            for m in contract.field_mapping
            if m.external_name not in first_row
        ]
