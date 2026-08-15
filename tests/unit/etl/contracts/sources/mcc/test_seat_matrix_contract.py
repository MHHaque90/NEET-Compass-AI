"""Tests for the MCC seat-matrix source contract."""

from __future__ import annotations

from etl.contracts.base import SourceContract
from etl.contracts.sources.mcc.contracts import (
    SEAT_MATRIX_COLUMNS,
    seat_matrix_2025_contract,
)


def test_contract_identity() -> None:
    contract = seat_matrix_2025_contract()
    assert contract.source_id == "mcc"
    assert contract.dataset == "seat_matrix"
    assert contract.effective_year == 2025
    assert str(contract.contract_version) == "1.1.0"
    assert contract.required_columns == SEAT_MATRIX_COLUMNS


def test_field_mappings_resolve_canonical_names() -> None:
    contract = seat_matrix_2025_contract()
    assert contract.get_canonical_name("Institute") == "college_name"
    assert contract.get_canonical_name("TotalSeats") == "total_seats"
    assert contract.get_canonical_name("Branch") == "course_id"
    assert contract.get_external_name("quota_id") == "Quota"


def test_contract_supports_csv_format() -> None:
    contract = seat_matrix_2025_contract()
    assert contract.supports_format("csv")
    assert contract.supports_format("table")


def test_validation_rules_cover_composite_key_and_enums() -> None:
    contract = seat_matrix_2025_contract()
    unique_keys = [
        rule for rule in contract.validation_rules if rule.rule_type == "unique_key"
    ]
    assert sorted(rule.field_name for rule in unique_keys) == sorted(
        ["college_id", "course_id", "quota_id", "category_id", "effective_year"]
    )
    enums = {
        rule.field_name: rule.params["values"]
        for rule in contract.validation_rules
        if rule.rule_type == "enum"
    }
    assert isinstance(enums, dict)
    category_values = enums["category_id"]
    assert isinstance(category_values, list)
    assert {"bc", "gn", "sc", "st", "st_pwd", "gn_pwd", "bc_pwd"} <= set(category_values)
    quota_values = enums["quota_id"]
    assert isinstance(quota_values, list)
    assert {"ai", "so"} <= set(quota_values)
    range_rule = next(
        rule
        for rule in contract.validation_rules
        if rule.field_name == "total_seats" and rule.rule_type == "range"
    )
    assert range_rule.params["min"] == 0
    assert range_rule.params["max"] == 2000


def test_contract_is_registerable() -> None:
    from etl.contracts.registry import ContractRegistry

    registry: ContractRegistry = ContractRegistry()
    registry.register(seat_matrix_2025_contract())
    fetched = registry.get_contract("mcc", "seat_matrix")
    assert isinstance(fetched, SourceContract)
    assert fetched.dataset == "seat_matrix"
