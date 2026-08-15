"""Tests for contract validation."""

from __future__ import annotations

from etl.contracts.base import FieldMapping, SourceContract, SourceType, ValidationRule
from etl.contracts.validators import ContractValidator, ValidationMode
from etl.contracts.version import ContractVersion


def _make_contract_with_rules() -> SourceContract:
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
        expected_columns=("college_name", "course_name", "rank", "score"),
        required_columns=("college_name", "course_name"),
        optional_columns=("rank", "score"),
        field_mapping=(
            FieldMapping(external_name="Institute Name", canonical_name="college_name"),
            FieldMapping(external_name="Course", canonical_name="course_name"),
            FieldMapping(external_name="Rank", canonical_name="rank"),
            FieldMapping(external_name="Score", canonical_name="score"),
        ),
        validation_rules=(
            ValidationRule(field_name="rank", rule_type="required"),
            ValidationRule(field_name="rank", rule_type="type", params={"type": "int"}),
            ValidationRule(field_name="rank", rule_type="range", params={"min": 1, "max": 100000}),
            ValidationRule(
                field_name="score",
                rule_type="range",
                params={"min": 0.0, "max": 100.0},
            ),
        ),
    )


class TestColumnValidation:
    """Tests for column validation."""

    def test_valid_columns_strict(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract, ValidationMode.STRICT)
        errors = validator.validate_columns(
            ["Institute Name", "Course", "Rank", "Score"], "mcc", "allotments"
        )
        assert len(errors) == 0

    def test_missing_required_column(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract, ValidationMode.STRICT)
        errors = validator.validate_columns(["Rank", "Score"], "mcc", "allotments")
        assert any(e.error_code.value == "MISSING_REQUIRED_COLUMN" for e in errors)

    def test_unknown_column_strict(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract, ValidationMode.STRICT)
        errors = validator.validate_columns(
            ["Institute Name", "Course", "Unknown"], "mcc", "allotments"
        )
        assert any(e.error_code.value == "UNKNOWN_COLUMN" for e in errors)

    def test_unknown_column_compatible(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract, ValidationMode.COMPATIBLE)
        errors = validator.validate_columns(
            ["Institute Name", "Course", "Unknown"], "mcc", "allotments"
        )
        assert not any(e.error_code.value == "UNKNOWN_COLUMN" for e in errors)


class TestRowValidation:
    """Tests for row validation."""

    def test_valid_row(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        errors = validator.validate_row({"rank": 100, "score": 85.5}, 1, "mcc", "allotments")
        assert len(errors) == 0

    def test_null_required_field(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        errors = validator.validate_row({"rank": None, "score": 85.5}, 1, "mcc", "allotments")
        assert any(e.error_code.value == "NULL_NOT_ALLOWED" for e in errors)

    def test_invalid_type(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        errors = validator.validate_row(
            {"rank": "not_a_number", "score": 85.5}, 1, "mcc", "allotments"
        )
        assert any(e.error_code.value == "INVALID_TYPE" for e in errors)

    def test_out_of_range(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        errors = validator.validate_row({"rank": 200000, "score": 85.5}, 1, "mcc", "allotments")
        assert any(e.error_code.value == "OUT_OF_RANGE" for e in errors)

    def test_score_out_of_range(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        errors = validator.validate_row({"rank": 100, "score": 150.0}, 1, "mcc", "allotments")
        assert any(e.error_code.value == "OUT_OF_RANGE" for e in errors)


class TestRecordValidation:
    """Tests for full record validation."""

    def test_valid_records(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        records = [
            {"rank": 100, "score": 85.5},
            {"rank": 200, "score": 90.0},
        ]
        result = validator.validate_records(records, "mcc", "allotments", 2026, "1.0")
        assert result.is_valid
        assert result.records_checked == 2
        assert result.records_valid == 2

    def test_invalid_records(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        records = [
            {"rank": 100, "score": 85.5},
            {"rank": None, "score": 90.0},
        ]
        result = validator.validate_records(records, "mcc", "allotments", 2026, "1.0")
        assert not result.is_valid
        assert result.records_invalid == 1

    def test_validation_result_structure(self) -> None:
        contract = _make_contract_with_rules()
        validator = ContractValidator(contract)
        records = [{"rank": 100, "score": 85.5}]
        result = validator.validate_records(records, "mcc", "allotments", 2026, "1.0")
        result_dict = result.to_dict()
        assert result_dict["source_id"] == "mcc"
        assert result_dict["dataset"] == "allotments"
        assert result_dict["effective_year"] == 2026
