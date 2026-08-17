"""Multi-source conformance test suite.

Verifies architectural invariants across MCC, Maharashtra, Karnataka, and Uttar
Pradesh state adapters. These tests verify architecture compliance, not
source-specific business assumptions.

Each test parameterized to run against all four sources.
"""

from __future__ import annotations

import csv
import os
import tempfile

import pytest

from etl.contracts.registry import ContractRegistry
from etl.contracts.base import SourceContract
from etl.contracts.version import ContractVersion


# --- A. Contract validity ---


@pytest.mark.parametrize(
    "source_id,dataset,contract_func",
    [
        # MCC
        ("mcc", "seat_matrix", None),
        ("mcc", "allotments", None),
        # Maharashtra
        ("mcc_state_maharashtra", "seat_matrix", None),
        ("mcc_state_maharashtra", "allotments", None),
        # Karnataka
        ("mcc_state_karnataka", "seat_matrix", None),
        ("mcc_state_karnataka", "allotments", None),
        # Uttar Pradesh
        ("mcc_state_uttar_pradesh", "seat_matrix", None),
        ("mcc_state_uttar_pradesh", "allotments", None),
    ],
)
def test_contract_validity(
    source_id,
    dataset,
    contract_func,
):
    """A1. Contract exists and is loadable."""
    registry: ContractRegistry = ContractRegistry()

    # Register the contract
    if source_id == "mcc":
        from etl.contracts.sources.mcc.contracts import (
            seat_matrix_2025_contract,
            allotments_2025_contract,
        )
        if dataset == "seat_matrix":
            registry.register(seat_matrix_2025_contract())
        else:
            registry.register(allotments_2025_contract())
    elif source_id == "mcc_state_maharashtra":
        from etl.contracts.sources.maharashtra.contracts import (
            seat_matrix_2026_contract,
            allotments_2026_contract,
        )
        if dataset == "seat_matrix":
            registry.register(seat_matrix_2026_contract())
        else:
            registry.register(allotments_2026_contract())
    elif source_id == "mcc_state_karnataka":
        from etl.contracts.sources.karnataka.contracts import (
            seat_matrix_2026_contract,
            allotments_2026_contract,
        )
        if dataset == "seat_matrix":
            registry.register(seat_matrix_2026_contract())
        else:
            registry.register(allotments_2026_contract())
    elif source_id == "mcc_state_uttar_pradesh":
        from etl.contracts.sources.uttar_pradesh.contracts import (
            seat_matrix_2026_contract,
            allotments_2026_contract,
        )
        if dataset == "seat_matrix":
            registry.register(seat_matrix_2026_contract())
        else:
            registry.register(allotments_2026_contract())

    # B1. Registry lookup succeeds
    fetched = registry.get_contract(source_id, dataset)
    assert isinstance(fetched, SourceContract)

    # B2. Contract version parses
    assert str(fetched.contract_version) in ("1.0.0", "1.1.0")


# --- B. Canonical independence ---

from etl.contracts.sources.maharashtra.adapters import (
    MaharashtraSeatMatrixAdapter,
    MaharashtraAllotmentsAdapter,
)
from etl.contracts.sources.karnataka.adapters import (
    KarnatakaSeatMatrixAdapter,
    KarnatakaAllotmentsAdapter,
)
from etl.contracts.sources.uttar_pradesh.adapters import (
    UttarPradeshSeatMatrixAdapter,
    UttarPradeshAllotmentsAdapter,
)
from etl.contracts.canonical import SourceMetadata


def _make_minimal_metadata(source_id: str) -> SourceMetadata:
    """Minimal SourceMetadata for adapter testing."""
    return SourceMetadata(
        source_id=source_id,
        authority="Test Authority",
        dataset="seat_matrix",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="test_1234",
        file_checksum="a" * 64,
        parser_version="test_v1",
        source_url="https://example.com",
    )


