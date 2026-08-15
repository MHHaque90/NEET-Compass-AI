"""Tests for contract versioning."""

from etl.contracts.version import ContractVersion


class TestContractVersion:
    """Tests for ContractVersion."""

    def test_parse_valid(self) -> None:
        v = ContractVersion.parse("1.0.0")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0

    def test_parse_complex(self) -> None:
        v = ContractVersion.parse("2.3.5")
        assert v.major == 2
        assert v.minor == 3
        assert v.patch == 5

    def test_parse_invalid(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            ContractVersion.parse("invalid")

    def test_parse_partial(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            ContractVersion.parse("1.0")

    def test_str(self) -> None:
        v = ContractVersion(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_compatible_same(self) -> None:
        v = ContractVersion(1, 0, 0)
        assert v.is_compatible_with(ContractVersion(1, 0, 0))

    def test_compatible_higher_minor(self) -> None:
        v = ContractVersion(1, 2, 0)
        assert v.is_compatible_with(ContractVersion(1, 0, 0))

    def test_incompatible_higher_major(self) -> None:
        v = ContractVersion(2, 0, 0)
        assert not v.is_compatible_with(ContractVersion(1, 0, 0))

    def test_incompatible_lower_minor(self) -> None:
        v = ContractVersion(1, 0, 0)
        assert not v.is_compatible_with(ContractVersion(1, 2, 0))

    def test_breaking_change(self) -> None:
        v1 = ContractVersion(1, 0, 0)
        v2 = ContractVersion(2, 0, 0)
        assert v2.is_breaking_change_from(v1)

    def test_non_breaking_change(self) -> None:
        v1 = ContractVersion(1, 0, 0)
        v2 = ContractVersion(1, 1, 0)
        assert not v2.is_breaking_change_from(v1)

    def test_next_major(self) -> None:
        v = ContractVersion(1, 2, 3)
        assert v.next_major() == ContractVersion(2, 0, 0)

    def test_next_minor(self) -> None:
        v = ContractVersion(1, 2, 3)
        assert v.next_minor() == ContractVersion(1, 3, 0)

    def test_next_patch(self) -> None:
        v = ContractVersion(1, 2, 3)
        assert v.next_patch() == ContractVersion(1, 2, 4)
