"""Composition root for the feature flag system.

The container is the *only* place that decides how providers are wired. It
builds the default provider chain from configuration:

    ENV  >  MEMORY  >  DATABASE  >  CONFIG_FILE  >  code default

and exposes a singleton ``FeatureFlagService``. Tests and alternate
deployments may pass their own providers (pure constructor injection) and
the container will use them verbatim instead of the defaults.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from sqlalchemy.engine import Engine

from feature_flags.config import FlagConfig, load_flags_yaml
from feature_flags.introspection import FeatureFlagIntrospection
from feature_flags.provider import FlagProvider
from feature_flags.providers.config_file import ConfigFileFlagProvider
from feature_flags.providers.database import DatabaseFlagProvider
from feature_flags.providers.env_var import EnvVarFlagProvider
from feature_flags.providers.memory import MemoryFlagProvider
from feature_flags.service import FeatureFlagService

DEFAULT_FLAGS_PATH = Path("config") / "flags.yaml"


class FeatureFlagContainer:
    """Wires providers and definitions into a ``FeatureFlagService``."""

    def __init__(
        self,
        *,
        flags_path: str | Path | None = None,
        engine: Engine | None = None,
        providers: Sequence[FlagProvider] | None = None,
        strict: bool = False,
        env_prefix: str = "FF_",
    ) -> None:
        self._path = Path(flags_path) if flags_path is not None else DEFAULT_FLAGS_PATH
        self._engine = engine
        self._strict = strict
        self._env_prefix = env_prefix

        flag_config = self._load_config()
        self._memory = MemoryFlagProvider()
        self._providers = (
            list(providers) if providers is not None else self._build_providers(flag_config)
        )
        self._service = FeatureFlagService(
            definitions=flag_config.definitions,
            providers=self._providers,
            strict=strict,
        )

    def _load_config(self) -> FlagConfig:
        if not self._path.exists():
            return FlagConfig(definitions={}, overrides={})
        return load_flags_yaml(self._path)

    def _build_providers(self, config: FlagConfig) -> list[FlagProvider]:
        providers: list[FlagProvider] = [EnvVarFlagProvider(prefix=self._env_prefix)]
        if self._engine is not None:
            providers.append(DatabaseFlagProvider(self._engine))
        if self._path.exists() and config.overrides:
            providers.append(ConfigFileFlagProvider(self._path, section="overrides"))
        providers.append(self._memory)
        return providers

    @property
    def service(self) -> FeatureFlagService:
        """The wired singleton flag service."""
        return self._service

    @property
    def memory(self) -> MemoryFlagProvider:
        return self._memory

    def introspection(self) -> FeatureFlagIntrospection:
        """A read-only introspection view sharing the wired providers.

        ``all_flags()`` on the result lists every flag with its resolved
        value, winning source, priority, and per-source overrides — exactly
        what the same providers evaluate to.
        """
        return FeatureFlagIntrospection(
            definitions=self._service.definitions,
            providers=self._providers,
            strict=self._strict,
        )

    def ensure_schema(self) -> None:
        """Create the feature flag table if a database provider is wired."""
        self._service.ensure_schema()


def build_feature_flags(
    *,
    flags_path: str | Path | None = None,
    engine: Engine | None = None,
    providers: Sequence[FlagProvider] | None = None,
    strict: bool = False,
    env_prefix: str = "FF_",
) -> FeatureFlagService:
    """Convenience builder returning a fully wired ``FeatureFlagService``."""
    return FeatureFlagContainer(
        flags_path=flags_path,
        engine=engine,
        providers=providers,
        strict=strict,
        env_prefix=env_prefix,
    ).service


def build_flag_introspection(
    *,
    flags_path: str | Path | None = None,
    engine: Engine | None = None,
    providers: Sequence[FlagProvider] | None = None,
    strict: bool = False,
    env_prefix: str = "FF_",
) -> FeatureFlagIntrospection:
    """Convenience builder returning a fully wired introspection service."""
    return FeatureFlagContainer(
        flags_path=flags_path,
        engine=engine,
        providers=providers,
        strict=strict,
        env_prefix=env_prefix,
    ).introspection()
