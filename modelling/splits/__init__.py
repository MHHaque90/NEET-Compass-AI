"""
Splits Module - Phase 6
Temporal dataset splitting with chronological boundaries.
"""

from modelling.config.modelling_readiness import get_temporal_validation_status
from modelling.splits.engine import SplitResult, TemporalSplitter, TemporalValidationStatus

__all__ = [
    "SplitResult",
    "TemporalSplitter",
    "TemporalValidationStatus",
    "get_temporal_validation_status",
]
