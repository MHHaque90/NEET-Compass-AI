"""
Leakage Prevention Module - Phase 4
Deterministic leakage detection that fails closed.
"""

from modelling.leakage.checker import (
    LeakageCategory,
    LeakageChecker,
    LeakageResult,
    LeakageViolation,
)

__all__ = [
    "LeakageCategory",
    "LeakageChecker",
    "LeakageResult",
    "LeakageViolation",
]
