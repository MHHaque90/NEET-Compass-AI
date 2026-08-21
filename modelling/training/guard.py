"""
Safe Model Training Guard - Phase 15
Training entry point that refuses to execute when readiness insufficient.
IMPOSSIBLE TO BYPASS ACCIDENTALLY.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from modelling.contracts.versioning import DatasetVersion
from modelling.leakage.checker import LeakageResult
from modelling.quality.gates import QualityGateResult
from modelling.splits.engine import TemporalValidationStatus


class TrainingBlockReason(str, Enum):
    """Reasons training is blocked."""

    TEMPORAL_VALIDATION_BLOCKED = "TEMPORAL_VALIDATION_BLOCKED"
    INSUFFICIENT_VERIFIED_YEARS = "INSUFFICIENT_VERIFIED_YEARS"
    TARGET_NOT_READY = "TARGET_NOT_READY"
    LEAKAGE_CHECKS_FAILED = "LEAKAGE_CHECKS_FAILED"
    DATA_QUALITY_GATES_FAILED = "DATA_QUALITY_GATES_FAILED"
    PROVENANCE_INCOMPLETE = "PROVENANCE_INCOMPLETE"
    NO_TARGET_DEFINED = "NO_TARGET_DEFINED"
    MODEL_ALREADY_EXISTS = "MODEL_ALREADY_EXISTS"


@dataclass(frozen=True)
class TrainingGuardResult:
    """Result of training guard check."""

    allowed: bool
    block_reasons: list[TrainingBlockReason]
    check_timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.allowed and self.block_reasons:
            raise ValueError("Cannot have block reasons if allowed=True")
        if not self.allowed and not self.block_reasons:
            raise ValueError("Must have block reasons if not allowed")


class TrainingGuard:
    """
    Safe training guard.
    IMPOSSIBLE TO BYPASS ACCIDENTALLY through normal configuration.
    NO "force training" option.
    """

    def __init__(
        self,
        temporal_status: TemporalValidationStatus,
        target_readiness: str,
        verified_years: dict[str, list[int]],
        minimum_years_required: int = 3,
    ):
        self.temporal_status = temporal_status
        self.target_readiness = target_readiness
        self.verified_years = verified_years
        self.minimum_years_required = minimum_years_required

    def check_training_allowed(
        self,
        dataset_version: DatasetVersion,
        leakage_result: LeakageResult,
        quality_gate_result: QualityGateResult,
        target_name: str,
    ) -> TrainingGuardResult:
        """
        Check if training is allowed.
        Returns TRAINING_BLOCKED with reasons if any check fails.
        """
        block_reasons = []
        details = {}

        # Check 1: Temporal validation
        if self.temporal_status != TemporalValidationStatus.READY:
            block_reasons.append(TrainingBlockReason.TEMPORAL_VALIDATION_BLOCKED)
            details["temporal_status"] = self.temporal_status.value

        # Check 2: Insufficient verified years
        total_verified = sum(len(years) for years in self.verified_years.values())
        if total_verified < self.minimum_years_required:
            block_reasons.append(TrainingBlockReason.INSUFFICIENT_VERIFIED_YEARS)
            details["verified_years"] = self.verified_years
            details["total_verified"] = total_verified
            details["minimum_required"] = self.minimum_years_required

        # Check 3: Target readiness
        if self.target_readiness != "READY":
            block_reasons.append(TrainingBlockReason.TARGET_NOT_READY)
            details["target_readiness"] = self.target_readiness
            details["requested_target"] = target_name

        # Check 4: Leakage checks
        if not leakage_result.passed:
            block_reasons.append(TrainingBlockReason.LEAKAGE_CHECKS_FAILED)
            details["leakage_violations"] = leakage_result.violation_count
            details["critical_violations"] = len(leakage_result.critical_violations)

        # Check 5: Data quality gates
        if not quality_gate_result.overall_passed:
            block_reasons.append(TrainingBlockReason.DATA_QUALITY_GATES_FAILED)
            details["quality_gates_passed"] = quality_gate_result.passed_gates
            details["quality_gates_total"] = quality_gate_result.total_gates

        # Check 6: Provenance completeness
        if not dataset_version.quality_gate_results.get("provenance_complete", False):
            block_reasons.append(TrainingBlockReason.PROVENANCE_INCOMPLETE)
            details["provenance_complete"] = False

        # Check 7: No target defined
        if target_name == "NO_TARGET_READY" or not target_name:
            block_reasons.append(TrainingBlockReason.NO_TARGET_DEFINED)
            details["target_name"] = target_name

        allowed = len(block_reasons) == 0

        return TrainingGuardResult(
            allowed=allowed,
            block_reasons=block_reasons,
            check_timestamp=datetime.now(UTC),
            details=details,
        )

    def execute_training(
        self,
        dataset_version: DatasetVersion,
        leakage_result: LeakageResult,
        quality_gate_result: QualityGateResult,
        target_name: str,
        training_config: dict[str, Any],
    ) -> "TrainingResult":
        """
        Execute training if allowed.
        This method WILL NOT EXECUTE if any guard check fails.
        """
        guard_result = self.check_training_allowed(
            dataset_version, leakage_result, quality_gate_result, target_name
        )

        if not guard_result.allowed:
            return TrainingResult(
                success=False,
                model_metadata=None,
                guard_result=guard_result,
                error_message=self._format_block_message(guard_result),
            )

        # Training would happen here in future sprints
        # For Sprint 4.0, we explicitly do NOT train
        return TrainingResult(
            success=False,
            model_metadata=None,
            guard_result=guard_result,
            error_message="TRAINING_BLOCKED: Sprint 4.0 does not execute training. Engine foundation only.",
        )

    def _format_block_message(self, result: TrainingGuardResult) -> str:
        """Format human-readable block message."""
        lines = ["TRAINING BLOCKED - Reasons:"]
        for reason in result.block_reasons:
            lines.append(f"  - {reason.value}")
        if result.details:
            lines.append("\nDetails:")
            for key, value in result.details.items():
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)


@dataclass(frozen=True)
class TrainingResult:
    """Result of training attempt."""

    success: bool
    model_metadata: Any | None
    guard_result: TrainingGuardResult
    error_message: str


# Singleton instance for global access
_global_guard: TrainingGuard | None = None


def get_training_guard() -> TrainingGuard:
    """Get or create global training guard."""
    global _global_guard
    if _global_guard is None:
        from modelling.config.modelling_readiness import (
            get_modelling_ready_years,
            get_target_readiness,
            get_temporal_validation_status,
        )
        from modelling.splits.engine import TemporalValidationStatus

        temporal_str = get_temporal_validation_status()
        temporal_status = (
            TemporalValidationStatus.READY
            if temporal_str == "READY"
            else TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS
        )

        _global_guard = TrainingGuard(
            temporal_status=temporal_status,
            target_readiness=get_target_readiness(),
            verified_years={k.value: v for k, v in get_modelling_ready_years().items()},
        )
    return _global_guard