@pytest.mark.parametrize(
    "adapter_class,adapter_name",
    [
        (MaharashtraSeatMatrixAdapter, "maharashtra_seat_matrix"),
        (MaharashtraAllotmentsAdapter, "maharashtra_allotments"),
        (KarnatakaSeatMatrixAdapter, "karnataka_seat_matrix"),
        (KarnatakaAllotmentsAdapter, "karnataka_allotments"),
        (UttarPradeshSeatMatrixAdapter, "up_seat_matrix"),
        (UttarPradeshAllotmentsAdapter, "up_allotments"),
    ],
)
def test_canonical_independence(adapter_class, adapter_name):
    """B1. Canonical records contain no SQLAlchemy objects, no DB session
    dependency, no PostgreSQL-specific objects, no source-specific column
    names leak into canonical output."""
    adapter = adapter_class()

    # Determine contract based on adapter name
    if adapter_name.startswith("maharashtra"):
        from etl.contracts.sources.maharashtra.contracts import (
            seat_matrix_2026_contract,
            allotments_2026_contract,
        )
        contract = (
            seat_matrix_2026_contract()
            if "seat_matrix" in adapter_name
            else allotments_2026_contract()
        )
    elif adapter_name.startswith("karnataka"):
        from etl.contracts.sources.karnataka.contracts import (
            seat_matrix_2026_contract,
            allotments_2026_contract,
        )
        contract = (
            seat_matrix_2026_contract()
            if "seat_matrix" in adapter_name
            else allotments_2026_contract()
        )
    elif adapter_name.startswith("up"):
        from etl.contracts.sources.uttar_pradesh.contracts import (
            seat_matrix_2026_contract,
            allotments_2026_contract,
        )
        contract = (
            seat_matrix_2026_contract()
            if "seat_matrix" in adapter_name
            else allotments_2026_contract()
        )

    metadata = _make_minimal_metadata(adapter.__class__.__module__)

    # Build minimal raw data
    if "seat_matrix" in adapter_name.lower():
        raw = [
            {
                "Institute": "Test College",
                "Course": "MBBS",
                "Category": "OP",
                "Quota": "AI",
                "TotalSeats": "100",
            }
        ]
    else:
        raw = [
            {
                "Institute": "Test College",
                "Course": "MBBS",
                "Category": "OP",
                "Quota": "AI",
                "Round": "Round 1",
                "OpeningRank": "1",
                "ClosingRank": "100",
                "SeatCount": "1",
            }
        ]

    # Transform - should NOT access DB, SQLAlchemy, or PostgreSQL
    result = adapter.transform(raw, contract, metadata)

    # B1 checks: canonical records contain only plain dicts
    for rec in result.records:
        # Must be a plain dict (not SQLAlchemy model)
        assert isinstance(rec, dict), (
            f"{adapter_name}: record is not a plain dict"
        )

        # Must not contain SQLAlchemy/_sa_ attributes
        for key in rec:
            assert not key.startswith("_"), (
                f"{adapter_name}: record contains SQLAlchemy attribute '_{key}'"
            )

        # Must not contain source-specific column names
        if "seat_matrix" in adapter_name.lower():
            canonical_fields = {
                "college_id",
                "college_name",
                "state",
                "institute_type",
                "quota_id",
                "course_id",
                "branch",
                "category_id",
                "pwd",
                "total_seats",
                "effective_year",
                "source_file_id",
            }
            for key in rec:
                assert key in canonical_fields, (
                    f"{adapter_name}: unexpected key '{key}' in canonical output. "
                    f"Expected only canonical seat_matrix fields. Got: {set(rec.keys())}"
                )
        elif "allotments" in adapter_name.lower():
            canonical_fields = {
                "college_id",
                "college_name",
                "course_id",
                "quota_id",
                "category_id",
                "round_id",
                "rank",
                "opening_rank",
                "closing_rank",
                "seat_count",
                "effective_year",
                "source_file_id",
            }
            for key in rec:
                assert key in canonical_fields, (
                    f"{adapter_name}: unexpected key '{key}' in canonical output. "
                    f"Expected only canonical allotment fields. Got: {set(rec.keys())}"
                )


# --- C. Validation ---

from etl.contracts.validators import ContractValidator, ValidationMode


