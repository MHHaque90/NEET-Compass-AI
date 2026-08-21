"""
NEET Compass AI - Modelling Engine Foundation
Sprint 4.0: Production-grade modelling infrastructure

This module provides the foundational architecture for future ML modelling
while strictly enforcing reliability gates and temporal validation requirements.

Current state: MODELLING_READY = False (only 1 verified year: MCC 2025)
"""

from modelling.baselines.engine import BaselineEngine, BaselineResult
from modelling.contracts.dataset import (
    DerivedFeatures,
    ModellingDatasetContract,
    ModellingRecord,
    Provenance,
    SourceFacts,
    Targets,
    TemporalMetadata,
)
from modelling.contracts.versioning import (
    DatasetVersion,
    FeatureVersion,
    QualityGateVersion,
    TransformationVersion,
)
from modelling.evaluation.engine import EvaluationEngine, EvaluationResult
from modelling.experiments.tracker import ExperimentMetadata, ExperimentTracker
from modelling.features.engine import FeatureEngine
from modelling.features.provenance import FeatureProvenance
from modelling.features.registry import FeatureRegistry
from modelling.leakage.checker import LeakageChecker, LeakageResult
from modelling.quality.gates import ModellingQualityGates, QualityGateResult
from modelling.registry.interface import ModelMetadata, ModelRegistry
from modelling.reliability.gates import GateResult, ModelLifecycleStage, ReliabilityGate
from modelling.splits.engine import SplitResult, TemporalSplitter, TemporalValidationStatus
from modelling.targets.engine import TargetEngine
from modelling.training.guard import TrainingBlockReason, TrainingGuard
from modelling.uncertainty.engine import AbstentionReason, ConfidenceLevel, UncertaintyEngine

__version__ = "4.0.0"
__sprint__ = "4.0"

# Current modelling readiness (from config/modelling_readiness.yaml)
MODELLING_READY_YEARS = {"MCC": [2025]}
TEMPORAL_VALIDATION_STATUS = "BLOCKED"
TARGET_READINESS = "NO_TARGET_READY"
TRAINING_STATUS = "TRAINING_BLOCKED"
PRODUCTION_MODEL_STATUS = "NOT_READY"

__all__ = [
    # Contracts
    "ModellingDatasetContract",
    "ModellingRecord",
    "SourceFacts",
    "DerivedFeatures",
    "Targets",
    "Provenance",
    "TemporalMetadata",
    # Versioning
    "DatasetVersion",
    "FeatureVersion",
    "TransformationVersion",
    "QualityGateVersion",
    # Features
    "FeatureEngine",
    "FeatureRegistry",
    "FeatureProvenance",
    # Leakage
    "LeakageChecker",
    "LeakageResult",
    # Targets
    "TargetEngine",
    # Splits
    "TemporalSplitter",
    "SplitResult",
    "TemporalValidationStatus",
    # Baselines
    "BaselineEngine",
    "BaselineResult",
    # Evaluation
    "EvaluationEngine",
    "EvaluationResult",
    # Uncertainty
    "UncertaintyEngine",
    "ConfidenceLevel",
    "AbstentionReason",
    # Reliability
    "ReliabilityGate",
    "ModelLifecycleStage",
    "GateResult",
    # Registry
    "ModelRegistry",
    "ModelMetadata",
    # Experiments
    "ExperimentTracker",
    "ExperimentMetadata",
    # Training
    "TrainingGuard",
    "TrainingBlockReason",
    # Quality
    "ModellingQualityGates",
    "QualityGateResult",
    # Status constants
    "MODELLING_READY_YEARS",
    "TEMPORAL_VALIDATION_STATUS",
    "TARGET_READINESS",
    "TRAINING_STATUS",
    "PRODUCTION_MODEL_STATUS",
]
