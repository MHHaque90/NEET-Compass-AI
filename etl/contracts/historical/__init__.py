"""Historical Evidence Acquisition Framework — Sprint 3.9.

This module provides the formal lifecycle for historical source artifacts,
evidence manifest, provenance gates, PII gates, contract compatibility,
artifact integrity, and temporal readiness validation.
"""

from __future__ import annotations

from .artifact_integrity import (
    ArtifactIntegrity,
    ArtifactIntegrityResult,
    build_source_file_id,
    compute_artifact_hash,
    verify_artifact_integrity,
)
from .contract_gate import (
    CONTRACT_COMPATIBILITY_VALUES,
    ContractCompatibility,
    ContractGate,
    ContractGateResult,
    validate_contract_compatibility,
)
from .lifecycle import (
    LIFECYCLE_TRANSITIONS,
    EvidenceLifecycleStage,
    lifecycle_requires_evidence,
    validate_transition,
)
from .manifest import (
    EvidenceManifest,
    ManifestField,
    create_manifest,
    validate_manifest,
)
from .pii_gate import (
    PII_BLOCKLIST,
    PIIGate,
    PIIGateResult,
    detect_pii,
    validate_no_pii,
)
from .promotion import (
    PROMOTION_REQUIREMENTS,
    VALID_PROMOTIONS,
    PromotionStage,
    PromotionWorkflow,
    can_promote,
)
from .provenance_gate import (
    REQUIRED_PROVENANCE_FIELDS,
    ProvenanceGate,
    ProvenanceGateResult,
    validate_provenance,
)
from .quality_gate_integration import (
    HistoricalQualityGateRunner,
    HistoricalQualityResult,
    run_historical_quality_gates,
)
from .status import (
    EvidenceStatus,
    is_blocking_status,
    is_terminal_status,
    requires_manual_intervention,
)
from .temporal_gate import (
    MINIMUM_VERIFIED_YEARS,
    TemporalReadinessGate,
    TemporalReadinessResult,
    compute_temporal_readiness,
)

__all__ = [
    # Lifecycle
    "EvidenceLifecycleStage",
    "LIFECYCLE_TRANSITIONS",
    "validate_transition",
    "lifecycle_requires_evidence",
    # Manifest
    "EvidenceManifest",
    "ManifestField",
    "create_manifest",
    "validate_manifest",
    # Status
    "EvidenceStatus",
    "is_terminal_status",
    "is_blocking_status",
    "requires_manual_intervention",
    # Provenance Gate
    "ProvenanceGate",
    "ProvenanceGateResult",
    "REQUIRED_PROVENANCE_FIELDS",
    "validate_provenance",
    # PII Gate
    "PIIGate",
    "PIIGateResult",
    "PII_BLOCKLIST",
    "detect_pii",
    "validate_no_pii",
    # Artifact Integrity
    "ArtifactIntegrity",
    "ArtifactIntegrityResult",
    "compute_artifact_hash",
    "verify_artifact_integrity",
    "build_source_file_id",
    # Contract Gate
    "ContractCompatibility",
    "ContractGate",
    "ContractGateResult",
    "CONTRACT_COMPATIBILITY_VALUES",
    "validate_contract_compatibility",
    # Quality Gate Integration
    "HistoricalQualityGateRunner",
    "HistoricalQualityResult",
    "run_historical_quality_gates",
    # Temporal Gate
    "TemporalReadinessGate",
    "TemporalReadinessResult",
    "compute_temporal_readiness",
    "MINIMUM_VERIFIED_YEARS",
    # Promotion
    "PromotionStage",
    "PromotionWorkflow",
    "can_promote",
    "PROMOTION_REQUIREMENTS",
    "VALID_PROMOTIONS",
]
