"""Configuration-file provider tests."""

from __future__ import annotations

import pytest

from feature_flags.errors import FlagConfigurationError, MalformedFlagValueError
from feature_flags.models import FlagSource
from feature_flags.providers.config_file import ConfigFileFlagProvider


def _write(path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_reads_boolean_overrides(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    _write(path, "overrides:\n  engines.rule: true\n  engines.ml: false\n")

    provider = ConfigFileFlagProvider(path)

    assert provider.get_enabled("engines.rule") is True
    assert provider.get_enabled("engines.ml") is False
    assert provider.get_enabled("engines.llm") is None


def test_reads_mapping_form(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    _write(path, "overrides:\n  engines.rule:\n    enabled: true\n")

    provider = ConfigFileFlagProvider(path)
    assert provider.get_enabled("engines.rule") is True


def test_missing_file_is_empty_by_default(tmp_path) -> None:
    provider = ConfigFileFlagProvider(tmp_path / "nope.yaml")
    assert provider.get_enabled("engines.rule") is None


def test_missing_file_required_raises(tmp_path) -> None:
    with pytest.raises(FlagConfigurationError):
        ConfigFileFlagProvider(tmp_path / "nope.yaml", required=True)


def test_malformed_override_raises(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    _write(path, "overrides:\n  engines.rule: maybe\n")
    provider = ConfigFileFlagProvider(path)
    with pytest.raises(MalformedFlagValueError):
        provider.get_enabled("engines.rule")


def test_non_mapping_section_raises(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    _write(path, "overrides: [a, b]\n")
    with pytest.raises(FlagConfigurationError):
        ConfigFileFlagProvider(path)


def test_source_identity(tmp_path) -> None:
    path = tmp_path / "flags.yaml"
    _write(path, "overrides: {}\n")
    assert ConfigFileFlagProvider(path).source == FlagSource.CONFIG_FILE
