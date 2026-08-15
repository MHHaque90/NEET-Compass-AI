"""Core domain types: categories, contexts, targeting rules, definitions.

These are the vocabulary of the whole flag system. All values are validated
at construction time (Pydantic) so a typo in a flag name or a rule can never
silently reach evaluation.
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FLAG_NAME_PATTERN = r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*$"
_FLAG_NAME_RE = re.compile(FLAG_NAME_PATTERN)


class FlagCategory(StrEnum):
    """Which capability a flag governs.

    Categories keep flags findable and groupable by owner discipline. They
    are metadata for operations/observability — not evaluation logic.
    """

    GENERAL = "GENERAL"
    RULE_ENGINE = "RULE_ENGINE"
    ML_ENGINE = "ML_ENGINE"
    LLM_ENGINE = "LLM_ENGINE"
    EXPERIMENTAL = "EXPERIMENTAL"


class FlagSource(StrEnum):
    """The origin that decided a flag's value, reported on every evaluation."""

    DEFAULT = "DEFAULT"  # the code/config-file baseline
    ENV = "ENV"  # environment variable (highest precedence, kill switch)
    MEMORY = "MEMORY"  # runtime in-process override
    DATABASE = "DATABASE"  # dynamic, real-time toggle without redeploy
    CONFIG_FILE = "CONFIG_FILE"  # YAML overrides shipped with the deploy
    UNKNOWN = "UNKNOWN"  # flag has no definition


class FlagContext(BaseModel):
    """Free-form context consumed by targeting rules.

    ``extra="allow"`` lets callers attach any attribute (``environment``,
    ``request_id``, ``user_id``, …) while still benefiting from Pydantic
    validation of declared fields. The object is frozen once built.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    def get(self, key: str, default: object = None) -> object:
        """Return a context attribute or ``default`` when absent."""
        return getattr(self, key, default)


def _stable_hash(value: str) -> int:
    """Deterministic hash stable across processes and machines.

    Python's built-in ``hash`` is randomized per process (PYTHONHASHSEED),
    which would make percentage rollouts non-deterministic. SHA-256 is used
    so the same key always lands in the same rollout bucket everywhere.
    """
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")


class EnvironmentRule(BaseModel):
    """Matches when ``context.environment`` is one of ``environments``."""

    type: Literal["environment"] = "environment"
    environments: list[str] = Field(min_length=1)

    def matches(self, context: FlagContext) -> bool:
        return context.get("environment") in self.environments


class PercentageRule(BaseModel):
    """Deterministic percentage rollout bucketed by ``context[key]``.

    e.g. ``key="request_id", percentage=10`` enables the flag for ~10% of
    requests, and the same ``request_id`` always gets the same verdict.
    """

    type: Literal["percentage"] = "percentage"
    percentage: int = Field(ge=0, le=100)
    key: str = Field(min_length=1)

    def matches(self, context: FlagContext) -> bool:
        value = context.get(self.key)
        if value is None:
            return False
        return _stable_hash(str(value)) % 100 < self.percentage


class SegmentRule(BaseModel):
    """Matches when ``context[key]`` is a member of ``segments``."""

    type: Literal["segment"] = "segment"
    key: str = Field(min_length=1)
    segments: list[str] = Field(min_length=1)

    def matches(self, context: FlagContext) -> bool:
        return context.get(self.key) in self.segments


Rule = Annotated[
    EnvironmentRule | PercentageRule | SegmentRule,
    Field(discriminator="type"),
]


class FlagDefinition(BaseModel):
    """Declarative description of one feature flag.

    Holds the *baseline* state and targeting rules. The effective state at
    evaluation time is decided by the providers (env / memory / database /
    config file) layered on top of ``default``.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    description: str = ""
    category: FlagCategory = FlagCategory.GENERAL
    default: bool = False
    owner: str = ""
    rules: list[Rule] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        if not _FLAG_NAME_RE.fullmatch(value):
            raise ValueError(f"Invalid flag name {value!r}; expected {FLAG_NAME_PATTERN!r}")
        return value

    @property
    def is_experimental(self) -> bool:
        """True when the flag is explicitly an experimental feature."""
        return self.category == FlagCategory.EXPERIMENTAL


class FlagState(BaseModel):
    """Result of one evaluation: the verdict plus full provenance."""

    name: str
    enabled: bool
    source: FlagSource
    rule_matched: bool | None = Field(
        default=None,
        description="None when the flag has no rules, no context, or was "
        "overridden by an authoritative environment variable.",
    )
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
