"""Tests for contract registry."""

from __future__ import annotations

import pytest
from etl.contracts.base import FieldMapping, SourceContract, SourceType
from etl.contracts.errors import ContractNotFoundError, IncompatibleVersionError
from etl.contracts.registry import ContractRegistry
from etl.contracts.version import ContractVersion


def _make_contract(
    source_id: str = "mcc",
    dataset: str = "allotments",
    version: str = "1.0.0",
) -> SourceContract:
    return SourceContract(
        source_id=source_id,
        source_name="Medical Counselling Committee",
        authority="mcc",
        dataset=dataset,
        source_type=SourceType.CSV,
        contract_version=ContractVersion.parse(version),
        effective_year=2026,
        publication_version="1.0",
        supported_formats=("csv",),
        expected_columns=("college_name", "course_name"),
        required_columns=("college_name",),
        optional_columns=("course_name",),
        field_mapping=(
            FieldMapping(external_name="Institute Name", canonical_name="college_name"),
            FieldMapping(external_name="Course", canonical_name="course_name"),
        ),
    )


class TestContractRegistry:
    """Tests for ContractRegistry."""

    def test_register_and_get(self) -> None:
        registry = ContractRegistry()
        contract = _make_contract()
        registry.register(contract)

        result = registry.get_contract("mcc", "allotments", "1.0.0")
        assert result.source_id == "mcc"

    def test_get_latest_version(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract(version="1.0.0"))
        registry.register(_make_contract(version="1.1.0"))

        result = registry.get_contract("mcc", "allotments")
        assert str(result.contract_version) == "1.1.0"

    def test_get_unknown_source(self) -> None:
        registry = ContractRegistry()
        with pytest.raises(ContractNotFoundError):
            registry.get_contract("unknown", "allotments")

    def test_get_unknown_dataset(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract())
        with pytest.raises(ContractNotFoundError):
            registry.get_contract("mcc", "unknown")

    def test_get_unknown_version(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract())
        with pytest.raises(ContractNotFoundError):
            registry.get_contract("mcc", "allotments", "9.9.9")

    def test_list_sources(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract(source_id="mcc"))
        registry.register(_make_contract(source_id="nmc"))
        assert sorted(registry.list_sources()) == ["mcc", "nmc"]

    def test_list_datasets(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract(dataset="allotments"))
        registry.register(_make_contract(dataset="seat_matrix"))
        assert sorted(registry.list_datasets("mcc")) == [
            "allotments",
            "seat_matrix",
        ]

    def test_list_versions(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract(version="1.0.0"))
        registry.register(_make_contract(version="1.1.0"))
        versions = registry.list_versions("mcc", "allotments")
        assert "1.0.0" in versions
        assert "1.1.0" in versions

    def test_has_contract(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract())
        assert registry.has_contract("mcc", "allotments", "1.0.0")
        assert not registry.has_contract("mcc", "allotments", "9.0.0")

    def test_get_compatible_contract(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract(version="1.0.0"))
        registry.register(_make_contract(version="1.2.0"))

        result = registry.get_compatible_contract("mcc", "allotments", ContractVersion(1, 1, 0))
        assert str(result.contract_version) == "1.2.0"

    def test_get_compatible_incompatible(self) -> None:
        registry = ContractRegistry()
        registry.register(_make_contract(version="1.0.0"))
        with pytest.raises(IncompatibleVersionError):
            registry.get_compatible_contract("mcc", "allotments", ContractVersion(2, 0, 0))
