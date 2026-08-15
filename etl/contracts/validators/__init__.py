"""Validation system for data contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from etl.contracts.base import SourceContract
from etl.contracts.errors import (
    ErrorCode,
    ValidationError,
    ValidationResult,
)


class ValidationMode(Enum):
    """Validation modes."""

    STRICT = "strict"
    COMPATIBLE = "compatible"


@dataclass
class ContractValidator:
    """Validates data against a source contract.

    Supports STRICT and COMPATIBLE modes:
    - STRICT: Missing required, invalid types, unknown columns → failure
    - COMPATIBLE: Additional columns accepted, required still mandatory
    """

    contract: SourceContract
    mode: ValidationMode = ValidationMode.STRICT

    def validate_columns(
        self,
        columns: list[str],
        source_id: str,
        dataset: str,
    ) -> list[ValidationError]:
        """Validate column structure against contract."""
        errors: list[ValidationError] = []
        contract_version = str(self.contract.contract_version)

        canonical_columns = set()
        for mapping in self.contract.field_mapping:
            canonical_columns.add(mapping.external_name)

        external_to_canonical: dict[str, str] = {}
        for mapping in self.contract.field_mapping:
            external_to_canonical[mapping.external_name] = mapping.canonical_name

        for col in self.contract.required_columns:
            found = False
            if col in columns or col in canonical_columns:
                found = True
            else:
                for ext, canon in external_to_canonical.items():
                    if canon == col and ext in columns:
                        found = True
                        break

            if not found:
                errors.append(
                    ValidationError(
                        error_code=ErrorCode.MISSING_REQUIRED_COLUMN,
                        source_id=source_id,
                        dataset=dataset,
                        contract_version=contract_version,
                        field=col,
                        message=f"Required column missing: {col}",
                    )
                )

        if self.mode == ValidationMode.STRICT:
            for col in columns:
                is_expected = False
                if (
                    col in self.contract.required_columns
                    or col in self.contract.optional_columns
                    or col in canonical_columns
                ):
                    is_expected = True
                else:
                    for ext, canon in external_to_canonical.items():
                        if canon == col or ext == col:
                            is_expected = True
                            break

                if not is_expected:
                    errors.append(
                        ValidationError(
                            error_code=ErrorCode.UNKNOWN_COLUMN,
                            source_id=source_id,
                            dataset=dataset,
                            contract_version=contract_version,
                            field=col,
                            message=f"Unknown column: {col}",
                        )
                    )

        return errors

    def validate_row(
        self,
        row: dict[str, Any],
        row_number: int,
        source_id: str,
        dataset: str,
    ) -> list[ValidationError]:
        """Validate a single data row against contract rules."""
        errors: list[ValidationError] = []
        contract_version = str(self.contract.contract_version)

        for rule in self.contract.validation_rules:
            field_value = row.get(rule.field_name)

            if rule.rule_type == "required":
                if field_value is None or (
                    isinstance(field_value, str) and not field_value.strip()
                ):
                    errors.append(
                        ValidationError(
                            error_code=ErrorCode.NULL_NOT_ALLOWED,
                            source_id=source_id,
                            dataset=dataset,
                            contract_version=contract_version,
                            field=rule.field_name,
                            row=row_number,
                            message=rule.message or f"Required field is empty: {rule.field_name}",
                        )
                    )

            elif rule.rule_type == "type":
                expected_type = rule.params.get("type", "str")
                if field_value is not None and not self._check_type(
                    field_value, str(expected_type)
                ):
                    errors.append(
                        ValidationError(
                            error_code=ErrorCode.INVALID_TYPE,
                            source_id=source_id,
                            dataset=dataset,
                            contract_version=contract_version,
                            field=rule.field_name,
                            row=row_number,
                            received_value=str(field_value)[:100],
                            expected=f"type:{expected_type}",
                            message=rule.message or f"Invalid type for {rule.field_name}",
                        )
                    )
            elif rule.rule_type == "range":
                if field_value is not None:
                    min_val = rule.params.get("min")
                    max_val = rule.params.get("max")
                    try:
                        num_val = float(field_value)
                        if min_val is not None and num_val < float(str(min_val)):
                            errors.append(
                                ValidationError(
                                    error_code=ErrorCode.OUT_OF_RANGE,
                                    source_id=source_id,
                                    dataset=dataset,
                                    contract_version=contract_version,
                                    field=rule.field_name,
                                    row=row_number,
                                    received_value=str(field_value),
                                    expected=f"range:[{min_val},{max_val}]",
                                    message=rule.message
                                    or f"Value below minimum: {rule.field_name}",
                                )
                            )
                        if max_val is not None and num_val > float(str(max_val)):
                            errors.append(
                                ValidationError(
                                    error_code=ErrorCode.OUT_OF_RANGE,
                                    source_id=source_id,
                                    dataset=dataset,
                                    contract_version=contract_version,
                                    field=rule.field_name,
                                    row=row_number,
                                    received_value=str(field_value),
                                    expected=f"range:[{min_val},{max_val}]",
                                    message=rule.message
                                    or f"Value above maximum: {rule.field_name}",
                                )
                            )
                    except (ValueError, TypeError):
                        errors.append(
                            ValidationError(
                                error_code=ErrorCode.INVALID_TYPE,
                                source_id=source_id,
                                dataset=dataset,
                                contract_version=contract_version,
                                field=rule.field_name,
                                row=row_number,
                                received_value=str(field_value)[:100],
                                expected=f"numeric in range [{min_val},{max_val}]",
                                message=rule.message or f"Non-numeric value: {rule.field_name}",
                            )
                        )

            elif rule.rule_type == "enum":
                allowed_raw = rule.params.get("values")
                if allowed_raw is None:
                    allowed_list: list[str] = []
                elif isinstance(allowed_raw, list):
                    allowed_list = [str(v) for v in allowed_raw]
                else:
                    allowed_list = [str(allowed_raw)]
                if field_value is not None and str(field_value) not in allowed_list:
                    errors.append(
                        ValidationError(
                            error_code=ErrorCode.INVALID_ENUM_VALUE,
                            source_id=source_id,
                            dataset=dataset,
                            contract_version=contract_version,
                            field=rule.field_name,
                            row=row_number,
                            received_value=str(field_value)[:100],
                            expected=f"enum:{allowed_list}",
                            message=rule.message or f"Invalid value for {rule.field_name}",
                        )
                    )

        return errors

    def validate_records(
        self,
        records: list[dict[str, Any]],
        source_id: str,
        dataset: str,
        effective_year: int,
        publication_version: str,
    ) -> ValidationResult:
        """Validate a complete set of records."""
        result = ValidationResult(
            source_id=source_id,
            dataset=dataset,
            contract_version=str(self.contract.contract_version),
            effective_year=effective_year,
            publication_version=publication_version,
            validation_timestamp=datetime.now(UTC).isoformat(),
            status="passed",
        )

        result.records_checked = len(records)
        seen_keys: set[tuple[Any, ...]] = set()

        for i, record in enumerate(records, start=1):
            row_errors = self.validate_row(record, i, source_id, dataset)

            unique_key_fields = [
                f for f in self.contract.validation_rules if f.rule_type == "unique_key"
            ]
            if unique_key_fields:
                key_values = tuple(record.get(f.field_name) for f in unique_key_fields)
                if key_values in seen_keys:
                    row_errors.append(
                        ValidationError(
                            error_code=ErrorCode.DUPLICATE_RECORD,
                            source_id=source_id,
                            dataset=dataset,
                            contract_version=str(self.contract.contract_version),
                            row=i,
                            message=f"Duplicate record at row {i}",
                        )
                    )
                else:
                    seen_keys.add(key_values)

            if row_errors:
                result.records_invalid += 1
                for error in row_errors:
                    result.add_error(error)
            else:
                result.records_valid += 1

        return result

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if a value matches the expected type."""
        if expected_type == "str":
            return isinstance(value, str)
        elif expected_type == "int":
            try:
                int(value)
                return True
            except (ValueError, TypeError):
                return False
        elif expected_type == "float":
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        elif expected_type == "bool":
            return isinstance(value, bool) or str(value).lower() in (
                "true",
                "false",
                "0",
                "1",
            )
        return True
