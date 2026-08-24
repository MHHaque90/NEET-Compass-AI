"""Tests for Evidence Manifest Validation — Sprint 4.1.

Critical assertions:
- All required manifest fields must be present
- Missing fields cause validation failure
"""

import pytest
from etl.contracts.historical.manifest import (
    EvidenceManifest,
    REQUIRED_MANIFEST_FIELDS,
    create_manifest,
    validate_manifest,
)
from etl.contracts.canonical import SourceMetadata


class TestEvidenceManifest:
    """Test evidence manifest creation and validation."""

    def test_required_fields_defined(self):
        """REQUIRED_MANIFEST_FIELDS should contain all mandatory fields."""
        assert len(REQUIRED_MANIFEST_FIELDS) > 0
        # Check key fields exist
        assert "source_authority" in REQUIRED_MANIFEST_FIELDS
        assert "source_url" in REQUIRED_MANIFEST_FIELDS
        assert "sha256" in REQUIRED_MANIFEST_FIELDS
        assert "pii_status" in REQUIRED_MANIFEST_FIELDS
        assert "modelling_readiness" in REQUIRED_MANIFEST_FIELDS

    def test_create_manifest_with_complete_metadata(self):
        """create_manifest should produce valid manifest with complete SourceMetadata."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        )

        manifest = create_manifest(
            source_metadata=metadata,
            artifact_filename="seat_matrix_r1_2024.csv",
            mime_type="text/csv",
            file_size=1024000,
            sha256="abc123def456" * 4 + "abc123",
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="VALIDATED",
            modelling_readiness="READY_WITH_LIMITATIONS",
            limitations=["Manual retrieval only"],
            notes="Test artifact",
        )

        assert manifest.source_authority == "Medical Counselling Committee"
        assert manifest.counselling_year == 2024
        assert manifest.dataset_type == "seat_matrix"
        assert manifest.sha256 == "abc123def456" * 4 + "abc123"
        assert manifest.modelling_readiness == "READY_WITH_LIMITATIONS"

    def test_validate_manifest_complete(self):
        """validate_manifest should pass for complete manifest."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        )

        manifest = create_manifest(
            source_metadata=metadata,
            artifact_filename="seat_matrix_r1_2024.csv",
            mime_type="text/csv",
            file_size=1024000,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="VALIDATED",
            modelling_readiness="READY_WITH_LIMITATIONS",
        )

        is_valid, missing = validate_manifest(manifest)
        assert is_valid is True
        assert missing == []

    def test_validate_manifest_missing_fields(self):
        """validate_manifest should fail for incomplete manifest."""
        # Create manifest with minimal required fields only
        manifest = EvidenceManifest(
            source_authority="Medical Counselling Committee",
            source_url="https://mcc.nic.in/archive-ug/",
            source_identifier="mcc_ug_archive",
            dataset_type="seat_matrix",
            counselling_year=2024,
            round="Round 1",
            course="MBBS+BDS+NURSING",
            quota="ALL_INDIA",
            retrieval_method="MANUAL_BROWSER",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            retrieval_status="SUCCESS",
            verification_status="VERIFIED",
            evidence_status="VERIFIED",
            artifact_filename="test.csv",
            mime_type="text/csv",
            file_size=1000,
            sha256="a" * 64,
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            contract_version="1.1.0",
            parser_version="mcc_etl_v1",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="VALIDATED",
            modelling_readiness="READY_WITH_LIMITATIONS",
            limitations=[],
            notes="",
        )

        # This should have all fields but let's test by creating incomplete one
        incomplete_manifest = EvidenceManifest(
            source_authority="",  # Missing
            source_url="",  # Missing
            source_identifier="",
            dataset_type="",
            counselling_year=0,
            round="",
            course="",
            quota="",
            retrieval_method="",
            retrieval_timestamp="",
            retrieval_status="",
            verification_status="",
            evidence_status="",
            artifact_filename="",
            mime_type="",
            file_size=0,
            sha256="",
            source_file_id="",
            contract_version="",
            parser_version="",
            format_status="",
            pii_status="",
            validation_status="",
            modelling_readiness="",
        )

        is_valid, missing = validate_manifest(incomplete_manifest)
        assert is_valid is False
        assert len(missing) > 0

    def test_manifest_to_dict_serialization(self):
        """Manifest should serialize to dict with all fields."""
        metadata = SourceMetadata(
            source_id="mcc_ug_archive",
            authority="Medical Counselling Committee",
            dataset="seat_matrix",
            effective_year=2024,
            publication_version="Round 1",
            contract_version="1.1.0",
            retrieval_timestamp="2026-08-15T14:30:00+00:00",
            source_file_id="mcc_ug_archive_seat_matrix_2024_abc123",
            file_checksum="abc123def456",
            parser_version="mcc_etl_v1",
            source_url="https://mcc.nic.in/archive-ug/2024/seat_matrix_r1.csv",
        )

        manifest = create_manifest(
            source_metadata=metadata,
            artifact_filename="test.csv",
            mime_type="text/csv",
            file_size=1000,
            sha256="a" * 64,
            retrieval_method="MANUAL_BROWSER",
            format_status="FORMAT_VERIFIED",
            pii_status="PII_CLEAR",
            validation_status="VALIDATED",
            modelling_readiness="READY",
        )

        d = manifest.to_dict()
        assert isinstance(d, dict)
        assert d["source_authority"] == "Medical Counselling Committee"
        assert d["sha256"] == "a" * 64
        assert "created_timestamp" in d
        assert "updated_timestamp" in d

    def test_manifest_from_dict(self):
        """Manifest should deserialize from dict."""
        data = {
            "source_authority": "Test Authority",
            "source_url": "https://example.com",
            "source_identifier": "test_source",
            "dataset_type": "test_dataset",
            "counselling_year": 2024,
            "round": "Round 1",
            "course": "MBBS",
            "quota": "ALL_INDIA",
            "retrieval_method": "MANUAL_BROWSER",
            "retrieval_timestamp": "2026-08-15T14:30:00+00:00",
            "retrieval_status": "SUCCESS",
            "verification_status": "VERIFIED",
            "evidence_status": "VERIFIED",
            "artifact_filename": "test.csv",
            "mime_type": "text/csv",
            "file_size": 1000,
            "sha256": "a" * 64,
            "source_file_id": "test_source_test_dataset_2024_abc123",
            "contract_version": "1.0.0",
            "parser_version": "v1",
            "format_status": "FORMAT_VERIFIED",
            "pii_status": "PII_CLEAR",
            "validation_status": "VALIDATED",
            "modelling_readiness": "READY",
            "limitations": [],
            "notes": "",
            "lifecycle_stage": "MODELLING_READY",
        }

        manifest = EvidenceManifest.from_dict(data)
        assert manifest.source_authority == "Test Authority"
        assert manifest.counselling_year == 2024