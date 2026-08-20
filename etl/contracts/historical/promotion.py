"""Promotion Workflow — Sprint 3.9.

Deterministic promotion workflow for historical datasets.

Example:
NOT_VERIFIED -> VERIFIED -> VALIDATED -> READY_WITH_LIMITATIONS -> READY

A dataset must NEVER jump directly from NOT_VERIFIED -> READY
without passing the required gates.

READY_WITH_LIMITATIONS must not silently become READY
without satisfying the missing conditions.

"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PromotionStage(str, Enum):
    """Promotion stages for historical datasets."""

    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    VALIDATED = "VALIDATED"
    READY_WITH_LIMITATIONS = "READY_WITH_LIMITATIONS"
    READY = "READY"

    # Blocking stages
    BLOCKED_DOWNLOAD = "BLOCKED_DOWNLOAD"
    BLOCKED_FORMAT = "BLOCKED_FORMAT"
    BLOCKED_PII = "BLOCKED_PII"
    BLOCKED_CONTRACT = "BLOCKED_CONTRACT"
    BLOCKED_PROVENANCE = "BLOCKED_PROVENANCE"
    BLOCKED_QUALITY = "BLOCKED_QUALITY"


# Promotion requirements: what must be true to advance
PROMOTION_REQUIREMENTS: dict[PromotionStage, dict[str, Any]] = {
    PromotionStage.NOT_VERIFIED: {
        "next": PromotionStage.VERIFIED,
        "requires": [
            "source_authority_verified",
            "source_url_accessible",
            "source_id_registered",
        ],
        "evidence": "Official source confirmed; URL returns HTTP 200",
    },
    PromotionStage.VERIFIED: {
        "next": PromotionStage.VALIDATED,
        "requires": [
            "artifact_retrieved",
            "checksum_recorded",
            "format_inspected",
            "pii_screened",
        ],
        "evidence": "File downloaded; SHA-256 computed; schema documented; PII status known",
    },
    PromotionStage.VALIDATED: {
        "next": PromotionStage.READY_WITH_LIMITATIONS,
        "requires": [
            "contract_compatible",
            "parsed_through_adapter",
            "quality_gates_executed",
        ],
        "evidence": "Contract compatibility confirmed; canonical records produced; 15 gates run",
    },
    PromotionStage.READY_WITH_LIMITATIONS: {
        "next": PromotionStage.READY,
        "requires": [
            "provenance_complete",
            "idempotency_verified",
            "limitations_resolved",
            "temporal_readiness_satisfied",
        ],
        "evidence": "All 10 provenance fields; re-ingestion idempotent; limitations addressed; temporal split possible",
    },
    PromotionStage.READY: {
        "next": None,
        "requires": [],
        "evidence": "All gates passed; modelling_readiness.yaml updated; temporal validation unblocked",
    },
}


# Valid promotion transitions (no skipping!)
VALID_PROMOTIONS: dict[PromotionStage, tuple[PromotionStage, ...]] = {
    PromotionStage.NOT_VERIFIED: (PromotionStage.VERIFIED,),
    PromotionStage.VERIFIED: (PromotionStage.VALIDATED, PromotionStage.BLOCKED_DOWNLOAD),
    PromotionStage.VALIDATED: (PromotionStage.READY_WITH_LIMITATIONS,
                                PromotionStage.BLOCKED_FORMAT,
                                PromotionStage.BLOCKED_PII,
                                PromotionStage.BLOCKED_CONTRACT,
                                PromotionStage.BLOCKED_PROVENANCE),
    PromotionStage.READY_WITH_LIMITATIONS: (PromotionStage.READY, PromotionStage.BLOCKED_QUALITY),
    PromotionStage.READY: (),
    # Blocking stages are terminal
    PromotionStage.BLOCKED_DOWNLOAD: (),
    PromotionStage.BLOCKED_FORMAT: (),
    PromotionStage.BLOCKED_PII: (),
    PromotionStage.BLOCKED_CONTRACT: (),
    PromotionStage.BLOCKED_PROVENANCE: (),
    PromotionStage.BLOCKED_QUALITY: (),
}


@dataclass(frozen=True)
class PromotionResult:
    """Result of a promotion attempt."""

    allowed: bool
    from_stage: PromotionStage
    to_stage: PromotionStage
    requirements_met: tuple[str, ...]
    requirements_missing: tuple[str, ...]
    evidence_required: str


class PromotionWorkflow:
    """Manages deterministic promotion of historical datasets."""

    def __init__(self) -> None:
        self.current_stage = PromotionStage.NOT_VERIFIED

    def can_promote(
        self,
        from_stage: PromotionStage,
        to_stage: PromotionStage,
        evidence: dict[str, bool] | None = None,
    ) -> PromotionResult:
        """Check if promotion is allowed with given evidence.

        Args:
            from_stage: Current promotion stage.
            to_stage: Desired next stage.
            evidence: Dict of requirement -> satisfied (True/False).

        Returns:
            PromotionResult with allowance and details.

        """
        evidence = evidence or {}

        # Check if transition is valid
        valid_next = VALID_PROMOTIONS.get(from_stage, ())
        if to_stage not in valid_next:
            return PromotionResult(
                allowed=False,
                from_stage=from_stage,
                to_stage=to_stage,
                requirements_met=(),
                requirements_missing=("INVALID_TRANSITION",),
                evidence_required=f"Cannot promote from {from_stage.value} to {to_stage.value}",
            )

        # Check requirements
        requirements = PROMOTION_REQUIREMENTS.get(from_stage, {}).get("requires", [])
        met = [req for req in requirements if evidence.get(req, False)]
        missing = [req for req in requirements if not evidence.get(req, False)]

        allowed = len(missing) == 0
        evidence_req = PROMOTION_REQUIREMENTS.get(from_stage, {}).get("evidence", "")

        return PromotionResult(
            allowed=allowed,
            from_stage=from_stage,
            to_stage=to_stage,
            requirements_met=tuple(met),
            requirements_missing=tuple(missing),
            evidence_required=evidence_req,
        )

    def promote(
        self,
        to_stage: PromotionStage,
        evidence: dict[str, bool],
    ) -> PromotionResult:
        """Attempt to promote to the next stage."""
        result = self.can_promote(self.current_stage, to_stage, evidence)
        if result.allowed:
            self.current_stage = to_stage
        return result

    def reset(self) -> None:
        """Reset to initial stage."""
        self.current_stage = PromotionStage.NOT_VERIFIED


def can_promote(
    from_stage: PromotionStage,
    to_stage: PromotionStage,
    evidence: dict[str, bool] | None = None,
) -> PromotionResult:
    """Convenience function to check promotion eligibility."""
    workflow: PromotionWorkflow = PromotionWorkflow()
    workflow.current_stage = from_stage
    return workflow.can_promote(from_stage, to_stage, evidence)
