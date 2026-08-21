"""
Modelling Data Quality Gates - Phase 16
Connects modelling input to existing data-quality framework.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from modelling.contracts.dataset import (
    AuthorityType,
    CategoryType,
    ModellingRecord,
    QuotaType,
    RoundType,
)


class ModellingQualityGate(str, Enum):
    """Quality gates specific to modelling data."""

    NO_DUPLICATE_RECORDS = "no_duplicate_records"
    REQUIRED_FIELDS_COMPLETE = "required_fields_complete"
    VALID_CATEGORY = "valid_category"
    VALID_QUOTA = "valid_quota"
    VALID_YEAR = "valid_year"
    VALID_ROUND = "valid_round"
    PROVENANCE_COMPLETE = "provenance_complete"
    NO_PII = "no_pii"
    NO_FUTURE_INFORMATION = "no_future_information"
    COMPATIBLE_CONTRACTS = "compatible_contracts"
    VALID_RANK = "valid_rank"
    VALID_SEAT_COUNT = "valid_seat_count"
    SOURCE_VERIFIED = "source_verified"


@dataclass(frozen=True)
class QualityGateResult:
    """Result of modelling quality gates."""

    overall_passed: bool
    passed_gates: int
    total_gates: int
    gate_results: dict[ModellingQualityGate, bool]
    failed_records: list[str] = field(default_factory=list)
    check_timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        if self.overall_passed and self.failed_records:
            raise ValueError("Cannot have failed records if overall_passed=True")


class ModellingQualityGates:
    """
    Modelling data quality gates.
    Reuses existing infrastructure where possible.
    """

    def __init__(self):
        self.valid_categories = {c.value for c in CategoryType}
        self.valid_quotas = {q.value for q in QuotaType}
        self.valid_rounds = {r.value for r in RoundType}
        self.valid_authorities = {a.value for a in AuthorityType}
        self.min_year = 2021
        self.max_year = 2030
        self.max_rank = 900000
        self.max_seats = 5000

    def run_gates(self, records: list[ModellingRecord]) -> QualityGateResult:
        """Run all quality gates on modelling records."""
        gate_results = {}
        failed_records = []

        # Gate 1: No duplicate records
        gate_results[ModellingQualityGate.NO_DUPLICATE_RECORDS] = self._check_no_duplicates(
            records, failed_records
        )

        # Gate 2: Required fields complete
        gate_results[ModellingQualityGate.REQUIRED_FIELDS_COMPLETE] = self._check_required_fields(
            records, failed_records
        )

        # Gate 3: Valid category
        gate_results[ModellingQualityGate.VALID_CATEGORY] = self._check_valid_category(
            records, failed_records
        )

        # Gate 4: Valid quota
        gate_results[ModellingQualityGate.VALID_QUOTA] = self._check_valid_quota(
            records, failed_records
        )

        # Gate 5: Valid year
        gate_results[ModellingQualityGate.VALID_YEAR] = self._check_valid_year(
            records, failed_records
        )

        # Gate 6: Valid round
        gate_results[ModellingQualityGate.VALID_ROUND] = self._check_valid_round(
            records, failed_records
        )

        # Gate 7: Provenance complete
        gate_results[ModellingQualityGate.PROVENANCE_COMPLETE] = self._check_provenance_complete(
            records, failed_records
        )

        # Gate 8: No PII
        gate_results[ModellingQualityGate.NO_PII] = self._check_no_pii(records, failed_records)

        # Gate 9: No future information
        gate_results[ModellingQualityGate.NO_FUTURE_INFORMATION] = self._check_no_future_info(
            records, failed_records
        )

        # Gate 10: Compatible contracts
        gate_results[ModellingQualityGate.COMPATIBLE_CONTRACTS] = self._check_compatible_contracts(
            records, failed_records
        )

        # Gate 11: Valid rank
        gate_results[ModellingQualityGate.VALID_RANK] = self._check_valid_rank(
            records, failed_records
        )

        # Gate 12: Valid seat count
        gate_results[ModellingQualityGate.VALID_SEAT_COUNT] = self._check_valid_seat_count(
            records, failed_records
        )

        # Gate 13: Source verified
        gate_results[ModellingQualityGate.SOURCE_VERIFIED] = self._check_source_verified(
            records, failed_records
        )

        passed_count = sum(1 for v in gate_results.values() if v)
        total_count = len(gate_results)
        overall_passed = passed_count == total_count

        return QualityGateResult(
            overall_passed=overall_passed,
            passed_gates=passed_count,
            total_gates=total_count,
            gate_results=gate_results,
            failed_records=list(set(failed_records)),
        )

    def _check_no_duplicates(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check for duplicate records."""
        seen = set()
        for record in records:
            key = record.record_id
            if key in seen:
                failed_records.append(key)
            seen.add(key)
        return len(failed_records) == 0 or all(
            r not in failed_records for r in [rec.record_id for rec in records]
        )

    def _check_required_fields(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check all required fields are present."""
        required_source = [
            "counselling_year",
            "counselling_authority",
            "round",
            "course",
            "institute",
            "institute_code",
            "quota",
            "category",
            "total_seats",
            "allotment_count",
        ]
        required_provenance = [
            "source_file_id",
            "file_checksum",
            "source_url",
            "parser_version",
            "retrieval_timestamp",
            "contract_version",
            "adapter_version",
            "transformation_version",
            "feature_version",
            "quality_gate_version",
        ]

        all_ok = True
        for record in records:
            for field in required_source:
                if (
                    not hasattr(record.source_facts, field)
                    or getattr(record.source_facts, field) is None
                ):
                    failed_records.append(record.record_id)
                    all_ok = False
            for field in required_provenance:
                if (
                    not hasattr(record.provenance, field)
                    or getattr(record.provenance, field) is None
                ):
                    failed_records.append(record.record_id)
                    all_ok = False
        return all_ok

    def _check_valid_category(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check all categories are valid."""
        all_ok = True
        for record in records:
            if record.source_facts.category.value not in self.valid_categories:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_valid_quota(self, records: list[ModellingRecord], failed_records: list[str]) -> bool:
        """Check all quotas are valid."""
        all_ok = True
        for record in records:
            if record.source_facts.quota.value not in self.valid_quotas:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_valid_year(self, records: list[ModellingRecord], failed_records: list[str]) -> bool:
        """Check all years are valid."""
        all_ok = True
        for record in records:
            year = record.source_facts.counselling_year
            if year < self.min_year or year > self.max_year:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_valid_round(self, records: list[ModellingRecord], failed_records: list[str]) -> bool:
        """Check all rounds are valid."""
        all_ok = True
        for record in records:
            if record.source_facts.round.value not in self.valid_rounds:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_provenance_complete(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check provenance is complete for all records."""
        required = [
            "source_file_id",
            "file_checksum",
            "source_url",
            "parser_version",
            "retrieval_timestamp",
            "contract_version",
            "adapter_version",
            "transformation_version",
            "feature_version",
            "quality_gate_version",
        ]
        all_ok = True
        for record in records:
            for field in required:
                if (
                    not hasattr(record.provenance, field)
                    or getattr(record.provenance, field) is None
                ):
                    failed_records.append(record.record_id)
                    all_ok = False
        return all_ok

    def _check_no_pii(self, records: list[ModellingRecord], failed_records: list[str]) -> bool:
        """Check no PII in records."""
        # PII fields that should NEVER appear in modelling data
        pii_fields = [
            "candidate_name",
            "candidate_id",
            "roll_number",
            "application_number",
            "date_of_birth",
            "email",
            "phone",
            "address",
            "aadhaar",
            "pan",
            "mother_name",
            "father_name",
            "category_certificate_number",
        ]
        all_ok = True
        for record in records:
            # Check source facts don't have PII
            for field in pii_fields:
                if hasattr(record.source_facts, field):
                    failed_records.append(record.record_id)
                    all_ok = False
            # Check derived features don't have PII
            for field in pii_fields:
                if hasattr(record.derived_features, field):
                    failed_records.append(record.record_id)
                    all_ok = False
        return all_ok

    def _check_no_future_info(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check no future information in features."""
        all_ok = True
        for record in records:
            # Check temporal metadata
            if not record.temporal_metadata.temporal_availability_verified:
                failed_records.append(record.record_id)
                all_ok = False
            if not record.temporal_metadata.leakage_check_passed:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_compatible_contracts(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check all records have compatible contract versions."""
        # For now, just verify contract_version is present and non-empty
        all_ok = True
        for record in records:
            if not record.provenance.contract_version:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_valid_rank(self, records: list[ModellingRecord], failed_records: list[str]) -> bool:
        """Check all ranks are valid."""
        all_ok = True
        for record in records:
            if record.source_facts.closing_rank is not None:
                if (
                    record.source_facts.closing_rank < 1
                    or record.source_facts.closing_rank > self.max_rank
                ):
                    failed_records.append(record.record_id)
                    all_ok = False
            if record.source_facts.opening_rank is not None:
                if (
                    record.source_facts.opening_rank < 1
                    or record.source_facts.opening_rank > self.max_rank
                ):
                    failed_records.append(record.record_id)
                    all_ok = False
        return all_ok

    def _check_valid_seat_count(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check all seat counts are valid."""
        all_ok = True
        for record in records:
            if (
                record.source_facts.total_seats < 0
                or record.source_facts.total_seats > self.max_seats
            ):
                failed_records.append(record.record_id)
                all_ok = False
            if record.source_facts.allotment_count < 0:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok

    def _check_source_verified(
        self, records: list[ModellingRecord], failed_records: list[str]
    ) -> bool:
        """Check all sources are VERIFIED in modelling_readiness.yaml."""
        # This would integrate with the modelling readiness config
        # For now, check that provenance has required fields
        all_ok = True
        for record in records:
            if not record.provenance.source_file_id or not record.provenance.file_checksum:
                failed_records.append(record.record_id)
                all_ok = False
        return all_ok
