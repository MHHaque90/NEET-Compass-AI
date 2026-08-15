"""Flag evaluation: source precedence and targeting-rule pipeline.

Precedence is declared by source type — not by provider registration order —
so the behaviour is stable no matter who wires the container:

    ENV  >  MEMORY  >  DATABASE  >  CONFIG_FILE  >  DEFAULT (code baseline)

The first provider that owns the flag (returns a non-``None`` value) wins.
Environment variables are treated as *authoritative kill switches*: their
value bypasses targeting rules so an incident response can force-disable a
feature globally without reasoning about rules. Every other source's value
is narrowed by the flag's targeting rules when a context is supplied.
"""

from __future__ import annotations

from collections.abc import Sequence

from feature_flags.models import FlagContext, FlagDefinition, FlagSource, FlagState
from feature_flags.provider import FlagProvider

SOURCE_PRECEDENCE: dict[FlagSource, int] = {
    FlagSource.ENV: 0,
    FlagSource.MEMORY: 1,
    FlagSource.DATABASE: 2,
    FlagSource.CONFIG_FILE: 3,
    FlagSource.DEFAULT: 4,
    FlagSource.UNKNOWN: 5,
}


def source_priority(source: FlagSource) -> int:
    """Return the precedence rank of a source (lower wins first).

    Providers only ever report the four override sources; ``DEFAULT`` and
    ``UNKNOWN`` are included so introspection can rank every possible
    winning source on the same scale.
    """
    return SOURCE_PRECEDENCE.get(source, SOURCE_PRECEDENCE[FlagSource.UNKNOWN])


def evaluate(
    definition: FlagDefinition,
    providers: Sequence[FlagProvider],
    context: FlagContext | None,
) -> FlagState:
    """Resolve a definition against the provider chain and return a verdict."""
    enabled, source = _resolve_base(definition, providers)
    rule_matched: bool | None = None

    # Authoritative kill switch: env wins without targeting.
    if source is not FlagSource.ENV and definition.rules:
        if context is None:
            rule_matched = None
        else:
            rule_matched = all(rule.matches(context) for rule in definition.rules)
            enabled = enabled and rule_matched

    return FlagState(
        name=definition.name,
        enabled=enabled,
        source=source,
        rule_matched=rule_matched,
    )


def _resolve_base(
    definition: FlagDefinition,
    providers: Sequence[FlagProvider],
) -> tuple[bool, FlagSource]:
    ranked = sorted(
        (provider for provider in providers if provider.source in SOURCE_PRECEDENCE),
        key=lambda provider: SOURCE_PRECEDENCE[provider.source],
    )
    for provider in ranked:
        value = provider.get_enabled(definition.name)
        if value is not None:
            return value, provider.source
    return definition.default, FlagSource.DEFAULT
