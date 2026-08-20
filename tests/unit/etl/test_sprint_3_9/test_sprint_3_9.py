"""Minimal deterministic tests for Sprint 3.9 Historical Evidence Acquisition & Data Readiness Gate.

Tests core functionality of the historical evidence framework.
"""

from __future__ import annotations

from etl.contracts.historical import (
    EvidenceLifecycleStage, EvidenceStatus,
    create_manifest, validate_manifest,
    ProvenanceGate, PIIGate, ArtifactIntegrity,
    ContractGate, ContractCompatibility,
    HistoricalQualityGateRunner, TemporalReadinessGate,
    PromotionStage, PromotionWorkflow, VALID_PROMOTIONS,
    validate_transition, lifecycle_requires_evidence,
    compute_temporal_readiness, MINIMUM_VERIFIED_YEARS,
    compute_artifact_hash, build_source_file_id,
    validate_contract_compatibility,
    detect_pii, validate_no_pii,
    PII_BLOCKLIST, verify_artifact_integrity
)
from etl.contracts.canonical import SourceMetadata


def test_imports():
    """Test all required imports work."""
    assert EvidenceLifecycleStage is not None
    assert EvidenceStatus is not None
    assert create_manifest is not None
    assert validate_manifest is not None
    assert ProvenanceGate is not None
    assert PIIGate is not None
    assert ArtifactIntegrity is not None
    assert ContractGate is not None
    assert ContractCompatibility is not None
    assert HistoricalQualityGateRunner is not None
    assert TemporalReadinessGate is not None
    assert PromotionStage is not None
    assert PromotionWorkflow is not None
    assert validate_transition is not None
    assert lifecycle_requires_evidence is not None
    assert compute_temporal_readiness is not None
    assert MINIMUM_VERIFIED_YEARS is not None
    assert compute_artifact_hash is not None
    assert build_source_file_id is not None
    assert validate_contract_compatibility is not None
    assert detect_pii is not None
    assert validate_no_pii is not None
    assert PII_BLOCKLIST is not None


def test_lifecycle_stage():
    """Test lifecycle stage enum."""
    stage = EvidenceLifecycleStage.DISCOVERED
    assert stage.value == "DISCOVERED"
    assert hasattr(EvidenceLifecycleStage, "SOURCE_VERIFIED")
    assert hasattr(EvidenceLifecycleStage, "MODELLING_READY")


def test_transition_validation():
    """Test lifecycle transition validation."""
    # Valid transition
    valid, reason = validate_transition(
        EvidenceLifecycleStage.DISCOVERED,
        EvidenceLifecycleStage.SOURCE_VERIFIED
    )
    assert valid is True

    # Invalid transition (direct to modelling ready)
    valid, reason = validate_transition(
        EvidenceLifecycleStage.DISCOVERED,
        EvidenceLifecycleStage.MODELLING_READY
    )
    assert valid is False


def test_manifest_creation():
    """Test evidence manifest creation."""
    manifest = create_manifest(
        source_metadata=None,
        artifact_filename='test.csv',
        mime_type='text/csv',
        file_size=100,
        sha256='a' * 64,
        retrieval_method='MANUAL_BROWSER',
        format_status='FORMAT_VERIFIED',
        pii_status='PII_CLEAR',
        validation_status='VALIDATED',
        modelling_readiness='READY',
        limitations=[],
        notes='Test',
    )
    assert manifest is not None
    assert hasattr(manifest, 'evidence_status')
    assert hasattr(manifest, 'lifecycle_stage')

    # Test validation
    is_valid, missing = validate_manifest(manifest)
    assert isinstance(is_valid, bool)


def test_manifest_with_data():
    """Test manifest creation with source data."""
    metadata = SourceMetadata(
        source_id='mcc_ug_archive',
        authority='MCC / DGHS',
        dataset='seat_matrix',
        effective_year=2025,
        publication_version='Round 1',
        contract_version='1.1.0',
        retrieval_timestamp='2026-08-09T10:00:00+00:00',
        source_file_id='mcc_seat_matrix_2025_abc123',
        file_checksum='a' * 64,
        parser_version='mcc_etl_v1',
        source_url='https://mcc.nic.in/archive-ug/',
    )

    manifest = create_manifest(
        source_metadata=metadata,
        artifact_filename='seat_matrix_2025.csv',
        mime_type='text/csv',
        file_size=1024,
        sha256='a' * 64,
        retrieval_method='MANUAL_BROWSER',
        format_status='FORMAT_VERIFIED',
        pii_status='PII_CLEAR',
        validation_status='VALIDATED',
        modelling_readiness='READY',
        limitations=[],
        notes='Full evidence manifest',
    )

    assert manifest is not None
    assert manifest.source_authority == 'MCC / DGHS'
    # Evidence status is VERIFIED because file_checksum is present
    assert manifest.evidence_status == 'VERIFIED'

    # Test validation
    is_valid, missing = validate_manifest(manifest)
    assert is_valid is True
    assert len(missing) == 0


