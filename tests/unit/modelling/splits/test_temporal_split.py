"""
Tests for Temporal Split Engine - Phase 6
"""

import pytest
from datetime import datetime, timezone
from modelling.splits.engine import TemporalSplitter, SplitResult, TemporalValidationStatus
from modelling.contracts.dataset import (
    ModellingRecord,
    SourceFacts,
    DerivedFeatures,
    Targets,
    Provenance,
    TemporalMetadata,
    AuthorityType,
    QuotaType,
    CategoryType,
    RoundType,
)


class TestTemporalSplitter:
    def _make_records(self, years):
        records = []
        for year in years:
            facts = SourceFacts(
                counselling_year=year, state="ALL_INDIA",
                counselling_authority=AuthorityType.MCC, round=RoundType.ROUND_1,
                course="MBBS", institute="AIIMS Delhi", institute_code="AIMS001",
                quota=QuotaType.AI, category=CategoryType.GN, total_seats=100, allotment_count=100,
            )
            features = DerivedFeatures(
                round_number=1, is_first_round=True, category_quota_combo="gn_ai",
                institute_type="govt", state_quota_indicator=False, year_index=0, seat_count_log=4.615,
            )
            targets = Targets()
            prov = Provenance(
                source_file_id=f"file_{year}", file_checksum="a"*64, source_url="https://test.com",
                parser_version="v1", retrieval_timestamp=datetime.now(timezone.utc), contract_version="1.0.0",
                adapter_version="v1", transformation_version="v1", feature_version="v1", quality_gate_version="v1",
            )
            # latest_allowed_year must be >= 2021 per TemporalMetadata validation
            allowed_year = max(year - 1, 2021)
            temporal = TemporalMetadata(
                prediction_time=datetime.now(timezone.utc), latest_allowed_year=allowed_year,
                latest_allowed_round=RoundType.ROUND_1, feature_computation_timestamp=datetime.now(timezone.utc),
            )
            records.append(ModellingRecord(
                source_facts=facts, derived_features=features, targets=targets,
                provenance=prov, temporal_metadata=temporal, dataset_version="v1", record_id=f"rec_{year}",
            ))
        return records

    def test_insufficient_years_blocked(self):
        ready_years = {AuthorityType.MCC: [2025]}
        splitter = TemporalSplitter(minimum_years_required=3)
        records = self._make_records([2025])
        result = splitter.split(records, ready_years)
        assert result.status == TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS
        assert len(result.train_records) == 0
        assert "Only 1 verified modelling-ready year(s)" in result.blocking_reason

    def test_sufficient_years_ready(self):
        ready_years = {AuthorityType.MCC: [2021, 2022, 2023, 2024, 2025]}
        # Use test_years_count=2 to match expected split
        splitter = TemporalSplitter(minimum_years_required=3, test_years_count=2, validation_years_count=1)
        records = self._make_records([2021, 2022, 2023, 2024, 2025])
        result = splitter.split(records, ready_years)
        assert result.status == TemporalValidationStatus.READY
        assert len(result.train_records) > 0
        assert len(result.validation_records) > 0
        assert len(result.test_records) > 0
        assert result.train_years == [2021, 2022]
        assert result.validation_years == [2023]
        assert result.test_years == [2024, 2025]

    def test_current_status_blocked(self):
        ready_years = {AuthorityType.MCC: [2025]}
        splitter = TemporalSplitter(minimum_years_required=3)
        status = splitter.get_current_status(ready_years)
        assert status == TemporalValidationStatus.BLOCKED_INSUFFICIENT_YEARS
