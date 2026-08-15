"""Tests for MCC abbreviation normalisation (the vocab mappers)."""

from __future__ import annotations

from etl.contracts.sources.mcc.mappings import (
    extract_college_id,
    extract_college_name,
    normalize_allotment_category,
    normalize_allotment_quota,
    normalize_course,
    normalize_seat_matrix_category,
    normalize_seat_matrix_quota,
)


def test_seat_matrix_category_normalisation() -> None:
    cases = {
        "BC NO": ("bc", False),
        "BC PH": ("bc_pwd", True),
        "EW NO": ("ew", False),
        "EW PH": ("ew_pwd", True),
        "OP NO": ("gn", False),
        "OP PH": ("gn_pwd", True),
        "SC NO": ("sc", False),
        "ST NO": ("st", False),
        "ST PH": ("st_pwd", True),
    }
    for raw, expected in cases.items():
        assert normalize_seat_matrix_category(raw) == expected, raw


def test_seat_matrix_quota_normalisation() -> None:
    assert normalize_seat_matrix_quota("All India") == "ai"
    assert normalize_seat_matrix_quota("Open Seat Quota") == "so"
    assert normalize_seat_matrix_quota("All India except Central / University") == "ai"


def test_course_normalisation() -> None:
    assert normalize_course("MBBS (MBBS)") == "mbbs"
    assert normalize_course("BDS (BDS)") == "bds"


def test_college_code_extraction() -> None:
    institute = (
        "ASCSR Govt Medical College, Nellore, OPP. TO AC SUBBA REDDY STADIUM "
        "DARGAMITTA NELLORE, / SPSR NELLORE DISTRICT, ANDHRA PRADESH (200446)"
    )
    assert extract_college_id(institute) == "200446"
    assert extract_college_name(institute).startswith("ASCSR Govt Medical College")
    assert "200446" not in extract_college_name(institute)


def test_college_code_extraction_without_code() -> None:
    name = extract_college_name("No Code Institute")
    assert name == "No Code Institute"
    assert extract_college_id("No Code Institute").startswith("no_code_institute")


def test_allotment_category_normalisation() -> None:
    cases = {
        "GN": ("gn", False),
        "GN PwD": ("gn_pwd", True),
        "BC": ("bc", False),
        "BC PwD": ("bc_pwd", True),
        "ST PwD": ("st_pwd", True),
        "SC": ("sc", False),
    }
    for raw, expected in cases.items():
        assert normalize_allotment_category(raw) == expected, raw


def test_allotment_quota_normalisation() -> None:
    assert normalize_allotment_quota("AI") == "ai"
    assert normalize_allotment_quota("SO") == "so"
    assert normalize_allotment_quota("AM") == "am"
    assert normalize_allotment_quota("IP") == "ip"
