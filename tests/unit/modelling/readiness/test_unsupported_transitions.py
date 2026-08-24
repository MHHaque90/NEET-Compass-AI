"""Tests for Unsupported Status Transitions — Sprint 4.1.

Critical assertions:
- NOT_VERIFIED -> READY direct jump FORBIDDEN
- READY_WITH_LIMITATIONS -> READY silent upgrade FORBIDDEN
- All transitions must have evidence
"""

import pytest
from etl.contracts.historical.promotion import (
    PromotionStage,
    PromotionWorkflow,
    VALID_PROMOTIONS,
    PROMOTION_REQUIREMENTS,
    can_promote,
    PromotionResult,
)
from etl.contracts.historical.lifecycle import (
    EvidenceLifecycleStage,
    LIFECYCLE_TRANSITIONS,
    validate_transition,
    lifecycle_requires_evidence,
)


class TestUnsupportedTransitions:
    """Test that unsupported transitions are rejected."""

    def test_not_verified_to_ready_forbidden(self):
        """NOT_VERIFIED -> READY direct jump is forbidden."""
        result = can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.READY, {})
        assert result.allowed is False
        assert "INVALID_TRANSITION" in result.requirements_missing

    def test_not_verified_to_validated_forbidden(self):
        """NOT_VERIFIED -> VALIDATED is forbidden."""
        result = can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.VALIDATED, {})
        assert result.allowed is False

    def test_not_verified_to_ready_limited_forbidden(self):
        """NOT_VERIFIED -> READY_WITH_LIMITATIONS is forbidden."""
        result = can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.READY_WITH_LIMITATIONS, {})
        assert result.allowed is False

    def test_verified_to_ready_forbidden(self):
        """VERIFIED -> READY direct jump is forbidden."""
        result = can_promote(PromotionStage.VERIFIED, PromotionStage.READY, {})
        assert result.allowed is False

    def test_validated_to_ready_forbidden(self):
        """VALIDATED -> READY direct jump is forbidden (must go through READY_WITH_LIMITATIONS)."""
        result = can_promote(PromotionStage.VALIDATED, PromotionStage.READY, {})
        assert result.allowed is False

    def test_ready_limited_to_ready_requires_evidence(self):
        """READY_WITH_LIMITATIONS -> READY requires resolving limitations."""
        # Without evidence
        result = can_promote(PromotionStage.READY_WITH_LIMITATIONS, PromotionStage.READY, {})
        assert result.allowed is False
        assert len(result.requirements_missing) > 0

        # With all evidence
        evidence = {
            "provenance_complete": True,
            "idempotency_verified": True,
            "limitations_resolved": True,
            "temporal_readiness_satisfied": True,
        }
        result = can_promote(PromotionStage.READY_WITH_LIMITATIONS, PromotionStage.READY, evidence)
        assert result.allowed is True

    def test_blocking_stages_are_terminal(self):
        """Blocking stages should have no valid next transitions."""
        for stage in [
            PromotionStage.BLOCKED_DOWNLOAD,
            PromotionStage.BLOCKED_FORMAT,
            PromotionStage.BLOCKED_PII,
            PromotionStage.BLOCKED_CONTRACT,
            PromotionStage.BLOCKED_PROVENANCE,
            PromotionStage.BLOCKED_QUALITY,
        ]:
            assert VALID_PROMOTIONS[stage] == ()

    def test_lifecycle_transitions_require_evidence(self):
        """Valid lifecycle transitions should require evidence."""
        valid_pairs = [
            (EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.SOURCE_VERIFIED),
            (EvidenceLifecycleStage.SOURCE_VERIFIED, EvidenceLifecycleStage.RETRIEVED),
            (EvidenceLifecycleStage.RETRIEVED, EvidenceLifecycleStage.HASHED),
            (EvidenceLifecycleStage.HASHED, EvidenceLifecycleStage.FORMAT_INSPECTED),
            (EvidenceLifecycleStage.FORMAT_INSPECTED, EvidenceLifecycleStage.PII_SCREENED),
            (EvidenceLifecycleStage.PII_SCREENED, EvidenceLifecycleStage.CONTRACT_CHECKED),
            (EvidenceLifecycleStage.CONTRACT_CHECKED, EvidenceLifecycleStage.PARSED),
            (EvidenceLifecycleStage.PARSED, EvidenceLifecycleStage.VALIDATED),
            (EvidenceLifecycleStage.VALIDATED, EvidenceLifecycleStage.PROVENANCE_COMPLETE),
            (EvidenceLifecycleStage.PROVENANCE_COMPLETE, EvidenceLifecycleStage.IDEMPOTENCY_VERIFIED),
            (EvidenceLifecycleStage.IDEMPOTENCY_VERIFIED, EvidenceLifecycleStage.QUALITY_GATES_PASSED),
            (EvidenceLifecycleStage.QUALITY_GATES_PASSED, EvidenceLifecycleStage.MODELLING_READY),
        ]

        for from_stage, to_stage in valid_pairs:
            requires = lifecycle_requires_evidence(from_stage, to_stage)
            assert requires is True, f"Transition {from_stage} -> {to_stage} should require evidence"

    def test_invalid_lifecycle_transition_rejected(self):
        """Invalid lifecycle transitions should be rejected."""
        # DISCOVERED -> MODELLING_READY (skip all intermediate)
        allowed, reason = validate_transition(EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.MODELLING_READY)
        assert allowed is False
        assert "Invalid transition" in reason

        # DISCOVERED -> VALIDATED (skip intermediate)
        allowed, reason = validate_transition(EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.VALIDATED)
        assert allowed is False

    def test_valid_lifecycle_transitions_allowed(self):
        """Valid adjacent lifecycle transitions should be allowed."""
        valid_pairs = [
            (EvidenceLifecycleStage.DISCOVERED, EvidenceLifecycleStage.SOURCE_VERIFIED),
            (EvidenceLifecycleStage.SOURCE_VERIFIED, EvidenceLifecycleStage.RETRIEVED),
            (EvidenceLifecycleStage.RETRIEVED, EvidenceLifecycleStage.HASHED),
            (EvidenceLifecycleStage.HASHED, EvidenceLifecycleStage.FORMAT_INSPECTED),
            (EvidenceLifecycleStage.FORMAT_INSPECTED, EvidenceLifecycleStage.PII_SCREENED),
            (EvidenceLifecycleStage.PII_SCREENED, EvidenceLifecycleStage.CONTRACT_CHECKED),
            (EvidenceLifecycleStage.CONTRACT_CHECKED, EvidenceLifecycleStage.PARSED),
            (EvidenceLifecycleStage.PARSED, EvidenceLifecycleStage.VALIDATED),
            (EvidenceLifecycleStage.VALIDATED, EvidenceLifecycleStage.PROVENANCE_COMPLETE),
            (EvidenceLifecycleStage.PROVENANCE_COMPLETE, EvidenceLifecycleStage.IDEMPOTENCY_VERIFIED),
            (EvidenceLifecycleStage.IDEMPOTENCY_VERIFIED, EvidenceLifecycleStage.QUALITY_GATES_PASSED),
            (EvidenceLifecycleStage.QUALITY_GATES_PASSED, EvidenceLifecycleStage.MODELLING_READY),
        ]

        for from_stage, to_stage in valid_pairs:
            allowed, reason = validate_transition(from_stage, to_stage)
            assert allowed is True, f"{from_stage} -> {to_stage} should be valid: {reason}"

    def test_promotion_requirements_exist_for_non_blocking_stages(self):
        """Every non-blocking promotion stage should have requirements defined."""
        for stage in PromotionStage:
            if stage in [
                PromotionStage.BLOCKED_DOWNLOAD,
                PromotionStage.BLOCKED_FORMAT,
                PromotionStage.BLOCKED_PII,
                PromotionStage.BLOCKED_CONTRACT,
                PromotionStage.BLOCKED_PROVENANCE,
                PromotionStage.BLOCKED_QUALITY,
            ]:
                # Blocking stages have no requirements (terminal)
                continue
            if stage != PromotionStage.READY:
                req = PROMOTION_REQUIREMENTS.get(stage)
                assert req is not None, f"Missing requirements for {stage}"
                assert "requires" in req
                assert "evidence" in req
                assert "next" in req
                assert len(req["requires"]) > 0


class TestPromotionWorkflowReset:
    """Test workflow reset functionality."""

    def test_reset_returns_to_not_verified(self):
        workflow = PromotionWorkflow()
        # Promote to VERIFIED
        workflow.promote(PromotionStage.VERIFIED, {
            "source_authority_verified": True,
            "source_url_accessible": True,
            "source_id_registered": True,
        })
        assert workflow.current_stage == PromotionStage.VERIFIED

        # Reset
        workflow.reset()
        assert workflow.current_stage == PromotionStage.NOT_VERIFIED