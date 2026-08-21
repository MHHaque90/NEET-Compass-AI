"""
Model Registry Interface - Phase 13
Metadata registry for future models.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from modelling.reliability.gates import ModelLifecycleStage


@dataclass(frozen=True)
class ModelMetadata:
    """
    Complete model metadata for registry.
    DO NOT register an actual production model - registry supports future models.
    """

    model_id: str
    model_name: str
    model_version: str
    dataset_version: str
    feature_version: str
    target_version: str
    training_period: dict[
        str, int
    ]  # {"train_start": 2021, "train_end": 2023, "val_year": 2024, "test_year": 2025}
    validation_period: dict[str, int]
    test_period: dict[str, int]
    algorithm: str
    hyperparameters: dict[str, Any]
    metrics: dict[str, float]
    calibration: dict[str, Any]
    subgroup_metrics: dict[str, dict[str, float]]
    uncertainty_method: str
    training_timestamp: datetime
    code_version: str
    status: ModelLifecycleStage = ModelLifecycleStage.RESEARCH_ONLY
    model_card_path: str | None = None
    leakage_audit_log: str | None = None
    review_report_path: str | None = None
    monitoring_config: dict[str, Any] | None = None

    def __post_init__(self):
        if not self.model_id:
            raise ValueError("model_id is required")
        if not self.model_name:
            raise ValueError("model_name is required")
        if not self.dataset_version:
            raise ValueError("dataset_version is required")


class ModelRegistry:
    """
    Model metadata registry interface.
    Supports future models - DO NOT register actual production model in Sprint 4.0.
    """

    def __init__(self):
        self.models: dict[str, ModelMetadata] = {}

    def register(self, metadata: ModelMetadata) -> None:
        """Register a model."""
        if metadata.model_id in self.models:
            raise ValueError(f"Model already registered: {metadata.model_id}")
        if metadata.status == ModelLifecycleStage.PRODUCTION_READY:
            # In Sprint 4.0, this should never happen
            raise ValueError(
                "Cannot register PRODUCTION_READY model in Sprint 4.0 - training blocked"
            )
        self.models[metadata.model_id] = metadata

    def get_model(self, model_id: str) -> ModelMetadata | None:
        """Get model metadata by ID."""
        return self.models.get(model_id)

    def get_models_by_stage(self, stage: ModelLifecycleStage) -> list[ModelMetadata]:
        """Get all models at a specific lifecycle stage."""
        return [m for m in self.models.values() if m.status == stage]

    def get_models_by_dataset(self, dataset_version: str) -> list[ModelMetadata]:
        """Get all models trained on a specific dataset version."""
        return [m for m in self.models.values() if m.dataset_version == dataset_version]

    def list_all(self) -> list[ModelMetadata]:
        """List all registered models."""
        return list(self.models.values())

    def update_status(self, model_id: str, new_status: ModelLifecycleStage) -> None:
        """Update model lifecycle stage."""
        if model_id not in self.models:
            raise KeyError(f"Model not found: {model_id}")
        # Cannot skip stages
        current = self.models[model_id].status
        stages = list(ModelLifecycleStage)
        current_idx = stages.index(current)
        new_idx = stages.index(new_status)
        if new_idx > current_idx + 1:
            raise ValueError(f"Cannot skip stages: {current.value} -> {new_status.value}")
        # Create new metadata with updated status (immutable)
        old = self.models[model_id]
        new_metadata = ModelMetadata(
            model_id=old.model_id,
            model_name=old.model_name,
            model_version=old.model_version,
            dataset_version=old.dataset_version,
            feature_version=old.feature_version,
            target_version=old.target_version,
            training_period=old.training_period,
            validation_period=old.validation_period,
            test_period=old.test_period,
            algorithm=old.algorithm,
            hyperparameters=old.hyperparameters,
            metrics=old.metrics,
            calibration=old.calibration,
            subgroup_metrics=old.subgroup_metrics,
            uncertainty_method=old.uncertainty_method,
            training_timestamp=old.training_timestamp,
            code_version=old.code_version,
            status=new_status,
            model_card_path=old.model_card_path,
            leakage_audit_log=old.leakage_audit_log,
            review_report_path=old.review_report_path,
            monitoring_config=old.monitoring_config,
        )
        self.models[model_id] = new_metadata

    def verify_provenance(self, model_id: str) -> bool:
        """Verify model provenance traces to dataset and code versions."""
        model = self.get_model(model_id)
        if not model:
            return False
        return bool(model.dataset_version and model.code_version and model.training_timestamp)
