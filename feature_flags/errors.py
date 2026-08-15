"""Feature flag exceptions.

Thin, typed errors so failures are unambiguous at the caller: an unknown
flag, a malformed toggle value, a configuration problem, or a disabled
capability are all distinguishable and can be handled (or surfaced) by name.
"""


class FeatureFlagError(Exception):
    """Base class for all feature flag system errors."""


class UnknownFlagError(FeatureFlagError):
    """A flag that has no definition was evaluated in strict mode."""


class MalformedFlagValueError(FeatureFlagError):
    """A provider returned a value that cannot be interpreted as a boolean."""


class FlagConfigurationError(FeatureFlagError):
    """Feature flag configuration (file, schema, wiring) is invalid."""


class FeatureDisabledError(FeatureFlagError):
    """A capability gate was required but the feature flag is disabled."""

    def __init__(self, flag_name: str) -> None:
        self.flag_name = flag_name
        super().__init__(f"Feature flag {flag_name!r} is disabled")
