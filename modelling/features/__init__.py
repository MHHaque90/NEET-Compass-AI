"""
Features Module - Phase 3 & 8
Feature engineering architecture with registry, engine, and provenance.
"""

from modelling.features.engine import FeatureEngine
from modelling.features.provenance import FeatureProvenance, FeatureProvenanceSet
from modelling.features.registry import FeatureRegistry
from modelling.features.types import FeatureDefinition, LeakageStatus, TemporalAvailability

__all__ = [
    "FeatureDefinition",
    "FeatureEngine",
    "FeatureProvenance",
    "FeatureProvenanceSet",
    "FeatureRegistry",
    "LeakageStatus",
    "TemporalAvailability",
]
