"""Tests for Contract Compatibility — Sprint 4.1.

Critical assertions:
- UNKNOWN contract compatibility -> NOT_READY
- INCOMPATIBLE contract -> NOT_READY (no forced adapters)
- COMPATIBLE_WITH_LIMITATIONS -> READY_WITH_LIMITATIONS
- COMPATIBLE + format verified -> READY
"""

import pytest
from etl.contracts.historical.contract_gate import (
    ContractCompatibility,
    ContractGate,
    ContractGateResult,
    validate_contract_compatibility,
    CONTRACT_COMPATIBILITY_VALUES,
)


class TestContractCompatibility:
    """Test contract compatibility classification."""

    def test_compatibility_values_defined(self):
        """All four compatibility values should exist."""
        assert ContractCompatibility.COMPATIBLE in CONTRACT_COMPATIBILITY_VALUES
        assert ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS in CONTRACT_COMPATIBILITY_VALUES
        assert ContractCompatibility.INCOMPATIBLE in CONTRACT_COMPATIBILITY_VALUES
        assert ContractCompatibility.UNKNOWN in CONTRACT_COMPATIBILITY_VALUES
        assert len(CONTRACT_COMPATIBILITY_VALUES) == 4

    def test_unknown_compatibility_not_ready(self):
        """UNKNOWN compatibility must not be modelling-ready."""
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.UNKNOWN, format_verified=False)
        assert result.passed is False
        assert result.compatibility == ContractCompatibility.UNKNOWN
        assert "UNKNOWN" in result.details.get("reason", "")

    def test_incompatible_contract_not_ready(self):
        """INCOMPATIBLE must not be forced through adapter."""
        gate = ContractGate()
        result = gate.validate(ContractCompatibility.INCOMPATIBLE, format_verified=True)
        assert result.passed is False
        assert result.compatibility == ContractCompatibility.INCOMPATIBLE
        assert "INCOMPATIBLE" in result.details.get("reason", "")

    def test_compatible_with_limitations_ready_with_limitations(self):
        """COMPATIBLE_WITH_LIMITATIONS -> READY_WITH_LIMITATIONS."""
        gate = ContractGate()
        result = gate.validate(
            ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS,
            format_verified=True,
            limitations=["Column X differs from v1.1.0"],
        )
        assert result.passed is True
        assert result.compatibility == ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS

    def test_compatible_requires_format_verified(self):
        """COMPATIBLE requires format_verified=True to pass."""
        gate = ContractGate(require_verified_format=True)
        # Without format verification
        result = gate.validate(ContractCompatibility.COMPATIBLE, format_verified=False)
        assert result.passed is False
        assert "Format not verified" in result.details.get("reason", "")

        # With format verification
        result = gate.validate(ContractCompatibility.COMPATIBLE, format_verified=True)
        assert result.passed is True

    def test_compatible_without_require_verified_format(self):
        """If require_verified_format=False, COMPATIBLE passes without format check."""
        gate = ContractGate(require_verified_format=False)
        result = gate.validate(ContractCompatibility.COMPATIBLE, format_verified=False)
        assert result.passed is True

    def test_allow_unknown_for_legacy(self):
        """Legacy allowance for UNKNOWN still not READY."""
        gate = ContractGate(allow_unknown_for_legacy=True)
        result = gate.validate(ContractCompatibility.UNKNOWN, format_verified=False)
        assert result.passed is False  # Still not READY
        assert "legacy allowance" in result.details.get("reason", "").lower()

    def test_convenience_function(self):
        """validate_contract_compatibility convenience function."""
        result = validate_contract_compatibility(
            "COMPATIBLE", format_verified=True, limitations=["test"]
        )
        assert isinstance(result, ContractGateResult)
        assert result.passed is True

    def test_string_input_conversion(self):
        """String input should be converted to enum."""
        gate = ContractGate()
        result = gate.validate("COMPATIBLE", format_verified=True)
        assert result.compatibility == ContractCompatibility.COMPATIBLE

    def test_invalid_string_becomes_unknown(self):
        """Invalid string compatibility becomes UNKNOWN."""
        gate = ContractGate()
        result = gate.validate("INVALID_STRING", format_verified=True)
        assert result.compatibility == ContractCompatibility.UNKNOWN
        assert result.passed is False

    def test_limitations_warning_for_compatible_with_limitations(self):
        """Should warn if COMPATIBLE_WITH_LIMITATIONS has no documented limitations."""
        gate = ContractGate()
        result = gate.validate(
            ContractCompatibility.COMPATIBLE_WITH_LIMITATIONS,
            format_verified=True,
            limitations=[],
        )
        assert result.passed is True
        assert "warning" in result.details
        assert "No limitations documented" in result.details["warning"]


class TestContractResult:
    """Test ContractGateResult structure."""

    def test_result_boolean_conversion(self):
        """ContractGateResult converts to bool based on passed."""
        result_pass = ContractGateResult(
            compatibility=ContractCompatibility.COMPATIBLE, passed=True, details={}
        )
        result_fail = ContractGateResult(
            compatibility=ContractCompatibility.UNKNOWN, passed=False, details={}
        )
        assert bool(result_pass) is True
        assert bool(result_fail) is False