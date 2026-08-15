"""Environment-variable provider.

The highest-precedence source and the operations "kill switch": a flag can be
forced off (or on) across every instance by setting one variable, no deploy,
no DB access required.

Convention: ``FF_`` + upper-snake name with dots replaced by underscores.
``engines.rule`` -> ``FF_ENGINES_RULE``.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from feature_flags.errors import MalformedFlagValueError
from feature_flags.models import FlagSource
from feature_flags.provider import FlagProvider

_TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}
_FALSE_VALUES = {"0", "false", "no", "off", "disabled"}


class EnvVarFlagProvider(FlagProvider):
    """Reads boolean flag values from environment variables."""

    source = FlagSource.ENV

    def __init__(self, prefix: str = "FF_", environ: Mapping[str, str] | None = None) -> None:
        self._prefix = prefix
        self._environ = environ if environ is not None else os.environ

    def _key(self, name: str) -> str:
        return self.key_for(name)

    def key_for(self, name: str) -> str:
        """Return the environment variable that controls ``name``.

        e.g. ``key_for("engines.rule") == "FF_ENGINES_RULE"``. Exposed so
        the introspection service can show operators exactly which variable
        to inspect or unset.
        """
        return self._prefix + name.replace(".", "_").upper()

    def get_enabled(self, name: str) -> bool | None:
        raw = self._environ.get(self._key(name))
        if raw is None:
            return None
        normalized = raw.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
        raise MalformedFlagValueError(
            f"Environment variable {self._key(name)!r} has unparseable value "
            f"{raw!r}; expected one of {sorted(_TRUE_VALUES | _FALSE_VALUES)}."
        )
