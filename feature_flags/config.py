"""YAML configuration loading for flag definitions and overrides.

The shipped file (``config/flags.yaml``) has two sections:

- ``definitions:`` — the flag catalogue: name -> description/category/default/
  rules/owner. This is the *source of truth* for what flags exist.
- ``overrides:`` — deploy-baseline toggles applied by the
  ``ConfigFileFlagProvider``. Values are booleans (or ``{enabled: bool}``).

Loading is strict: a malformed definition raises so a broken deploy fails
before any flag is evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from feature_flags.errors import FlagConfigurationError
from feature_flags.models import FlagDefinition


@dataclass(frozen=True)
class FlagConfig:
    """Parsed flag configuration: definitions plus raw overrides."""

    definitions: dict[str, FlagDefinition]
    overrides: dict[str, Any]


def load_flags_yaml(path: str | Path) -> FlagConfig:
    """Parse a flags file into definitions and overrides."""
    config_path = Path(path)
    if not config_path.exists():
        raise FlagConfigurationError(f"Flag configuration file not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    definitions: dict[str, FlagDefinition] = {}
    raw_definitions = data.get("definitions", {})
    if not isinstance(raw_definitions, dict):
        raise FlagConfigurationError("'definitions' must be a mapping of flag name -> spec.")
    for name, raw in raw_definitions.items():
        if not isinstance(name, str):
            raise FlagConfigurationError("Flag names must be strings.")
        spec = dict(raw) if isinstance(raw, dict) else {"default": bool(raw)}
        spec.pop("name", None)
        try:
            definitions[name] = FlagDefinition(name=name, **spec)
        except Exception as exc:
            raise FlagConfigurationError(
                f"Invalid definition for flag {name!r}: {exc}"
            ) from exc

    overrides = data.get("overrides", {})
    if overrides is None:
        overrides = {}
    if not isinstance(overrides, dict):
        raise FlagConfigurationError("'overrides' must be a mapping of flag name -> value.")

    return FlagConfig(definitions=definitions, overrides=dict(overrides))
