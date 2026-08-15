"""The service facade: the single entry point consumers use.

``FeatureFlagService`` is constructed by dependency injection with a mapping
of definitions and a sequence of providers; it performs no configuration
loading itself (that is the container's job) and holds no business logic. It
exposes the three reads the rest of the platform needs:

- ``is_enabled(name)`` — cheap boolean for feature gates;
- ``get_state(name)`` — full provenance (value + source + rule match) for
  observability and debugging;
- ``all_states()`` — snapshot for admin/audit surfaces.

Unknown-flag behaviour is a policy choice exposed via ``strict``:
- ``strict=False`` (default): unknown flags evaluate to ``disabled`` with
  source ``UNKNOWN`` and a warning — safe when flags are retired before
  their consumers;
- ``strict=True``: raises ``UnknownFlagError`` — catches typos early in
  environments where every flag name is known.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from feature_flags.errors import FlagConfigurationError, UnknownFlagError
from feature_flags.evaluator import evaluate
from feature_flags.models import FlagContext, FlagDefinition, FlagSource, FlagState
from feature_flags.provider import FlagProvider
from feature_flags.providers.memory import MemoryFlagProvider

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Evaluates feature flags against a provider chain."""

    def __init__(
        self,
        definitions: Mapping[str, FlagDefinition],
        providers: Sequence[FlagProvider],
        *,
        strict: bool = False,
    ) -> None:
        self._definitions = dict(definitions)
        self._providers = list(providers)
        self._strict = strict
        self._memory = next(
            (
                provider
                for provider in self._providers
                if isinstance(provider, MemoryFlagProvider)
            ),
            None,
        )

    # ── Public API ────────────────────────────────────────────────────────
    def is_enabled(self, name: str, context: FlagContext | None = None) -> bool:
        """Return ``True`` when the flag is currently enabled."""
        return self.get_state(name, context).enabled

    def get_state(self, name: str, context: FlagContext | None = None) -> FlagState:
        """Evaluate one flag and return its full provenance."""
        definition = self._definitions.get(name)
        if definition is None:
            if self._strict:
                raise UnknownFlagError(
                    f"Unknown feature flag {name!r} evaluated in strict mode."
                )
            logger.warning("Unknown feature flag %r evaluated; treating as disabled.", name)
            return FlagState(name=name, enabled=False, source=FlagSource.UNKNOWN)
        return evaluate(definition, self._providers, context)

    def all_states(self, context: FlagContext | None = None) -> dict[str, FlagState]:
        """Evaluate every known flag (ordered snapshot for observability)."""
        return {
            name: self.get_state(name, context)
            for name in sorted(self._definitions)
        }

    def set_override(self, name: str, enabled: bool) -> None:
        """Set an in-process override via the memory provider (if present)."""
        if self._memory is None:
            raise FlagConfigurationError(
                "No MemoryFlagProvider is wired; cannot set runtime overrides."
            )
        self._memory.set(name, bool(enabled))

    def clear_override(self, name: str | None = None) -> None:
        """Clear runtime override(s) via the memory provider (if present)."""
        if self._memory is None:
            raise FlagConfigurationError(
                "No MemoryFlagProvider is wired; cannot clear runtime overrides."
            )
        self._memory.clear(name)

    def ensure_schema(self) -> None:
        """Create the database table for every wired database provider."""
        from feature_flags.providers.database import DatabaseFlagProvider

        for provider in self._providers:
            if isinstance(provider, DatabaseFlagProvider):
                provider.ensure_schema()

    @property
    def definitions(self) -> Mapping[str, FlagDefinition]:
        return self._definitions
