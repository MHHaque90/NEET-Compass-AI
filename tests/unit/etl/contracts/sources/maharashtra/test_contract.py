"""Tests for the Maharashtra state source contract."""

from __future__ import annotations

from etl.contracts.base import SourceContract
from etl.contracts.sources.maharashtra.contracts import (
    SEAT_MATRIX_COLUMNS,
    allotments_2026_contract,
    seat_matrix_2026_contract,
)


def test_contract_identity_seat_matrix() -> None:
    contract = seat_matrix_2026_contract()
    assert contract.source_id == "mcc_state_maharashtra"
    assert contract.dataset == "seat_matrix"
    assert contract.effective_year == 2026
    assert str(contract.contract_version) == "1.0.0"
    assert contract.required_columns == SEAT_MATRIX_COLUMNS


def test_contract_identity_allotments() -> None:
    contract = allotments_2026_contract()
    assert contract.source_id == "mcc_state_maharashtra"
    assert contract.dataset == "allotments"
    assert contract.effective_year == 2026
    assert str(contract.contract_version) == "1.0.0"
    assert contract.required_columns is not None


def test_field_mappings_resolve_canonical_names() -> None:
    contract = seat_matrix_2026_contract()
    assert contract.get_canonical_name("Institute") == "college_name"
    assert contract.get_canonical_name("TotalSeats") == "total_seats"
    assert contract.get_external_name("quota_id") == "Quota"
    assert contract.get_external_name("category_id") == "Category"


def test_contract_supports_csv_format() -> None:
    contract = seat_matrix_2026_contract()
    assert contract.supports_format("csv")
    assert contract.supports_format("table")


def test_validation_rules_cover_composite_key_and_enums() -> None:
    contract = seat_matrix_2026_contract()
    unique_keys = [
        rule for rule in contract.validation_rules if rule.rule_type == "unique_key"
    ]
    assert sorted(rule.field_name for rule in unique_keys) == sorted(
        ["college_id", "course_id", "quota_id", "category_id", "effective_year"]
    )


def test_contract_is_registerable() -> None:
    from etl.contracts.registry import ContractRegistry

    registry: ContractRegistry = ContractRegistry()
    registry.register(seat_matrix_2026_contract())
    fetched = registry.get_contract("mcc_state_maharashtra", "seat_matrix")
    assert isinstance(fetched, SourceContract)
    assert fetched.dataset == "seat_matrix"
