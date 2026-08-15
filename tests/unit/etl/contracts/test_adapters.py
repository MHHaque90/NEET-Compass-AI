"""Tests for adapters."""

from etl.contracts.adapters import ColumnMappingAdapter, IdentityAdapter
from etl.contracts.base import FieldMapping, SourceContract, SourceType
from etl.contracts.canonical import SourceMetadata
from etl.contracts.version import ContractVersion


def _make_contract() -> SourceContract:
    return SourceContract(
        source_id="mcc",
        source_name="Medical Counselling Committee",
        authority="mcc",
        dataset="allotments",
        source_type=SourceType.CSV,
        contract_version=ContractVersion.parse("1.0.0"),
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


def _make_metadata() -> SourceMetadata:
    return SourceMetadata(
        source_id="mcc",
        authority="mcc",
        dataset="allotments",
        effective_year=2026,
        publication_version="1.0",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00Z",
    )


class TestIdentityAdapter:
    """Tests for IdentityAdapter."""

    def test_transform(self) -> None:
        adapter = IdentityAdapter()
        data = [{"college": "AIIMS", "course": "MBBS"}]
        result = adapter.transform(data, _make_contract(), _make_metadata())
        assert result.records == data
        assert result.records_transformed == 1

    def test_validate_source(self) -> None:
        adapter = IdentityAdapter()
        errors = adapter.validate_source([{"data": 1}], _make_contract())
        assert len(errors) == 0

    def test_validate_source_empty(self) -> None:
        adapter = IdentityAdapter()
        errors = adapter.validate_source([], _make_contract())
        assert len(errors) == 1


class TestColumnMappingAdapter:
    """Tests for ColumnMappingAdapter."""

    def test_transform(self) -> None:
        adapter = ColumnMappingAdapter()
        data = [{"Institute Name": "AIIMS", "Course": "MBBS"}]
        result = adapter.transform(data, _make_contract(), _make_metadata())
        assert result.records[0]["college_name"] == "AIIMS"
        assert result.records[0]["course_name"] == "MBBS"

    def test_validate_source(self) -> None:
        adapter = ColumnMappingAdapter()
        data = [{"Institute Name": "AIIMS", "Course": "MBBS"}]
        errors = adapter.validate_source(data, _make_contract())
        assert len(errors) == 0

    def test_validate_source_missing_column(self) -> None:
        adapter = ColumnMappingAdapter()
        data = [{"Course": "MBBS"}]
        errors = adapter.validate_source(data, _make_contract())
        assert len(errors) == 1
        assert "Institute Name" in errors[0]
