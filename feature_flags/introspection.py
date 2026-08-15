"""Feature flag introspection service.

A read-only, dependency-injected counterpart to ``FeatureFlagService`` that
lists the whole flag catalogue and, for every flag, reports the resolved
value, the winning source, its precedence priority, and each configured
source's own override (environment / memory / database / config file).

It is built from the *same* definitions and providers the evaluation path
uses, so what introspection shows is exactly what the flags evaluate to —
there is no separate "display state" that could drift from reality. No
business logic, prediction logic, UI, or REST layer is involved.

Unknown flags mirror ``FeatureFlagService``: ``introspect_flag`` returns
``None`` in lenient mode and raises ``UnknownFlagError`` in strict mode.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from feature_flags.errors import UnknownFlagError
from feature_flags.evaluator import evaluate, source_priority
from feature_flags.models import FlagContext, FlagDefinition, FlagSource
from feature_flags.models.introspection import FlagIntrospection, FlagIntrospectionReport
from feature_flags.provider import FlagProvider
from feature_flags.providers.env_var import EnvVarFlagProvider

_DEFAULT_PROVIDER_NAME = "definition-default"
_UNKNOWN_PROVIDER_NAME = "unknown-flag"

_OVERRIDE_SOURCES: tuple[FlagSource, ...] = (
    FlagSource.ENV,
    FlagSource.MEMORY,
    FlagSource.DATABASE,
    FlagSource.CONFIG_FILE,
)


class FeatureFlagIntrospection:
    """Builds introspection snapshots from definitions + a provider chain."""

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

    def introspect_flag(
        self,
        name: str,
        context: FlagContext | None = None,
    ) -> FlagIntrospection | None:
        """Introspect one flag, or ``None`` when unknown (lenient mode)."""
        definition = self._definitions.get(name)
        if definition is None:
            if self._strict:
                raise UnknownFlagError(
                    f"Unknown feature flag {name!r} introspected in strict mode."
                )
            return None
        return self._build(definition, context)

    def all_flags(self, context: FlagContext | None = None) -> FlagIntrospectionReport:
        """Snapshot of every known flag, sorted by name (deterministic)."""
        return FlagIntrospectionReport(
            flags=[
                self._build(definition, context)
                for definition in sorted(self._definitions.values(), key=lambda d: d.name)
            ]
        )

    def _build(
        self,
        definition: FlagDefinition,
        context: FlagContext | None,
    ) -> FlagIntrospection:
        state = evaluate(definition, self._providers, context)

        overrides: dict[FlagSource, bool | None] = {}
        winning_provider: FlagProvider | None = None
        for provider in self._providers:
            if provider.source in _OVERRIDE_SOURCES:
                overrides[provider.source] = provider.get_enabled(definition.name)
            if provider.source is state.source:
                winning_provider = provider

        last_modified = (
            winning_provider.get_updated_at(definition.name)
            if winning_provider is not None
            else None
        )

        if state.source is FlagSource.DEFAULT:
            source_provider = _DEFAULT_PROVIDER_NAME
        elif winning_provider is not None:
            source_provider = type(winning_provider).__name__
        else:
            source_provider = _UNKNOWN_PROVIDER_NAME

        env_provider = next(
            (provider for provider in self._providers if isinstance(provider, EnvVarFlagProvider)),
            None,
        )

        return FlagIntrospection(
            name=definition.name,
            description=definition.description,
            current_value=state.enabled,
            source=state.source,
            source_provider=source_provider,
            priority=source_priority(state.source),
            default_value=definition.default,
            last_modified=last_modified,
            environment_var=env_provider.key_for(definition.name) if env_provider else None,
            environment_override=overrides.get(FlagSource.ENV),
            database_override=overrides.get(FlagSource.DATABASE),
            config_override=overrides.get(FlagSource.CONFIG_FILE),
            memory_override=overrides.get(FlagSource.MEMORY),
        )


__all__ = ["FeatureFlagIntrospection"]
