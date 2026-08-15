"""Introspection models: read-only snapshots of the flag catalogue.

These are pure data records produced by ``FeatureFlagIntrospection``. They
carry the *why* of every flag — the resolved value, the winning source, its
priority, and each source's own override — so operators can audit the system
without touching the evaluation path. No business or prediction logic lives
here.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from feature_flags.models.definition import FlagSource


class FlagIntrospection(BaseModel):
    """One flag's complete current state plus per-source provenance.

    ``current_value`` is the resolved verdict (what ``is_enabled`` would
    return); ``source`` and ``priority`` identify *why* it won. The
    ``*_override`` fields report each lower-level source's own value, so a
    flag that is "on" can always be traced to the override that did it.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    current_value: bool
    source: FlagSource
    source_provider: str
    priority: int
    default_value: bool
    last_modified: datetime | None
    environment_var: str | None
    environment_override: bool | None
    database_override: bool | None
    config_override: bool | None
    memory_override: bool | None


class FlagIntrospectionReport(BaseModel):
    """Ordered snapshot of the whole flag catalogue.

    ``flags`` is sorted by flag name (deterministic, mirroring
    ``FeatureFlagService.all_states``); ``generated_at`` records when the
    snapshot was taken; ``total`` is derived from the flag list.
    """

    model_config = ConfigDict(frozen=True)

    flags: list[FlagIntrospection]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total(self) -> int:
        """Number of flags in the snapshot."""
        return len(self.flags)
