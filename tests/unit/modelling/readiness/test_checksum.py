"""Tests for Checksum Verification / Artifact Integrity — Sprint 4.1.

Critical assertions:
- Same bytes -> same checksum -> same identity
- Modified bytes -> different checksum -> different identity
- Missing checksum -> NOT_READY
"""

import pytest
from etl.contracts.historical.artifact_integrity import (
    ArtifactIntegrity,
    ArtifactIntegrityResult,
    build_source_file_id,
    compute_artifact_hash,
    verify_artifact_integrity,
)


class TestArtifactIntegrity:
    """Test deterministic artifact integrity verification."""

    def test_same_bytes_same_hash(self):
        """Same bytes must produce identical SHA-256."""
        data = b"test artifact content"
        hash1 = compute_artifact_hash(data)
        hash2 = compute_artifact_hash(data)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_modified_bytes_different_hash(self):
        """Modified bytes must produce different SHA-256."""
        data1 = b"original content"
        data2 = b"modified content"
        hash1 = compute_artifact_hash(data1)
        hash2 = compute_artifact_hash(data2)
        assert hash1 != hash2

    def test_build_source_file_id_deterministic(self):
        """Same (checksum, source_id, dataset, year) -> same source_file_id."""
        checksum = "a" * 64
        id1 = build_source_file_id(checksum, "mcc_ug_archive", "seat_matrix", 2024)
        id2 = build_source_file_id(checksum, "mcc_ug_archive", "seat_matrix", 2024)
        assert id1 == id2
        assert "mcc_ug_archive_seat_matrix_2024" in id1
        assert id1.endswith("aaaaaaaaaaaa")  # First 12 chars of checksum

    def test_different_checksum_different_id(self):
        """Different checksum -> different source_file_id."""
        id1 = build_source_file_id("a" * 64, "mcc_ug_archive", "seat_matrix", 2024)
        id2 = build_source_file_id("b" * 64, "mcc_ug_archive", "seat_matrix", 2024)
        assert id1 != id2

    def test_artifact_integrity_verify_pass(self):
        """Verification passes when checksum matches."""
        integrity = ArtifactIntegrity("mcc_ug_archive", "seat_matrix", 2024)
        data = b"test content for verification"
        expected = compute_artifact_hash(data)

        result = integrity.verify(data, expected_checksum=expected)
        assert result.passed is True
        assert result.checksum == expected
        assert result.source_file_id is not None
        assert result.details["checksum_match"] is True

    def test_artifact_integrity_verify_fail(self):
        """Verification fails when checksum doesn't match."""
        integrity = ArtifactIntegrity("mcc_ug_archive", "seat_matrix", 2024)
        data = b"test content"
        wrong_checksum = "b" * 64

        result = integrity.verify(data, expected_checksum=wrong_checksum)
        assert result.passed is False
        assert result.details["checksum_match"] is False

    def test_artifact_integrity_no_expected_checksum(self):
        """Verification passes (no expected) but records actual checksum."""
        integrity = ArtifactIntegrity("mcc_ug_archive", "seat_matrix", 2024)
        data = b"test content"

        result = integrity.verify(data, expected_checksum=None)
        assert result.passed is True  # No expected, so passes
        assert result.checksum == compute_artifact_hash(data)
        assert result.source_file_id is not None
        assert result.details["expected_checksum"] is None

    def test_verify_file_method(self, tmp_path):
        """Verify file integrity from path."""
        integrity = ArtifactIntegrity("mcc_ug_archive", "seat_matrix", 2024)
        test_file = tmp_path / "test_artifact.csv"
        test_content = b"col1,col2\nval1,val2\n"
        test_file.write_bytes(test_content)
        expected = compute_artifact_hash(test_content)

        result = integrity.verify_file(test_file, expected_checksum=expected)
        assert result.passed is True
        assert result.checksum == expected
        assert result.details["file_path"] == str(test_file)

    def test_verify_artifact_integrity_function(self):
        """Convenience function verify_artifact_integrity works with expected_checksum."""
        data = b"convenience function test"
        expected = compute_artifact_hash(data)
        result = verify_artifact_integrity(
            data, "mcc_ug_archive", "seat_matrix", 2024, expected_checksum=expected
        )
        assert isinstance(result, ArtifactIntegrityResult)
        assert result.passed is True
        assert result.checksum == expected

    def test_verify_artifact_integrity_function_missing_checksum(self):
        """verify_artifact_integrity fails when expected_checksum is None."""
        data = b"convenience function test"
        result = verify_artifact_integrity(
            data, "mcc_ug_archive", "seat_matrix", 2024, expected_checksum=None
        )
        assert isinstance(result, ArtifactIntegrityResult)
        assert result.passed is False
        assert result.details.get("missing_checksum") is True

    def test_empty_data_hash(self):
        """Empty data produces valid hash."""
        hash_val = compute_artifact_hash(b"")
        assert len(hash_val) == 64
        # SHA-256 of empty string
        assert hash_val == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TestChecksumMissingMeansNotReady:
    """Tests enforcing that missing checksum means NOT_READY."""

    def test_missing_checksum_in_manifest_fails_integrity(self):
        """If manifest has empty sha256, integrity check should fail."""
        integrity = ArtifactIntegrity("test", "test", 2024)
        # Empty checksum means we can't verify
        result = integrity.verify(b"data", expected_checksum="")
        # Empty string won't match actual hash
        assert result.passed is False
        assert result.details["checksum_match"] is False