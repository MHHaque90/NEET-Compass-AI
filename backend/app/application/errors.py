"""Application-layer exceptions.

Thin, domain-specific error types so services can fail expressively without
leaking framework concerns. The API layer maps these to HTTP responses.
"""


class ApplicationError(Exception):
    """Base class for all application-layer errors."""


class CandidateValidationError(ApplicationError, ValueError):
    """Candidate input failed domain validation."""


class CollegeNotFoundError(ApplicationError):
    """A referenced college does not exist in the master catalog."""


class RecommendationEngineNotConfigured(ApplicationError):
    """No scoring engine is registered for the configured backend name."""


class PredictionUnavailable(ApplicationError):
    """An engine could not produce a score (no data / not supported)."""
