"""Tests for SHA-256 checksum."""

from etl.contracts.canonical.checksum import (
    compute_checksum,
    compute_string_checksum,
)


class TestChecksum:
    """Tests for SHA-256 checksums."""

    def test_same_data_same_checksum(self) -> None:
        data = b"hello world"
        assert compute_checksum(data) == compute_checksum(data)

    def test_different_data_different_checksum(self) -> None:
        assert compute_checksum(b"hello") != compute_checksum(b"world")

    def test_string_checksum(self) -> None:
        result = compute_string_checksum("test")
        assert len(result) == 64  # SHA-256 hex digest length

    def test_empty_data(self) -> None:
        result = compute_checksum(b"")
        assert len(result) == 64

    def test_deterministic(self) -> None:
        data = b"NEET Compass AI"
        c1 = compute_checksum(data)
        c2 = compute_checksum(data)
        assert c1 == c2
