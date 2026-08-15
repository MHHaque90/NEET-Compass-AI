"""Environment-variable provider tests."""

from __future__ import annotations

import pytest

from feature_flags.errors import MalformedFlagValueError
from feature_flags.models import FlagSource
from feature_flags.providers.env_var import EnvVarFlagProvider


def _provider(**env: str) -> EnvVarFlagProvider:
    return EnvVarFlagProvider(environ=dict(env))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("enabled", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("disabled", False),
        ("  true  ", True),  # whitespace tolerated
    ],
)
def test_parses_boolean_literals(raw: str, expected: bool) -> None:
    provider = _provider(**{"FF_ENGINES_RULE": raw})
    assert provider.get_enabled("engines.rule") is expected


def test_env_key_convention() -> None:
    provider = _provider(**{"FF_EXPERIMENTAL_CHOICE_FILLING_V2": "true"})
    assert provider.get_enabled("experimental.choice_filling_v2") is True


def test_custom_prefix() -> None:
    provider = EnvVarFlagProvider(prefix="MYAPP_", environ={"MYAPP_FOO": "true"})
    assert provider.get_enabled("foo") is True


def test_unset_var_returns_none() -> None:
    assert _provider().get_enabled("engines.rule") is None


def test_malformed_value_raises() -> None:
    provider = _provider(**{"FF_ENGINES_RULE": "treu"})
    with pytest.raises(MalformedFlagValueError):
        provider.get_enabled("engines.rule")


def test_source_identity() -> None:
    assert _provider().source == FlagSource.ENV
