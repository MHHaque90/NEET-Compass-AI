"""Tests for base contract."""

from etl.contracts.base import FieldMapping, SourceContract, SourceType, ValidationRule
from etl.contracts.version import ContractVersion


class TestSourceContract:
    """Tests for SourceContract."""

    def _make_contract(self) -> SourceContract:
        return SourceContract(
            source_id="mcc",
            source_name="Medical Counselling Committee",
            authority="mcc",
            dataset="allotments",
            source_type=SourceType.CSV,
            contract_version=ContractVersion.parse("1.0.0"),
            effective_year=2026,
            publication_version="1.0",
            supported_formats=("csv", "excel"),
            expected_columns=("college_name", "course_name"),
            required_columns=("college_name",),
            optional_columns=("course_name",),
            field_mapping=(
                FieldMapping(external_name="Institute Name", canonical_name="college_name"),
                FieldMapping(external_name="Course", canonical_name="course_name"),
            ),
            validation_rules=(ValidationRule(field_name="rank", rule_type="required"),),
        )

    def test_get_canonical_name(self) -> None:
        contract = self._make_contract()
        assert contract.get_canonical_name("Institute Name") == "college_name"

    def test_get_canonical_name_unknown(self) -> None:
        contract = self._make_contract()
        assert contract.get_canonical_name("Unknown") is None

    def test_get_external_name(self) -> None:
        contract = self._make_contract()
        assert contract.get_external_name("college_name") == "Institute Name"

    def test_is_required_column(self) -> None:
        contract = self._make_contract()
        assert contract.is_required_column("college_name")
        assert not contract.is_required_column("course_name")

    def test_is_expected_column(self) -> None:
        contract = self._make_contract()
        assert contract.is_expected_column("college_name")
        assert contract.is_expected_column("course_name")
        assert not contract.is_expected_column("unknown")

    def test_supports_format(self) -> None:
        contract = self._make_contract()
        assert contract.supports_format("csv")
        assert contract.supports_format("excel")
        assert not contract.supports_format("pdf")

    def test_get_validation_rules(self) -> None:
        contract = self._make_contract()
        rules = contract.get_validation_rules_for_field("rank")
        assert len(rules) == 1
