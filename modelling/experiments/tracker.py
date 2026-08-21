"""
Experiment Reproducibility - Phase 14
Experiment metadata structure for reproducible experiments.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ExperimentMetadata:
    """
    Complete experiment metadata for reproducibility.
    An experiment must be reproducible from:
    - dataset identity
    - feature version
    - target version
    - code version
    - random seed
    - configuration
    - model configuration
    """

    experiment_id: str
    experiment_name: str
    dataset_version: str
    feature_version: str
    target_version: str
    code_version: str
    random_seed: int
    configuration: dict[str, Any]
    model_config: dict[str, Any]
    created_timestamp: datetime
    author: str
    description: str
    git_commit: str
    dependencies_hash: str
    dataset_identity: str
    feature_identity: str
    target_identity: str

    def __post_init__(self):
        if not self.experiment_id:
            raise ValueError("experiment_id is required")
        if not self.dataset_version:
            raise ValueError("dataset_version is required")
        if not self.feature_version:
            raise ValueError("feature_version is required")
        if not self.target_version:
            raise ValueError("target_version is required")
        if not self.code_version:
            raise ValueError("code_version is required")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")


@dataclass
class ExperimentTracker:
    """
    Experiment tracker for reproducibility.
    Avoids uncontrolled randomness.
    """

    experiments: dict[str, ExperimentMetadata] = field(default_factory=dict)

    def create_experiment(
        self,
        experiment_name: str,
        dataset_version: str,
        feature_version: str,
        target_version: str,
        code_version: str,
        random_seed: int,
        configuration: dict[str, Any],
        model_config: dict[str, Any],
        author: str,
        description: str,
        git_commit: str,
        dependencies: dict[str, str],
    ) -> ExperimentMetadata:
        """Create a new experiment with deterministic ID."""
        # Compute deterministic experiment ID
        identity_components = {
            "dataset_version": dataset_version,
            "feature_version": feature_version,
            "target_version": target_version,
            "code_version": code_version,
            "random_seed": random_seed,
            "configuration": configuration,
            "model_config": model_config,
            "git_commit": git_commit,
        }
        identity_str = json.dumps(identity_components, sort_keys=True)
        experiment_id = hashlib.sha256(identity_str.encode()).hexdigest()[:16]

        # Compute dependency hash
        deps_str = json.dumps(dependencies, sort_keys=True)
        dependencies_hash = hashlib.sha256(deps_str.encode()).hexdigest()[:16]

        metadata = ExperimentMetadata(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            dataset_version=dataset_version,
            feature_version=feature_version,
            target_version=target_version,
            code_version=code_version,
            random_seed=random_seed,
            configuration=configuration,
            model_config=model_config,
            created_timestamp=datetime.utcnow(),
            author=author,
            description=description,
            git_commit=git_commit,
            dependencies_hash=dependencies_hash,
            dataset_identity=dataset_version,
            feature_identity=feature_version,
            target_identity=target_version,
        )

        if experiment_id in self.experiments:
            existing = self.experiments[experiment_id]
            if existing != metadata:
                raise ValueError(
                    f"Experiment ID collision with different metadata: {experiment_id}"
                )

        self.experiments[experiment_id] = metadata
        return metadata

    def get_experiment(self, experiment_id: str) -> ExperimentMetadata | None:
        """Get experiment by ID."""
        return self.experiments.get(experiment_id)

    def list_experiments(self) -> list[ExperimentMetadata]:
        """List all experiments."""
        return list(self.experiments.values())

    def verify_reproducibility(
        self,
        experiment_id: str,
        current_code_version: str,
        current_dependencies: dict[str, str],
    ) -> dict[str, bool]:
        """Verify experiment can be reproduced with current environment."""
        exp = self.get_experiment(experiment_id)
        if not exp:
            return {"found": False}

        results = {
            "found": True,
            "code_version_match": exp.code_version == current_code_version,
            "dependencies_match": exp.dependencies_hash
            == hashlib.sha256(
                json.dumps(current_dependencies, sort_keys=True).encode()
            ).hexdigest()[:16],
            "dataset_version": exp.dataset_version,
            "feature_version": exp.feature_version,
            "target_version": exp.target_version,
            "random_seed": exp.random_seed,
        }
        results["fully_reproducible"] = all(
            [
                results["code_version_match"],
                results["dependencies_match"],
            ]
        )
        return results
