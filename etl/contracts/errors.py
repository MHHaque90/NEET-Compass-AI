"""Structured errors for contract validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ErrorCode(Enum):
    """Error codes for contract validation."""

    MISSING_REQUIRED_COLUMN = "MISSING_REQUIRED_COLUMN"
    UNKNOWN_COLUMN = "UNKNOWN_COLUMN"
    INVALID_TYPE = "INVALID_TYPE"
    NULL_NOT_ALLOWED = "NULL_NOT_ALLOWED"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    INVALID_ENUM_VALUE = "INVALID_ENUM_VALUE"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    REFERENTIAL_INTEGRITY = "REFERENTIAL_INTEGRITY"
    INVALID_VERSION = "INVALID_VERSION"
    CONTRACT_NOT_FOUND = "CONTRACT_NOT_FOUND"
    INCOMPATIBLE_VERSION = "INCOMPATIBLE_VERSION"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"
    INVALID_FIELD_MAPPING = "INVALID_FIELD_MAPPING"


class ValidationErrorSeverity(Enum):
    """Severity levels for validation errors."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class ValidationError:
    """A single validation error."""

    error_code: ErrorCode
    source_id: str
    dataset: str
    contract_version: str
    field: str | None = None
    row: int | None = None
    received_value: str | None = None
    expected: str | None = None
    message: str = ""
    severity: ValidationErrorSeverity = ValidationErrorSeverity.ERROR

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        result: dict[str, object] = {
            "error_code": self.error_code.value,
            "source_id": self.source_id,
            "dataset": self.dataset,
            "contract_version": self.contract_version,
            "severity": self.severity.value,
            "message": self.message,
        }
        if self.field is not None:
            result["field"] = self.field
        if self.row is not None:
            result["row"] = self.row
        if self.received_value is not None:
            result["received_value"] = self.received_value
        if self.expected is not None:
            result["expected"] = self.expected
        return result


@dataclass
class ValidationResult:
    """Structured validation result."""

    source_id: str
    dataset: str
    contract_version: str
    effective_year: int
    publication_version: str
    validation_timestamp: str
    status: str = "pending"
    records_checked: int = 0
    records_valid: int = 0
    records_invalid: int = 0
    warnings: list[ValidationError] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    def add_error(self, error: ValidationError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.status = "failed"

    def add_warning(self, warning: ValidationError) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "dataset": self.dataset,
            "contract_version": self.contract_version,
            "effective_year": self.effective_year,
            "publication_version": self.publication_version,
            "validation_timestamp": self.validation_timestamp,
            "status": self.status,
            "records_checked": self.records_checked,
            "records_valid": self.records_valid,
            "records_invalid": self.records_invalid,
            "warnings": [w.to_dict() for w in self.warnings],
            "errors": [e.to_dict() for e in self.errors],
        }


@dataclass(frozen=True)
class ContractError(Exception):
    """Base error for contract operations."""

    source_id: str
    dataset: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "dataset": self.dataset,
            "message": self.message,
        }


@dataclass(frozen=True)
class ContractNotFoundError(ContractError):
    """Raised when a contract is not found in the registry."""

    version: str = ""

    def __init__(self, source_id: str, dataset: str, version: str = "") -> None:
        msg = f"Contract not found: {source_id}/{dataset}"
        if version:
            msg += f" v{version}"
        super().__init__(source_id=source_id, dataset=dataset, message=msg)


@dataclass(frozen=True)
class IncompatibleVersionError(ContractError):
    """Raised when contract versions are incompatible."""

    required: str = ""
    provided: str = ""

    def __init__(self, source_id: str, dataset: str, required: str, provided: str) -> None:
        msg = f"Incompatible version: required {required}, provided {provided}"
        super().__init__(source_id=source_id, dataset=dataset, message=msg)


@dataclass(frozen=True)
class InvalidVersionFormatError(ContractError):
    """Raised when a version string is invalid."""

    def __init__(self, source_id: str, dataset: str, version: str) -> None:
        msg = f"Invalid version format: {version}"
        super().__init__(source_id=source_id, dataset=dataset, message=msg)
