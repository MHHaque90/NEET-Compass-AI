"""Tests for Historical Artifact Promotion Workflow — Sprint 4.1.

Critical assertions:
- NOT_VERIFIED -> READY direct jump is FORBIDDEN
- READY_WITH_LIMITATIONS -> READY silent upgrade is FORBIDDEN
- Valid promotion requires evidence at each stage
- Blocking transitions are terminal and require evidence
"""

import pytest
from etl.contracts.historical.promotion import (
    PromotionStage,
    PromotionWorkflow,
    VALID_PROMOTIONS,
    PROMOTION_REQUIREMENTS,
    PromotionResult,
    can_promote,
)


class TestPromotionWorkflow:
    """Test the deterministic promotion workflow."""

    def test_initial_stage(self):
        workflow = PromotionWorkflow()
        assert workflow.current_stage == PromotionStage.NOT_VERIFIED

    def test_valid_promotion_not_verified_to_verified(self):
        workflow = PromotionWorkflow()
        evidence = {
            "source_authority_verified": True,
            "source_url_accessible": True,
            "source_id_registered": True,
        }
        result = workflow.promote(PromotionStage.VERIFIED, evidence)
        assert result.allowed is True
        assert workflow.current_stage == PromotionStage.VERIFIED

    def test_invalid_direct_jump_not_verified_to_ready(self):
        """FORBIDDEN: NOT_VERIFIED -> READY direct jump."""
        workflow = PromotionWorkflow()
        result = workflow.can_promote(PromotionStage.NOT_VERIFIED, PromotionStage.READY, {})
        assert result.allowed is False
        assert "INVALID_TRANSITION" in result.requirements_missing

    def test_invalid_silent_upgrade_ready_limited_to_ready(self):
        """FORBIDDEN: READY_WITH_LIMITATIONS -> READY without resolving limitations."""
        workflow = PromotionWorkflow()
        workflow.current_stage = PromotionStage.READY_WITH_LIMITATIONS
        result = workflow.can_promote(
            PromotionStage.READY_WITH_LIMITATIONS, PromotionStage.READY, {}
        )
        assert result.allowed is False
        assert len(result.requirements_missing) > 0

    def test_blocked_download_transition_requires_evidence(self):
        """VERIFIED -> BLOCKED_DOWNLOAD requires evidence for VERIFIED stage."""
        result = can_promote(PromotionStage.VERIFIED, PromotionStage.BLOCKED_DOWNLOAD, {})
        assert result.allowed is False

    def test_blocked_format_transition_requires_evidence(self):
        """VALIDATED -> BLOCKED_FORMAT requires VALIDATED evidence."""
        result = can_promote(PromotionStage.VALIDATED, PromotionStage.BLOCKED_FORMAT, {})
        assert result.allowed is False

    def test_blocked_pii_transition_requires_evidence(self):
        """VALIDATED -> BLOCKED_PII requires VALIDATED evidence."""
        result = can_promote(PromotionStage.VALIDATED, PromotionStage.BLOCKED_PII, {})
        assert result.allowed is False

    def test_blocked_contract_transition_requires_evidence(self):
        """VALIDATED -> BLOCKED_CONTRACT requires VALIDATED evidence."""
        result = can_promote(PromotionStage.VALIDATED, PromotionStage.BLOCKED_CONTRACT, {})
        assert result.allowed is False

    def test_blocked_provenance_transition_requires_evidence(self):
        """VALIDATED -> BLOCKED_PROVENANCE requires VALIDATED evidence."""
        result = can_promote(PromotionStage.VALIDATED, PromotionStage.BLOCKED_PROVENANCE, {})
        assert result.allowed is False

    def test_blocked_quality_transition_requires_evidence(self):
        """READY_WITH_LIMITATIONS -> BLOCKED_QUALITY requires READY_WITH_LIMITATIONS evidence."""
        result = can_promote(PromotionStage.READY_WITH_LIMITATIONS, PromotionStage.BLOCKED_QUALITY, {})
        assert result.allowed is False

    def test_valid_promotions_mapping_complete(self):
        """Every non-blocking stage should have valid next stages defined."""
        for stage in PromotionStage:
            if stage in [
                PromotionStage.BLOCKED_DOWNLOAD,
                PromotionStage.BLOCKED_FORMAT,
                PromotionStage.BLOCKED_PII,
                PromotionStage.BLOCKED_CONTRACT,
                PromotionStage.BLOCKED_PROVENANCE,
                PromotionStage.BLOCKED_QUALITY,
            ]:
                assert VALID_PROMOTIONS[stage] == ()
            elif stage != PromotionStage.READY:
                assert len(VALID_PROMOTIONS[stage]) > 0

    def test_promotion_requirements_exist(self):
        """Each non-blocking promotion stage should have requirements defined."""
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
                req = PROMOTION_REQUIREMENTS.get(stage, {})
                assert "requires" in req, f"Missing 'requires' for {stage}"
                assert "evidence" in req, f"Missing 'evidence' for {stage}"
                assert len(req["requires"]) > 0, f"Empty requires for {stage}"

    def test_full_promotion_path_with_evidence(self):
        """Test complete valid promotion path with all evidence."""
        workflow = PromotionWorkflow()

        # NOT_VERIFIED -> VERIFIED
        result = workflow.promote(PromotionStage.VERIFIED, {
            "source_authority_verified": True,
            "source_url_accessible": True,
            "source_id_registered": True,
        })
        assert result.allowed is True

        # VERIFIED -> VALIDATED
        result = workflow.promote(PromotionStage.VALIDATED, {
            "artifact_retrieved": True,
            "checksum_recorded": True,
            "format_inspected": True,
            "pii_screened": True,
        })
        assert result.allowed is True

        # VALIDATED -> READY_WITH_LIMITATIONS
        result = workflow.promote(PromotionStage.READY_WITH_LIMITATIONS, {
            "contract_compatible": True,
            "parsed_through_adapter": True,
            "quality_gates_executed": True,
        })
        assert result.allowed is True

        # READY_WITH_LIMITATIONS -> READY (with all evidence)
        result = workflow.promote(PromotionStage.READY, {
            "provenance_complete": True,
            "idempotency_verified": True,
            "limitations_resolved": True,
            "temporal_readiness_satisfied": True,
        })
        assert result.allowed is True
        assert workflow.current_stage == PromotionStage.READY


class TestPromotionResult:
    """Test PromotionResult structure."""

    def test_promotion_result_structure(self):
        result = PromotionResult(
            allowed=True,
            from_stage=PromotionStage.NOT_VERIFIED,
            to_stage=PromotionStage.VERIFIED,
            requirements_met=("source_authority_verified",),
            requirements_missing=(),
            evidence_required="Official source confirmed",
        )
        assert result.allowed is True
        assert result.from_stage == PromotionStage.NOT_VERIFIED
        assert result.to_stage == PromotionStage.VERIFIED