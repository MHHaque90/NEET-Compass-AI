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
from .human_ingestion import (
    HumanArtifactIngestor,
    IngestionInput,
    IngestionResult,
    ingest_historical_artifact,
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
    "CONTRACT_COMPATIBILITY_VALUES",
    "LIFECYCLE_TRANSITIONS",
    "MINIMUM_VERIFIED_YEARS",
    "PII_BLOCKLIST",
    "PROMOTION_REQUIREMENTS",
    "REQUIRED_PROVENANCE_FIELDS",
    "VALID_PROMOTIONS",
    "ArtifactIntegrity",
    "ArtifactIntegrityResult",
    "ContractCompatibility",
    "ContractGate",
    "ContractGateResult",
    "EvidenceLifecycleStage",
    "EvidenceManifest",
    "EvidenceStatus",
    "HistoricalQualityGateRunner",
    "HistoricalQualityResult",
    "HumanArtifactIngestor",
    "IngestionInput",
    "IngestionResult",
    "ManifestField",
    "PIIGate",
    "PIIGateResult",
    "PromotionStage",
    "PromotionWorkflow",
    "ProvenanceGate",
    "ProvenanceGateResult",
    "TemporalReadinessGate",
    "TemporalReadinessResult",
    "build_source_file_id",
    "can_promote",
    "compute_artifact_hash",
    "compute_temporal_readiness",
    "create_manifest",
    "detect_pii",
    "ingest_historical_artifact",
    "is_blocking_status",
    "is_terminal_status",
    "lifecycle_requires_evidence",
    "requires_manual_intervention",
    "run_historical_quality_gates",
    "validate_contract_compatibility",
    "validate_manifest",
    "validate_no_pii",
    "validate_provenance",
    "validate_transition",
    "verify_artifact_integrity",
]
