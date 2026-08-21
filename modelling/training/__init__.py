"""
Training Module - Phase 15
Safe model training guard - IMPOSSIBLE TO BYPASS.
"""

from modelling.training.guard import (
    TrainingBlockReason,
    TrainingGuard,
    TrainingGuardResult,
    TrainingResult,
    get_training_guard,
)

__all__ = [
    "TrainingBlockReason",
    "TrainingGuard",
    "TrainingGuardResult",
    "TrainingResult",
    "get_training_guard",
]