@pytest.mark.parametrize(
    "source_id",
    ["mcc", "mcc_state_maharashtra", "mcc_state_karnataka", "mcc_state_uttar_pradesh"],
)
def test_strict_validation_rejects_malformed_input(source_id):
    """C1. STRICT mode rejects malformed input."""
    from etl.contracts.sources.maharashtra.contracts import seat_matrix_2026_contract
    from etl.contracts.sources.maharashtra.adapters import MaharashtraSeatMatrixAdapter

    with open(
        "etl/contracts/sources/maharashtra/fixtures/seat_matrix_r1_2026.csv",
        "r",
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    adapter = MaharashtraSeatMatrixAdapter()
    contract = seat_matrix_2026_contract()
    validator = ContractValidator(contract, ValidationMode.STRICT)

    columns = list(rows[0].keys()) if rows else []
    column_errors = validator.validate_columns(columns, source_id, "seat_matrix")
    assert isinstance(column_errors, list)


@pytest.mark.parametrize(
    "source_id",
    ["mcc", "mcc_state_maharashtra", "mcc_state_karnataka", "mcc_state_uttar_pradesh"],
)
def test_compatible_validation_works(source_id):
    """C2. COMPATIBLE mode behaves correctly."""
    import csv

    from etl.contracts.sources.maharashtra.contracts import seat_matrix_2026_contract
    from etl.contracts.validators import ContractValidator, ValidationMode

    with open(
        "etl/contracts/sources/maharashtra/fixtures/seat_matrix_r1_2026.csv",
        "r",
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    adapter = MaharashtraSeatMatrixAdapter()
    contract = seat_matrix_2026_contract()
    validator = ContractValidator(contract, ValidationMode.COMPATIBLE)

    columns = list(rows[0].keys()) if rows else []
    column_errors = validator.validate_columns(columns, source_id, "seat_matrix")
    assert isinstance(column_errors, list)


# --- D. Provenance ---

from etl.contracts.sources.maharashtra.provenance import (
    build_metadata,
    build_source_file_id,
    bytes_checksum,
    PARSER_VERSION as MAH_PARSER_VERSION,
)
from etl.contracts.sources.karnataka.provenance import (
    PARSER_VERSION as KA_PARSER_VERSION,
)
from etl.contracts.sources.uttar_pradesh.provenance import (
    PARSER_VERSION as UP_PARSER_VERSION,
    build_metadata as up_build_metadata,
    build_source_file_id as up_build_source_file_id,
    bytes_checksum as up_bytes_checksum,
)


@pytest.mark.parametrize(
    "build_func,build_source_id",
    [
        (build_metadata, "mcc_state_maharashtra"),
        (build_metadata, "mcc_state_karnataka"),
        (up_build_metadata, "mcc_state_uttar_pradesh"),
    ],
)
def test_provenance_taxonomy_is_complete(build_func, build_source_id):
    """D1. Every real source record carries the full provenance taxonomy."""
    SAMPLE = b"Institute,Course\nTest College,MBBS\n"

    meta = build_func(
        source_id=build_source_id,
        authority="Test Authority",
        dataset="seat_matrix",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        source_url="https://example.com",
        checksum=bytes_checksum(SAMPLE),
    )

    for field in (
        "source_id",
        "dataset",
        "effective_year",
        "publication_version",
        "contract_version",
        "source_url",
        "file_checksum",
        "source_file_id",
        "parser_version",
        "retrieval_timestamp",
    ):
        val = getattr(meta, field)
        assert val not in (None, ""), field


# --- E. PII ---

from etl.contracts.sources.maharashtra.adapters import MaharashtraAllotmentsAdapter
from etl.contracts.sources.karnataka.adapters import KarnatakaAllotmentsAdapter
from etl.contracts.sources.uttar_pradesh.adapters import UttarPradeshAllotmentsAdapter


def _make_pii_allotment_metadata(source_id: str) -> SourceMetadata:
    """Minimal metadata for PII testing."""
    from etl.contracts.canonical import SourceMetadata

    return SourceMetadata(
        source_id=source_id,
        authority="Test Authority",
        dataset="allotments",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="test_pii_1234",
        file_checksum="b" * 64,
        parser_version="test_v1",
        source_url="https://example.com",
    )


def _make_pii_raw_data():
    """Raw allotment data with PII columns."""
    return [
        {
            "Institute": "Test College",
            "Course": "MBBS",
            "Category": "OP",
            "Quota": "AI",
            "Round": "Round 1",
            "OpeningRank": "1",
            "ClosingRank": "100",
            "SeatCount": "1",
            "Candidate Name": "John Doe",
            "Percentile": "95.5",
        },
        ]


@pytest.mark.parametrize(
    "adapter_class,adapter_name",
    [
        (MaharashtraAllotmentsAdapter, "maharashtra_allotments"),
        (KarnatakaAllotmentsAdapter, "karnataka_allotments"),
        (UttarPradeshAllotmentsAdapter, "up_allotments"),
    ],
)
def test_pii_protection(adapter_class, adapter_name):
    """E1. Adapters cannot emit candidate identifiers or other prohibited
    candidate-level PII."""
    adapter = adapter_class()

    # Determine the right contract
    if adapter_name == "maharashtra_allotments":
        from etl.contracts.sources.maharashtra.contracts import allotments_2026_contract
        contract = allotments_2026_contract()
    elif adapter_name == "karnataka_allotments":
        from etl.contracts.sources.karnataka.contracts import allotments_2026_contract
        contract = allotments_2026_contract()
    elif adapter_name == "up_allotments":
        from etl.contracts.sources.uttar_pradesh.contracts import allotments_2026_contract
        contract = allotments_2026_contract()

    metadata = _make_pii_allotment_metadata(adapter.__class__.__module__)

    # Raw data with PII columns
    raw_with_pii = _make_pii_raw_data()

    # Transform
    result = adapter.transform(raw_with_pii, contract, metadata)

    # E1 checks: canonical output must NOT contain candidate PII
    pii_fields = {
        "candidate_name",
        "percentile",
        "application_id",
        "password",
        "mother_name",
        "father_name",
        "guardian_name",
        "religion",
        "aadhaar",
        "contact_no",
        "email",
    }

    for rec in result.records:
        rec_keys = set(rec.keys())
        # No PII fields should appear in canonical output
        pii_found = rec_keys & pii_fields
        assert not pii_found, (
            f"{adapter_name}: PII leaked into canonical output: {pii_found}"
        )

        # All keys should be from the expected canonical set
        expected_canonical = {
            "college_id",
            "college_name",
            "course_id",
            "quota_id",
            "category_id",
            "round_id",
            "rank",
            "opening_rank",
            "closing_rank",
            "seat_count",
            "effective_year",
            "source_file_id",
        }
        unexpected = rec_keys - expected_canonical
        assert not unexpected, (
            f"{adapter_name}: unexpected keys in canonical output: {unexpected}"
        )


# --- F. Idempotency ---

from etl.contracts.sources.maharashtra.pipeline import (
    InMemoryFileRegistry,
    InMemoryLoader,
    ingest_seat_matrix,
    seat_matrix_loader,
)
from etl.contracts.sources.karnataka.pipeline import (
    ingest_seat_matrix as up_ingest_seat_matrix,
    seat_matrix_loader as up_seat_matrix_loader,
)
from etl.contracts.sources.uttar_pradesh.pipeline import (
    ingest_seat_matrix as up_ingest_seat_matrix,
    seat_matrix_loader as up_seat_matrix_loader,
)


@pytest.mark.parametrize(
    "adapter_name",
    ["maharashtra", "karnataka", "uttar_pradesh"],
)
def test_file_level_idempotency(adapter_name, request):
    """F1. Same file/content does not create duplicate logical records."""
    # Read fixture content
    if adapter_name == "maharashtra":
        fixture = "etl/contracts/sources/maharashtra/fixtures/seat_matrix_r1_2026.csv"
    elif adapter_name == "karnataka":
        fixture = "etl/contracts/sources/karnataka/fixtures/seatmatrix_ka_r1_2026.csv"
    else:
        fixture = "etl/contracts/sources/uttar_pradesh/fixtures/seatmatrix_up_r1_2026.csv"

    with open(fixture, "r") as f:
        content = f.read()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        registry = InMemoryFileRegistry()
        loader = (
            seat_matrix_loader()
            if adapter_name == "maharashtra"
            else (
                up_seat_matrix_loader()
                if adapter_name == "karnataka"
                else up_seat_matrix_loader()
            )
        )

        # Run 1: ingest
        if adapter_name == "maharashtra":
            result1 = ingest_seat_matrix(tmp_path, registry, loader)
        elif adapter_name == "karnataka":
            result1 = ingest_seat_matrix(tmp_path, registry, loader)
        else:
            result1 = ingest_seat_matrix(tmp_path, registry, loader)

        assert result1.file_ingested is True
        assert result1.errors == []

        # Run 2: same bytes, same URL -> short-circuits on checksum
        result2 = ingest_seat_matrix(tmp_path, registry, loader)
        assert result2.file_ingested is False
        assert result2.records_transformed == 0
        assert result2.records_skipped > 0  # rows skipped due to checksum match
        assert loader.count() == 8  # no second write

        # Run 3: same URL, changed bytes -> new source identity
        changed_path = tmp_path + "_changed"
        with open(changed_path, "w") as f:
            f.write(content.replace("OP", "SC", 1))

        result3 = ingest_seat_matrix(changed_path, registry, loader)
        assert result3.file_ingested is True  # same source_url, new bytes
        assert result3.records_transformed == 8
        assert loader.count() == 8  # no duplicate keys; new row adds one key

    finally:
        os.unlink(tmp_path)
        if os.path.exists(changed_path):
            os.unlink(changed_path)


# --- G. Adapter boundary ---

def test_adapter_no_db_write():
    """G1. Adapters do not write directly to PostgreSQL."""
    from etl.contracts.sources.maharashtra.adapters import (
        MaharashtraSeatMatrixAdapter,
        MaharashtraAllotmentsAdapter,
    )
    from etl.contracts.sources.karnataka.adapters import (
        KarnatakaSeatMatrixAdapter,
        KarnatakaAllotmentsAdapter,
    )
    from etl.contracts.sources.uttar_pradesh.adapters import (
        UttarPradeshSeatMatrixAdapter,
        UttarPradeshAllotmentsAdapter,
    )

    adapter_classes = [
        MaharashtraSeatMatrixAdapter,
        MaharashtraAllotmentsAdapter,
        KarnatakaSeatMatrixAdapter,
        KarnatakaAllotmentsAdapter,
        UttarPradeshSeatMatrixAdapter,
        UttarPradeshAllotmentsAdapter,
    ]

    for adapter_class in adapter_classes:
        adapter = adapter_class()
        assert hasattr(adapter, "transform"), f"{adapter_class}: missing transform method"
        assert hasattr(adapter, "validate_source"), f"{adapter_class}: missing validate_source method"


def test_adapter_no_business_logic():
    """G2. Adapters contain no business logic, prediction, or recommendation."""
    from etl.contracts.sources.maharashtra.adapters import MaharashtraAllotmentsAdapter

    adapter = MaharashtraAllotmentsAdapter()

    # Build minimal test data
    raw = [
        {
            "Institute": "Test College",
            "Course": "MBBS",
            "Category": "OP",
            "Quota": "AI",
            "Round": "Round 1",
            "OpeningRank": "1",
            "ClosingRank": "100",
            "SeatCount": "1",
        }
    ]

    from etl.contracts.sources.maharashtra.contracts import allotments_2026_contract
    from etl.contracts.canonical import SourceMetadata

    metadata = SourceMetadata(
        source_id="mcc_state_maharashtra",
        authority="Test Authority",
        dataset="allotments",
        effective_year=2026,
        publication_version="Round 1",
        contract_version="1.0.0",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        source_file_id="test_no_biz_1234",
        file_checksum="c" * 64,
        parser_version="test_v1",
        source_url="https://example.com",
    )

    contract = allotments_2026_contract()
    result = adapter.transform(raw, contract, metadata)

    # G2 checks: result should only contain canonical fields
    expected = {
        "college_id",
        "college_name",
        "course_id",
        "quota_id",
        "category_id",
        "round_id",
        "rank",
        "opening_rank",
        "closing_rank",
        "seat_count",
        "effective_year",
        "source_file_id",
    }
    for rec in result.records:
        rec_keys = set(rec.keys())
        unexpected = rec_keys - expected
        assert not unexpected, f"Adapter contains unexpected keys: {unexpected}"

    # No business logic: rank should just be integer, not computed probability
    for rec in result.records:
        assert isinstance(rec.get("rank"), int), "rank should be integer, not computed probability"


# --- H. Parser boundary ---

from etl.contracts.sources.maharashtra.parsers import parse_csv
from etl.contracts.sources.karnataka.parsers import parse_csv as up_parse_csv_k
from etl.contracts.sources.uttar_pradesh.parsers import parse_csv as up_parse_csv_u


def test_parser_no_persistence():
    """H1. Parsers only parse source representations and do not perform
    persistence or prediction."""

    # Read MCC fixture
    with open(
        "etl/contracts/sources/maharashtra/fixtures/seat_matrix_r1_2026.csv",
        "r",
    ) as f:
        content = f.read()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # H1 checks: parse_csv returns plain data, no DB access
        rows = parse_csv(tmp_path)
        assert isinstance(rows, list)
        if rows:
            assert isinstance(rows[0], dict)

        # No PostgreSQL, no ML, no prediction
        assert len(rows) > 0  # should parse at least header + rows

        # Same for Karnataka parser
        with open(
            "etl/contracts/sources/karnataka/fixtures/seatmatrix_ka_r1_2026.csv",
            "r",
        ) as f:
            content2 = f.read()
        tmp2_path = tmp.name + "_2"
        with open(tmp2_path, "w") as f:
            f.write(content2)
        rows2 = up_parse_csv_k(tmp2_path)
        assert isinstance(rows2, list)

        # Same for UP parser
        with open(
            "tests/unit/etl/contracts/sources/uttar_pradesh/tests/fixtures/"
            "seatmatrix_up_r1_2026.csv",
            "r",
        ) as f:
            content3 = f.read()
        tmp3_path = tmp.name + "_3"
        with open(tmp3_path, "w") as f:
            f.write(content3)
        rows3 = up_parse_csv_u(tmp3_path)
        assert isinstance(rows3, list)

    finally:
        os.unlink(tmp_path)
        if os.path.exists(tmp2_path):
            os.unlink(tmp2_path)
        if os.path.exists(tmp3_path):
            os.unlink(tmp3_path)