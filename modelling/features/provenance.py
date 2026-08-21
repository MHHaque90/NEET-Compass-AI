"""
Feature Provenance - Phase 3 & 8
Tracks the complete lineage of each feature for reproducibility.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FeatureProvenance:
    """
    Complete provenance record for a derived feature.
    Tracks: source records, transformations, versions, timestamps.
    """

    feature_name: str
    feature_version: str
    source_record_ids: list[str]
    source_file_ids: list[str]
    transformation_logic_hash: str
    computation_timestamp: datetime
    computed_by: str
    dependencies: list[str] = field(default_factory=list)
    intermediate_results: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.feature_name:
            raise ValueError("feature_name is required")
        if not self.feature_version:
            raise ValueError("feature_version is required")
        if not self.source_record_ids:
            raise ValueError("source_record_ids cannot be empty")
        if not self.source_file_ids:
            raise ValueError("source_file_ids cannot be empty")
        if not self.transformation_logic_hash:
            raise ValueError("transformation_logic_hash is required")

    @classmethod
    def create(
        cls,
        feature_name: str,
        feature_version: str,
        source_record_ids: list[str],
        source_file_ids: list[str],
        transformation_logic: str,
        computed_by: str = "FeatureEngine",
        dependencies: list[str] | None = None,
        intermediate_results: dict[str, Any] | None = None,
    ) -> "FeatureProvenance":
        """Factory to create provenance with computed hash."""
        logic_hash = hashlib.sha256(transformation_logic.encode()).hexdigest()[:16]
        return cls(
            feature_name=feature_name,
            feature_version=feature_version,
            source_record_ids=sorted(source_record_ids),
            source_file_ids=sorted(source_file_ids),
            transformation_logic_hash=logic_hash,
            computation_timestamp=datetime.utcnow(),
            computed_by=computed_by,
            dependencies=dependencies or [],
            intermediate_results=intermediate_results or {},
        )

    def verify_integrity(self, expected_logic: str) -> bool:
        """Verify the transformation logic matches the stored hash."""
        expected_hash = hashlib.sha256(expected_logic.encode()).hexdigest()[:16]
        return expected_hash == self.transformation_logic_hash


@dataclass(frozen=True)
class FeatureProvenanceSet:
    """
    Complete provenance for all features in a modelling record.
    """

    record_id: str
    dataset_version: str
    feature_version: str
    feature_provenances: dict[str, FeatureProvenance]
    created_timestamp: datetime

    def __post_init__(self):
        if not self.record_id:
            raise ValueError("record_id is required")
        if not self.dataset_version:
            raise ValueError("dataset_version is required")
        if not self.feature_version:
            raise ValueError("feature_version is required")

    def get_all_source_record_ids(self) -> list[str]:
        """Get all unique source record IDs across all features."""
        all_ids = set()
        for prov in self.feature_provenances.values():
            all_ids.update(prov.source_record_ids)
        return sorted(all_ids)

    def get_all_source_file_ids(self) -> list[str]:
        """Get all unique source file IDs across all features."""
        all_ids = set()
        for prov in self.feature_provenances.values():
            all_ids.update(prov.source_file_ids)
        return sorted(all_ids)

    def verify_all(self, transformation_logics: dict[str, str]) -> dict[str, bool]:
        """Verify integrity of all feature provenances."""
        results = {}
        for name, prov in self.feature_provenances.items():
            expected_logic = transformation_logics.get(name, "")
            results[name] = prov.verify_integrity(expected_logic)
        return results
