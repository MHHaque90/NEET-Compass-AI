"""
Dataset Versioning - Phase 7 & 8
Deterministic identity for modelling datasets, features, and quality gates.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DatasetVersion:
    """
    Modelling dataset version identity.
    Deterministic from: source_file_ids + transformation_version + feature_version + quality_gate_version
    """

    version: str
    created_timestamp: datetime
    source_file_ids: list[str]
    source_checksums: dict[str, str]
    transformation_version: str
    feature_version: str
    quality_gate_version: str
    quality_gate_results: dict[str, any]
    row_count: int
    column_count: int
    year_range: tuple[int, int]
    authorities: list[str]
    target_variables: list[str]
    schema_hash: str
    modelling_ready: bool = False
    temporal_validation_blocked: bool = True
    target_readiness: str = "NO_TARGET_READY"

    @classmethod
    def create(
        cls,
        source_file_ids: list[str],
        source_checksums: dict[str, str],
        transformation_version: str,
        feature_version: str,
        quality_gate_version: str,
        quality_gate_results: dict[str, any],
        row_count: int,
        column_count: int,
        year_range: tuple[int, int],
        authorities: list[str],
        target_variables: list[str],
        schema_hash: str,
        modelling_ready: bool = False,
        temporal_validation_blocked: bool = True,
        target_readiness: str = "NO_TARGET_READY",
    ) -> "DatasetVersion":
        """Factory method to create a new dataset version with computed identity."""
        version = cls._compute_version(
            source_file_ids,
            transformation_version,
            feature_version,
            quality_gate_version,
        )
        return cls(
            version=version,
            created_timestamp=datetime.now(UTC),
            source_file_ids=sorted(source_file_ids),
            source_checksums=source_checksums,
            transformation_version=transformation_version,
            feature_version=feature_version,
            quality_gate_version=quality_gate_version,
            quality_gate_results=quality_gate_results,
            row_count=row_count,
            column_count=column_count,
            year_range=year_range,
            authorities=sorted(authorities),
            target_variables=sorted(target_variables),
            schema_hash=schema_hash,
            modelling_ready=modelling_ready,
            temporal_validation_blocked=temporal_validation_blocked,
            target_readiness=target_readiness,
        )

    @staticmethod
    def _compute_version(
        source_file_ids: list[str],
        transformation_version: str,
        feature_version: str,
        quality_gate_version: str,
    ) -> str:
        """Compute deterministic dataset version."""
        sorted_ids = "|".join(sorted(source_file_ids))
        components = (
            f"{sorted_ids}|{transformation_version}|{feature_version}|{quality_gate_version}"
        )
        return hashlib.sha256(components.encode()).hexdigest()[:16]

    def verify_identity(self) -> bool:
        """Verify this version matches its declared components."""
        expected = self._compute_version(
            self.source_file_ids,
            self.transformation_version,
            self.feature_version,
            self.quality_gate_version,
        )
        return expected == self.version


@dataclass(frozen=True)
class FeatureVersion:
    """
    Explicit feature version metadata.
    A feature change MUST produce a new version.
    """

    version: str
    created_timestamp: datetime
    feature_definitions: dict[str, dict[str, any]]
    feature_computation_code_hash: str
    changed_from_previous: list[str] = field(default_factory=list)
    deprecated_features: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        version: str,
        feature_definitions: dict[str, dict[str, any]],
        feature_computation_code_hash: str,
        changed_from_previous: list[str] | None = None,
        deprecated_features: list[str] | None = None,
    ) -> "FeatureVersion":
        return cls(
            version=version,
            created_timestamp=datetime.now(UTC),
            feature_definitions=feature_definitions,
            feature_computation_code_hash=feature_computation_code_hash,
            changed_from_previous=changed_from_previous or [],
            deprecated_features=deprecated_features or [],
        )


@dataclass(frozen=True)
class TransformationVersion:
    """
    Dataset transformation logic version.
    Increment on ANY change to aggregation, join logic, missing value handling, etc.
    """

    version: str
    created_timestamp: datetime
    aggregation_logic_hash: str
    join_logic_hash: str
    missing_value_handling_hash: str
    changed_from_previous: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        version: str,
        aggregation_logic_hash: str,
        join_logic_hash: str,
        missing_value_handling_hash: str,
        changed_from_previous: list[str] | None = None,
    ) -> "TransformationVersion":
        return cls(
            version=version,
            created_timestamp=datetime.now(UTC),
            aggregation_logic_hash=aggregation_logic_hash,
            join_logic_hash=join_logic_hash,
            missing_value_handling_hash=missing_value_handling_hash,
            changed_from_previous=changed_from_previous or [],
        )


@dataclass(frozen=True)
class QualityGateVersion:
    """
    Quality gate thresholds and logic version.
    Increment on ANY change to gate thresholds, logic, or classification criteria.
    """

    version: str
    created_timestamp: datetime
    gate_thresholds_hash: str
    gate_logic_hash: str
    classification_criteria_hash: str
    changed_from_previous: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        version: str,
        gate_thresholds_hash: str,
        gate_logic_hash: str,
        classification_criteria_hash: str,
        changed_from_previous: list[str] | None = None,
    ) -> "QualityGateVersion":
        return cls(
            version=version,
            created_timestamp=datetime.now(UTC),
            gate_thresholds_hash=gate_thresholds_hash,
            gate_logic_hash=gate_logic_hash,
            classification_criteria_hash=classification_criteria_hash,
            changed_from_previous=changed_from_previous or [],
        )
