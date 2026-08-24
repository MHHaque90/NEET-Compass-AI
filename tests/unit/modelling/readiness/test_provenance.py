"""Tests for Provenance Completeness — Sprint 4.1.

Critical assertions:
- Missing provenance -> NOT_READY
- All required fields must be present (11 fields including source_url)
"""

import pytest
from etl.contracts.historical.provenance_gate import (
    ProvenanceGate,
    ProvenanceGateResult,
    REQUIRED_PROVENANCE_FIELDS,
    validate_provenance,
)
from etl.contracts.canonical import SourceMetadata


class TestProvenanceGate:
    """Test provenance gate validation."""

    def test_required_fields_count(self):
        """Should have exactly 11 required provenance fields (including source_url)."""
        assert len(REQUIRED_PROVENANCE_FIELDS) == 11
        expected = {
            "source_id", "authority", "dataset", "effective_year",
            "publication_version", "contract_version", "retrieval_timestamp",
            "source_file_id", "file_checksum", "parser_version",
            "source_url",
        }
        assert set(REQUIRED_PROVENANCE_FIELDS) == expected

    def test_provenance_passes_with_all_fields(self):
        """ProvenanceGate should pass when all 11 fields present."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        )

        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is True
        assert result.missing_fields == ()
        assert len(result.present_fields) == 11

    def test_provenance_fails_with_missing_field(self):
        """ProvenanceGate should fail when any required field missing."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="",  # MISSING
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        )

        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is False
        assert "retrieval_timestamp" in result.missing_fields
        assert result.details["missing_count"] == 1

    def test_provenance_fails_with_multiple_missing(self):
        """ProvenanceGate should report all missing fields."""
        metadata = SourceMetadata(
            source_id="",
            authority="",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="",
            contract_version="",
            retrieval_timestamp="",
            source_file_id="",
            file_checksum="",
            parser_version="",
            source_url="",
        )

        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is False
        assert result.details["missing_count"] > 1
        assert result.details["present_count"] < 11

    def test_provenance_validates_dict(self):
        """ProvenanceGate should validate from dict."""
        data = {
            "source_id": "mcc_ug_archive",
            "authority": "Medical Counselling Committee",
            "dataset": "seat_matrix",
            "effective_year": 2024,
            "publication_version": "Round 1",
            "contract_version": "1.1.0",
            "retrieval_timestamp": "2026-08-15T14:30:00+00:00",
            "source_file_id": "mcc_ug_archive_seat_matrix_2024_abc123",
            "file_checksum": "abc123def456",
            "parser_version": "mcc_etl_v1",
            "source_url": "https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        }

        gate = ProvenanceGate()
        result = gate.validate_dict(data)
        assert result.passed is True

    def test_provenance_dict_missing_fields(self):
        """ProvenanceGate should detect missing fields from dict."""
        data = {
            "source_id": "mcc_ug_archive",
            "authority": "Medical Counselling Committee",
            # Missing most fields
        }

        gate = ProvenanceGate()
        result = gate.validate_dict(data)
        assert result.passed is False
        assert result.details["missing_count"] > 1

    def test_empty_string_counts_as_missing(self):
        """Empty string should count as missing."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="",  # Empty string
        )

        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is False
        assert "source_url" in result.missing_fields

    def test_none_value_counts_as_missing(self):
        """None value should count as missing."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url=None,  # None
        )

        gate = ProvenanceGate()
        result = gate.validate(metadata)
        assert result.passed is False
        assert "source_url" in result.missing_fields

    def test_convenience_function(self):
        """validate_provenance convenience function."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        )

        result = validate_provenance(metadata)
        assert isinstance(result, ProvenanceGateResult)
        assert result.passed is True

    def test_result_boolean_conversion(self):
        """ProvenanceGateResult converts to bool."""
        result_pass = ProvenanceGateResult(
            passed=True, missing_fields=(), present_fields=("a",), details={}
        )
        result_fail = ProvenanceGateResult(
            passed=False, missing_fields=("a",), present_fields=(), details={}
        )
        assert bool(result_pass) is True
        assert bool(result_fail) is False