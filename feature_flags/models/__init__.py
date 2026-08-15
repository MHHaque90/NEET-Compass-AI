"""Domain types for the feature flag system (package).

Split into ``definition`` (the flag vocabulary) and ``introspection``
(read-only observability snapshots) with a single re-export surface so the
original ``from feature_flags.models import ...`` imports keep working
unchanged.
"""

from feature_flags.models.definition import (
    FLAG_NAME_PATTERN,
    EnvironmentRule,
    FlagCategory,
    FlagContext,
    FlagDefinition,
    FlagSource,
    FlagState,
    PercentageRule,
    Rule,
    SegmentRule,
)
from feature_flags.models.introspection import (
    FlagIntrospection,
    FlagIntrospectionReport,
)

__all__ = [
    "FLAG_NAME_PATTERN",
    "EnvironmentRule",
    "FlagCategory",
    "FlagContext",
    "FlagDefinition",
    "FlagIntrospection",
    "FlagIntrospectionReport",
    "FlagSource",
    "FlagState",
    "PercentageRule",
    "Rule",
    "SegmentRule",
]
