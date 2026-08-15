"""Configuration-file provider.

Reads flag overrides from the ``overrides:`` section of a YAML file shipped
with the deployment. This is the *deploy-baseline* source: it changes with a
release but not at runtime. A missing file degrades to "no overrides" unless
``required=True`` (a deploy that is supposed to ship overrides but forgot
them is a configuration error and should fail fast).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from feature_flags.errors import FlagConfigurationError, MalformedFlagValueError
from feature_flags.models import FlagSource
from feature_flags.provider import FlagProvider

logger = logging.getLogger(__name__)


class ConfigFileFlagProvider(FlagProvider):
    """Reads boolean overrides from a YAML ``overrides:`` section."""

    source = FlagSource.CONFIG_FILE

    def __init__(
        self,
        path: str | Path,
        section: str = "overrides",
        *,
        required: bool = False,
    ) -> None:
        self._path = Path(path)
        self._section = section
        self._overrides: dict[str, Any] = self._load(required)

    def _load(self, required: bool) -> dict[str, Any]:
        if not self._path.exists():
            if required:
                raise FlagConfigurationError(
                    f"Required flag configuration file not found: {self._path}"
                )
            logger.warning(
                "Flag configuration file %s not found; treating as empty.", self._path
            )
            return {}
        data = yaml.safe_load(self._path.read_text(encoding="utf-8")) or {}
        section = data.get(self._section, {})
        if section is None:
            return {}
        if not isinstance(section, dict):
            raise FlagConfigurationError(
                f"Section {self._section!r} in {self._path} must be a mapping."
            )
        return dict(section)

    def get_enabled(self, name: str) -> bool | None:
        raw = self._overrides.get(name)
        if raw is None:
            return None
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, dict):
            enabled = raw.get("enabled")
            if isinstance(enabled, bool):
                return enabled
        raise MalformedFlagValueError(
            f"Override for flag {name!r} in {self._path} must be a boolean or "
            f"a mapping with an 'enabled' boolean; got {raw!r}."
        )
