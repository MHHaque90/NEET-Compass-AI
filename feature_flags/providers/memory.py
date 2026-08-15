"""In-process memory provider.

Used for runtime overrides set by the application itself (e.g. an ops admin
toggling a flag for the lifetime of the process) and by tests. Sits between
environment variables and the database in precedence.
"""

from __future__ import annotations

from feature_flags.models import FlagSource
from feature_flags.provider import FlagProvider


class MemoryFlagProvider(FlagProvider):
    """Maps flag names to explicit boolean overrides."""

    source = FlagSource.MEMORY

    def __init__(self, overrides: dict[str, bool] | None = None) -> None:
        self._overrides: dict[str, bool] = dict(overrides or {})

    def get_enabled(self, name: str) -> bool | None:
        return self._overrides.get(name)

    def set(self, name: str, enabled: bool) -> None:
        """Set a runtime override for one flag."""
        self._overrides[name] = bool(enabled)

    def clear(self, name: str | None = None) -> None:
        """Remove one override, or all when ``name`` is omitted."""
        if name is None:
            self._overrides.clear()
        else:
            self._overrides.pop(name, None)
