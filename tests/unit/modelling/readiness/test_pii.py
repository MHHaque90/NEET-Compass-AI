"""Tests for PII Rejection — Sprint 4.1.

Critical assertions:
- Candidate PII detection -> REJECTED (NOT_READY)
- PII gate fails closed
- Blocklist covers known NEET counselling PII patterns
- Fuzzy patterns also catch related fields
"""

import pytest
from etl.contracts.historical.pii_gate import (
    PIIGate,
    PIIGateResult,
    PII_BLOCKLIST,
    PII_PATTERNS,
    detect_pii,
    validate_no_pii,
)


class TestPIIGate:
    """Test PII detection and rejection."""

    def test_blocklist_contains_expected_fields(self):
        """PII_BLOCKLIST should contain known candidate identifiers."""
        expected = {
            "candidate_name",
            "father_name",
            "roll_number",
            "application_number",
            "phone",
            "email",
            "aadhaar",
            "percentile",
            "neet_score",
            "all_india_rank",
            "state_rank",
        }
        for field in expected:
            assert field in PII_BLOCKLIST, f"Missing from blocklist: {field}"

    def test_detect_pii_exact_match(self):
        """detect_pii should flag exact blocklist matches."""
        headers = ["Institute Code", "Candidate Name", "Rank", "Score"]
        detected = detect_pii(headers)
        # "Candidate Name" is in blocklist, "Rank" and "Score" match fuzzy patterns
        assert "Candidate Name" in detected

    def test_detect_pii_case_insensitive(self):
        """PII detection should be case-insensitive for blocklist."""
        headers = ["candidate_name", "FATHER_NAME", "Roll_Number"]
        detected = detect_pii(headers)
        assert "candidate_name" in detected
        assert "FATHER_NAME" in detected
        assert "Roll_Number" in detected

    def test_detect_pii_multiple_matches(self):
        """Should detect multiple PII fields."""
        headers = ["Candidate Name", "Father Name", "Phone", "Email", "Rank"]
        detected = detect_pii(headers)
        assert "Candidate Name" in detected
        assert "Father Name" in detected
        assert "Phone" in detected
        assert "Email" in detected
        # Rank also matches fuzzy pattern
        assert "Rank" in detected

    def test_detect_pii_fuzzy_patterns(self):
        """Fuzzy patterns catch category, rank, score related fields."""
        headers = ["Category", "Rank", "Score", "Percentile"]
        detected = detect_pii(headers)
        # All match fuzzy patterns
        assert "Category" in detected  # matches "category" pattern
        assert "Rank" in detected      # matches "rank" pattern
        assert "Score" in detected     # matches "score" pattern
        assert "Percentile" in detected  # matches "percentile" pattern

    def test_pii_gate_fails_on_detected_pii(self):
        """PIIGate should fail (REJECTED) when PII detected."""
        gate = PIIGate()
        headers = ["Institute Code", "Candidate Name", "Father Name", "Rank"]
        result = gate.validate(headers)
        assert result.passed is False
        assert "Candidate Name" in result.detected_fields
        assert "Father Name" in result.detected_fields

    def test_pii_gate_details_include_scanned_fields(self):
        """PIIGateResult should include all scanned fields."""
        gate = PIIGate()
        headers = ["Institute Code", "Candidate Name", "Rank"]
        result = gate.validate(headers)
        assert "Institute Code" in result.scanned_fields
        assert "Candidate Name" in result.scanned_fields
        assert "Rank" in result.scanned_fields

    def test_pii_gate_fails_closed(self):
        """PII gate fails closed - any PII means NOT_READY."""
        gate = PIIGate()
        headers = ["Institute Code", "Candidate Name", "Rank", "Score"]
        result = gate.validate(headers)
        assert result.passed is False

    def test_validate_no_pii_function(self):
        """validate_no_pii convenience function returns PIIGateResult."""
        result = validate_no_pii(["Institute Code", "Candidate Name", "Rank"])
        assert isinstance(result, PIIGateResult)
        assert result.passed is False
        assert "Candidate Name" in result.detected_fields

    def test_pii_patterns_fuzzy_matching(self):
        """PII_PATTERNS should cover fuzzy matching categories."""
        assert "candidate" in PII_PATTERNS
        assert "applicant" in PII_PATTERNS
        assert "aadhaar" in PII_PATTERNS
        assert "percentile" in PII_PATTERNS


class TestPIIResult:
    """Test PIIGateResult structure."""

    def test_result_boolean_conversion(self):
        """PIIGateResult should convert to bool based on passed."""
        result_pass = PIIGateResult(
            passed=True, detected_fields=(), scanned_fields=("a",), details={}
        )
        result_fail = PIIGateResult(
            passed=False, detected_fields=("Candidate Name",), scanned_fields=("a",), details={}
        )
        assert bool(result_pass) is True
        assert bool(result_fail) is False