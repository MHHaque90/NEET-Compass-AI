"""ETL transformer + validator unit tests (no filesystem, no DB)."""

from __future__ import annotations

import pytest

from app.infrastructure.etl.transformers.allotment_transformer import AllotmentTransformer
from app.infrastructure.etl.validators import DataValidationError, validate_rows


def test_transformer_maps_columns_and_stamps_year() -> None:
    column_map = {
        "Institute Code": "college_code",
        "Course": "course",
        "Closing Rank": "closing_rank",
        "Opening Rank": "opening_rank",
    }
    transformer = AllotmentTransformer(column_map=column_map, year=2025)

    rows = list(
        transformer.transform(
            [
                {
                    "Institute Code": "MYS-01",
                    "Course": "MBBS",
                    "Opening Rank": "1,001",
                    "Closing Rank": "2,500",
                },
            ]
        )
    )
    assert len(rows) == 1
    assert rows[0] == {
        "college_code": "MYS-01",
        "course": "MBBS",
        "counselling_year": 2025,
        "opening_rank": 1001,
        "closing_rank": 2500,
    }


def test_transformer_skips_blank_and_rankless_rows() -> None:
    transformer = AllotmentTransformer(column_map={"Closing Rank": "closing_rank"}, year=2025)
    rows = list(transformer.transform([{}, {"Closing Rank": ""}]))
    assert rows == []


def test_validate_rows_accepts_wellformed() -> None:
    valid = [
        {
            "college_code": "MYS-01",
            "course": "MBBS",
            "counselling_year": 2025,
            "round_number": 1,
            "quota_type": "AIQ",
            "category": "GENERAL",
            "gender": "NEUTRAL",
            "opening_rank": 100,
            "closing_rank": 200,
        }
    ]
    rows = validate_rows(valid)
    assert len(rows) == 1
    assert rows[0].course.value == "MBBS"


def test_validate_rows_rejects_bad_rows_all_or_nothing() -> None:
    bad = [
        {
            "college_code": "X",
            "course": "MBBS",
            "counselling_year": 2025,
            "round_number": 1,
            "quota_type": "AIQ",
            "category": "NOT_A_CATEGORY",
            "gender": "NEUTRAL",
            "opening_rank": 100,
            "closing_rank": 200,
        }
    ]
    with pytest.raises(DataValidationError):
        validate_rows(bad)
