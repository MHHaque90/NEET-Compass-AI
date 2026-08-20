"""Historical Evidence Lifecycle — Sprint 3.9.

Formal lifecycle for a historical source artifact. Every transition
must have evidence. A document existing on an official website must NOT
automatically move through the lifecycle.
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class EvidenceLifecycleStage(str, Enum):
    """Lifecycle stages for a historical source artifact.

    Each stage represents a verified gate. Transitions require evidence.
    """

    # Stage 0: Source discovered but not yet verified
    DISCOVERED = "DISCOVERED"

    # Stage 1: Source authority and URL verified
    SOURCE_VERIFIED = "SOURCE_VERIFIED"

    # Stage 2: Artifact successfully retrieved
    RETRIEVED = "RETRIEVED"

    # Stage 3: SHA-256 checksum computed and recorded
    HASHED = "HASHED"

    # Stage 4: Format inspected (column headers, structure recorded)
    FORMAT_INSPECTED = "FORMAT_INSPECTED"

    # Stage 5: PII screening completed
    PII_SCREENED = "PII_SCREENED"

    # Stage 6: Contract compatibility checked
    CONTRACT_CHECKED = "CONTRACT_CHECKED"

    # Stage 7: Parsed through canonical adapter
    PARSED = "PARSED"

    # Stage 8: Validated against data quality gates
    VALIDATED = "VALIDATED"

    # Stage 9: Complete provenance recorded
    PROVENANCE_COMPLETE = "PROVENANCE_COMPLETE"

    # Stage 10: Idempotency verified (re-ingestion produces same results)
    IDEMPOTENCY_VERIFIED = "IDEMPOTENCY_VERIFIED"

    # Stage 11: All quality gates passed
    QUALITY_GATES_PASSED = "QUALITY_GATES_PASSED"

    # Stage 12: Modelling ready
    MODELLING_READY = "MODELLING_READY"

    # Terminal blocking states
    BLOCKED_AUTOMATED_DOWNLOAD = "BLOCKED_AUTOMATED_DOWNLOAD"
    BLOCKED_FORMAT_INCOMPATIBLE = "BLOCKED_FORMAT_INCOMPATIBLE"
    BLOCKED_PII_DETECTED = "BLOCKED_PII_DETECTED"
    BLOCKED_CONTRACT_INCOMPATIBLE = "BLOCKED_CONTRACT_INCOMPATIBLE"
    BLOCKED_PROVENANCE_INCOMPLETE = "BLOCKED_PROVENANCE_INCOMPLETE"
    BLOCKED_QUALITY_GATES_FAILED = "BLOCKED_QUALITY_GATES_FAILED"


# Valid lifecycle transitions. Each transition MUST have evidence.
# Format: (from_stage, to_stage) -> required_evidence_description
LIFECYCLE_TRANSITIONS: Final[dict[tuple[EvidenceLifecycleStage, EvidenceLifecycleStage], str]] = {
    (EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.SOURCE_VERIFIED):
        "Official source authority confirmed; URL accessible (HTTP 200); source_id registered in data_sources.yaml",

    (EvidenceLifecycleStage.SOURCE_VERIFIED, EvidenceLifecycleStage.RETRIEVED):
        "File downloaded successfully; HTTP 200 response; retrieval_timestamp recorded; retrieval_method documented",

    (EvidenceLifecycleStage.SOURCE_VERIFIED, EvidenceLifecycleStage.BLOCKED_AUTOMATED_DOWNLOAD):
        "Automated download returned HTTP 403/429; bot protection confirmed; manual retrieval path documented",

    (EvidenceLifecycleStage.RETRIEVED, EvidenceLifecycleStage.HASHED):
        "SHA-256 checksum computed from file bytes; checksum recorded in provenance; source_file_id generated",

    (EvidenceLifecycleStage.HASHED, EvidenceLifecycleStage.FORMAT_INSPECTED):
        "Column headers/schema documented; data types recorded; sample rows inspected; format_status recorded",

    (EvidenceLifecycleStage.FORMAT_INSPECTED, EvidenceLifecycleStage.PII_SCREENED):
        "PII blocklist applied to all columns; PII status recorded (CLEAR/DETECTED/EXCLUDED); no candidate identifiers in canonical path",

    (EvidenceLifecycleStage.PII_SCREENED, EvidenceLifecycleStage.CONTRACT_CHECKED):
        "Contract version identified; column mapping verified; category/quota codes mapped; compatibility classification assigned",

    (EvidenceLifecycleStage.PII_SCREENED, EvidenceLifecycleStage.BLOCKED_PII_DETECTED):
        "PII columns detected in source; source documented as PII_BEARING; excluded from canonical modelling path",

    (EvidenceLifecycleStage.CONTRACT_CHECKED, EvidenceLifecycleStage.PARSED):
        "Source parsed through existing adapter; canonical records produced; adapter validation passed",

    (EvidenceLifecycleStage.CONTRACT_CHECKED, EvidenceLifecycleStage.BLOCKED_CONTRACT_INCOMPATIBLE):
        "Contract compatibility = INCOMPATIBLE; format differences documented; new contract version required but not created",

    (EvidenceLifecycleStage.CONTRACT_CHECKED, EvidenceLifecycleStage.BLOCKED_FORMAT_INCOMPATIBLE):
        "Format inspection revealed structural incompatibility; cannot parse with existing contracts",

    (EvidenceLifecycleStage.PARSED, EvidenceLifecycleStage.VALIDATED):
        "All 15 data quality gates executed; gate results recorded; classification assigned (READY/READY_WITH_LIMITATIONS/NOT_READY)",

    (EvidenceLifecycleStage.VALIDATED, EvidenceLifecycleStage.PROVENANCE_COMPLETE):
        "All 10 required provenance fields present; SourceMetadata complete for all records; checksum chain verified",

    (EvidenceLifecycleStage.PROVENANCE_COMPLETE, EvidenceLifecycleStage.IDEMPOTENCY_VERIFIED):
        "Re-ingestion of same file produces identical canonical records; checksum short-circuit works; logical uniqueness enforced",

    (EvidenceLifecycleStage.IDEMPOTENCY_VERIFIED, EvidenceLifecycleStage.QUALITY_GATES_PASSED):
        "All critical quality gates pass; classification = READY or READY_WITH_LIMITATIONS; no gate silently overridden",

    (EvidenceLifecycleStage.QUALITY_GATES_PASSED, EvidenceLifecycleStage.MODELLING_READY):
        "Temporal readiness gate passed; minimum verified years satisfied; promotion workflow completed; modelling_readiness.yaml updated",
}


def validate_transition(
    from_stage: str | EvidenceLifecycleStage,
    to_stage: str | EvidenceLifecycleStage,
) -> tuple[bool, str]:
    """Validate that a lifecycle transition is permitted.

    Args:
        from_stage: Current lifecycle stage (enum or string).
        to_stage: Proposed next stage (enum or string).

    Returns:
        Tuple of (is_valid, evidence_requirement_description).

    """
    from_stage_str = from_stage.value if isinstance(from_stage, EvidenceLifecycleStage) else from_stage
    to_stage_str = to_stage.value if isinstance(to_stage, EvidenceLifecycleStage) else to_stage

    key = (EvidenceLifecycleStage(from_stage_str) if isinstance(from_stage_str, str) else from_stage_str,
           EvidenceLifecycleStage(to_stage_str) if isinstance(to_stage_str, str) else to_stage_str)

    if key in LIFECYCLE_TRANSITIONS:
        return True, LIFECYCLE_TRANSITIONS[key]
    return False, f"Invalid transition: {from_stage_str} -> {to_stage_str}"


def lifecycle_requires_evidence(
    from_stage: EvidenceLifecycleStage,
    to_stage: EvidenceLifecycleStage,
) -> bool:
    """Check if a transition requires documented evidence.

    ALL transitions require evidence. This function always returns True
    for valid transitions to enforce the principle.
    """
    valid, _ = validate_transition(from_stage, to_stage)
    return valid
