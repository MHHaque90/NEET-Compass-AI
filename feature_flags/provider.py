"""Provider contract.

A ``FlagProvider`` is a read-only source of flag states. Every provider
reports the ``FlagSource`` it represents so the evaluator can apply a single,
declared precedence order regardless of the order providers are registered.
Returning ``None`` means *"this source does not manage that flag"* — the
evaluator then falls through to the next source.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from feature_flags.models import FlagSource


class FlagProvider(ABC):
    """Abstract read-side access to flag values for one source."""

    source: FlagSource

    @abstractmethod
    def get_enabled(self, name: str) -> bool | None:
        """Return the flag's value from this source, or ``None`` if unset.

        Providers must raise ``MalformedFlagValueError`` for values they own
        but cannot parse (never silently return ``None`` for corruption).
        """

    def get_updated_at(self, name: str) -> datetime | None:
        """Return when this source last modified the flag, or ``None``.

        Only time-aware sources (e.g. the database) override this; it is
        used by the introspection service. Defaults to ``None`` (unknown).
        """
        return None