def test_pii_detection():
    """Test PII detection."""
    # No PII
    detected = detect_pii(['college_id', 'course_id', 'quota_id'])
    assert len(detected) == 0

    # With PII
    detected = detect_pii(['college_id', 'candidate_name', 'quota_id'])
    assert 'candidate_name' in detected

    # Test validation
    result = validate_no_pii(['college_id', 'course_id', 'quota_id'])
    assert result.passed is True

    result = validate_no_pii(['college_id', 'candidate_name', 'quota_id'])
    assert result.passed is False


def test_contract_compatibility():
    """Test contract compatibility validation."""
    # COMPATIBLE with format verified
    result = validate_contract_compatibility(
        ContractCompatibility.COMPATIBLE,
        format_verified=True
    )
    assert result.passed is True

    # INCOMPATIBLE
    result = validate_contract_compatibility(
        ContractCompatibility.INCOMPATIBLE,
        format_verified=True
    )
    assert result.passed is False

    # UNKNOWN
    result = validate_contract_compatibility(
        ContractCompatibility.UNKNOWN,
        format_verified=True
    )
    assert result.passed is False


def test_temporal_readiness():
    """Test temporal readiness computation."""
    # 1 year - blocked
    result = compute_temporal_readiness({'MCC': [2025]})
    assert result.passed is False
    assert result.verified_count == 1
    assert result.minimum_required == MINIMUM_VERIFIED_YEARS

    # 3 years - sufficient
    result = compute_temporal_readiness({'MCC': [2021, 2023, 2025]})
    assert result.verified_count >= 3
    assert result.minimum_required == MINIMUM_VERIFIED_YEARS


def test_artifact_integrity():
    """Test artifact integrity checks."""
    # Same bytes -> same hash
    data = b'test data for hash computation'
    hash1 = compute_artifact_hash(data)
    hash2 = compute_artifact_hash(data)
    assert hash1 == hash2

    # Different bytes -> different hash
    hash3 = compute_artifact_hash(b'different data')
    assert hash1 != hash3

    # Source file ID building
    sid = build_source_file_id('a' * 64, 'mcc', 'seat_matrix', 2025)
    assert sid == 'mcc_seat_matrix_2025_aaaaaaaaaaaa'

    # Artifact integrity verification
    result = verify_artifact_integrity(
        data,
        source_id='mcc',
        dataset='seat_matrix',
        effective_year=2025,
        expected_checksum=hash1,
    )
    assert result.passed is True


def test_provenance_gate():
    """Test provenance completeness validation."""
    metadata = SourceMetadata(
        source_id='mcc_ug_archive',
        authority='MCC / DGHS',
        dataset='seat_matrix',
        effective_year=2025,
        publication_version='Round 1',
        contract_version='1.1.0',
        retrieval_timestamp='2026-08-09T10:00:00+00:00',
        source_file_id='mcc_seat_matrix_2025_abc123',
        file_checksum='a' * 64,
        parser_version='mcc_etl_v1',
        source_url='https://mcc.nic.in/archive-ug/',
    )

    gate = ProvenanceGate()
    result = gate.validate(metadata)
    assert result.passed is True
    assert len(result.missing_fields) == 0


def test_promotion_workflow():
    """Test promotion workflow logic."""
    # NOT_VERIFIED -> VERIFIED is the only valid first step
    valid_next = VALID_PROMOTIONS.get(PromotionStage.NOT_VERIFIED, ())
    assert PromotionStage.VERIFIED in valid_next
    assert PromotionStage.READY not in valid_next  # Cannot skip

    # Valid promotion sequence
    assert PromotionStage.VALIDATED in VALID_PROMOTIONS[PromotionStage.VERIFIED]
    assert PromotionStage.READY_WITH_LIMITATIONS in VALID_PROMOTIONS[PromotionStage.VALIDATED]
    assert PromotionStage.READY in VALID_PROMOTIONS[PromotionStage.READY_WITH_LIMITATIONS]


if __name__ == "__main__":
    test_imports()
    test_lifecycle_stage()
    test_transition_validation()
    test_manifest_creation()
    test_manifest_with_data()
    test_pii_detection()
    test_contract_compatibility()
    test_temporal_readiness()
    test_artifact_integrity()
    test_provenance_gate()
    test_promotion_workflow()
    print('All minimal Sprint 3.9 tests passed!')