"""Tests for the MCC allotments source contract (PII-boundary checks)."""

from __future__ import annotations

from etl.contracts.sources.mcc.contracts import (
    ALLOTMENT_COLUMNS,
    ALLOTMENT_PRIVACY_BLOCKLIST,
    allotments_2025_contract,
)


def test_contract_identity() -> None:
    contract = allotments_2025_contract()
    assert contract.source_id == "mcc"
    assert contract.dataset == "allotments"
    assert contract.effective_year == 2025
    assert str(contract.contract_version) == "1.1.0"
    assert contract.required_columns == ALLOTMENT_COLUMNS


def test_field_mappings_resolve_canonical_names() -> None:
    contract = allotments_2025_contract()
    assert contract.get_canonical_name("Institute Code") == "college_id"
    assert contract.get_canonical_name("Rank") == "rank"
    assert contract.get_canonical_name("Seats") == "seat_count"


def test_contract_declared_columns_exclude_pii() -> None:
    """The contract must never promise to read candidate PII columns."""
    contract = allotments_2025_contract()
    declared = set(contract.expected_columns) | set(contract.required_columns)
    leaked = declared & ALLOTMENT_PRIVACY_BLOCKLIST
    assert leaked == set()
    # Sanity: these are the PII fields MCC does publish in human reports.
    assert {"Candidate Name", "Percentile", "Contact No"} <= ALLOTMENT_PRIVACY_BLOCKLIST


def test_allotment_unique_key_is_six_fields() -> None:
    contract = allotments_2025_contract()
    unique_fields = sorted(
        rule.field_name
        for rule in contract.validation_rules
        if rule.rule_type == "unique_key"
    )
    assert unique_fields == sorted(
        ["college_id", "course_id", "quota_id", "category_id", "round_id", "rank"]
    )


def test_rank_and_seat_count_ranges() -> None:
    contract = allotments_2025_contract()
    by_field = {
        (rule.field_name, rule.rule_type): rule for rule in contract.validation_rules
    }
    assert by_field[("rank", "range")].params["min"] == 1
    assert by_field[("rank", "range")].params["max"] == 900000
    assert by_field[("seat_count", "range")].params["min"] == 1
    assert by_field[("seat_count", "range")].params["max"] == 3
