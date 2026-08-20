"""Contract Compatibility Gate — Sprint 3.9.

Formalizes historical contract compatibility classification.
A dataset must be classified as:
- COMPATIBLE
- COMPATIBLE_WITH_LIMITATIONS
- INCOMPATIBLE
- UNKNOWN

UNKNOWN MUST NOT become modelling-ready.
INCOMPATIBLE MUST NOT be forced through an adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ContractCompatibility(str, Enum):
    """Contract compatibility classification."""

    COMPATIBLE = "COMPATIBLE"
    COMPATIBLE_WITH_LIMITATIONS = "COMPATIBLE_WITH_LIMITATIONS"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


CONTRACT_COMPATIBILITY_VALUES: tuple[ContractCompatibility, ...] = (
    ContractCompatibility.COMPATIBLE,
    ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS,
    ContractCompatibility.INCOMPATIBLE,
    ContractCompatibility.UNKNOWN,
)


@dataclass(frozen=True)
class ContractGateResult:
    """Result of contract compatibility validation."""

    compatibility: ContractCompatibility
    passed: bool
    details: dict[str, Any]

    def __bool__(self) -> bool:
        return self.passed


class ContractGate:
    """Validates contract compatibility for historical datasets.

    Rules:
    - UNKNOWN -> NOT_READY (cannot proceed)
    - INCOMPATIBLE -> NOT_READY (must not force through adapter)
    - COMPATIBLE_WITH_LIMITATIONS -> READY_WITH_LIMITATIONS
    - COMPATIBLE -> READY (if all other gates pass)
    """

    def __init__(
        self,
        require_verified_format: bool = True,
        allow_unknown_for_legacy: bool = False,
    ):
        self.require_verified_format = require_verified_format
        self.allow_unknown_for_legacy = allow_unknown_for_legacy

    def validate(
        self,
        compatibility: ContractCompatibility | str,
        format_verified: bool = False,
        limitations: list[str] | None = None,
    ) -> ContractGateResult:
        """Validate contract compatibility.

        Args:
            compatibility: Compatibility classification.
            format_verified: Whether format was verified against actual source.
            limitations: Known limitations.

        Returns:
            ContractGateResult.

        """
        if isinstance(compatibility, str):
            try:
                compat = ContractCompatibility(compatibility)
            except ValueError:
                compat = ContractCompatibility.UNKNOWN
        else:
            compat = compatibility

        passed = True
        details = {
            "compatibility": compat.value,
            "format_verified": format_verified,
            "limitations": limitations or [],
        }

        if compat == ContractCompatibility.UNKNOWN:
            if self.allow_unknown_for_legacy:
                passed = False  # Still not READY
                details["reason"] = "Contract compatibility UNKNOWN - legacy allowance but not modelling-ready"
            else:
                passed = False
                details["reason"] = "Contract compatibility UNKNOWN - cannot proceed without verification"

        elif compat == ContractCompatibility.INCOMPATIBLE:
            passed = False
            details["reason"] = "Contract INCOMPATIBLE - cannot force through adapter"

        elif compat == ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS:
            passed = True  # But only READY_WITH_LIMITATIONS
            details["reason"] = "Contract compatible with documented limitations"
            if not limitations:
                details["warning"] = "No limitations documented for COMPATIBLE_WITH_LIMITATIONS"

        elif compat == ContractCompatibility.COMPATIBLE:
            if self.require_verified_format and not format_verified:
                passed = False
                details["reason"] = "Format not verified - cannot confirm COMPATIBLE without source evidence"
            else:
                passed = True
                details["reason"] = "Contract COMPATIBLE and format verified"

        return ContractGateResult(
            compatibility=compat,
            passed=passed,
            details=details,
        )


def validate_contract_compatibility(
    compatibility: ContractCompatibility | str,
    format_verified: bool = False,
    limitations: list[str] | None = None,
    require_verified_format: bool = True,
) -> ContractGateResult:
    """Convenience function to validate contract compatibility."""
    gate = ContractGate(require_verified_format=require_verified_format)
    return gate.validate(compatibility, format_verified, limitations)
