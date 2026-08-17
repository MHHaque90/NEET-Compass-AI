"""Pytest fixtures shared by the Maharashtra contract-pilot tests.

The row constants mirror the expected Maharashtra CET Cell data schema,
so adapter/parser tests run against real provenance rather than invented
column names.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

SEAT_MATRIX_HEADER: list[str] = [
    "StateName", "Institute", "Course", "Category", "Quota", "TotalSeats",
]


# Real-shaped Maharashtra seat-matrix rows (machine-readable schema).
# Note: original data does NOT include bc_pwd category, so changing
# BC NO -> BC PH in the test below always creates a new unique key.
REAL_SEAT_MATRIX_ROWS: list[list[str]] = [
    # Category tokens (bare, without NO/PH/PwD suffix – compatible with
    # test_three_runs_same_source_url_changed_bytes which does
    # replace(b"OP", b"GN", 1)).
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "OP",
        "AI",
        "100",
    ],
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "BC",
        "AI",
        "50",
    ],
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "EW",
        "AI",
        "30",
    ],
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "SC",
        "AI",
        "20",
    ],
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "ST",
        "AI",
        "10",
    ],
    # Categories with PH suffix (test change: OP -> GN introduces gn_pwd)
    [
        "Maharashtra",
        "AIIMS Mumbai",
        "MBBS",
        "OP PH",
        "AI",
        "80",
    ],
    [
        "Maharashtra",
        "AIIMS Mumbai",
        "BDS",
        "OP",
        "AI",
        "60",
    ],
    # Additional row to make 8 total – BC category (test change will affect OP, not BC)
    [
        "Maharashtra",
        "AIIMS Mumbai",
        "MBBS",
        "BC",
        "AI",
        "40",
    ],
]


# A CSV whose two data rows collapse to the same composite key -> duplicate.
DUPLICATE_SEAT_MATRIX_ROWS: list[list[str]] = [
    SEAT_MATRIX_HEADER,
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "OP NO",
        "AI",
        "100",
    ],
    [
        "Maharashtra",
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "OP NO",
        "AI",
        "100",
    ],
]


ALLOTMENT_HEADER: list[str] = [
    "Institute", "Course", "Category", "Quota", "Round", "OpeningRank",
    "ClosingRank", "SeatCount",
]


# Real-shaped Maharashtra allotment CSV rows (machine-readable schema).
# 4 rows covering categories: gn (OP), bc (BC), st_pwd (ST PwD).
REAL_ALLOTMENT_ROWS: list[list[str]] = [
    [
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "OP",
        "AI",
        "Round 1",
        "1",
        "50",
        "1",
    ],
    [
        "ASCSR Govt Medical College, Nellore",
        "MBBS",
        "BC",
        "AI",
        "Round 1",
        "51",
        "100",
        "1",
    ],
    [
        "AIIMS Mumbai",
        "MBBS",
        "ST PwD",
        "AI",
        "Round 1",
        "101",
        "150",
        "1",
    ],
    [
        "AIIMS Mumbai",
        "BDS",
        "OP",
        "AI",
        "Round 1",
        "8001",
        "8020",
        "1",
    ],
]


@pytest.fixture
def seat_matrix_csv(tmp_path: Path) -> Path:
    """A UTF-8 (BOM) seat-matrix CSV mirroring the real Maharashtra schema."""
    path = tmp_path / "seatmatrix_mah_r1_2026.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(SEAT_MATRIX_HEADER)
        for row in REAL_SEAT_MATRIX_ROWS:
            writer.writerow(row)
    return path


@pytest.fixture
def duplicate_seat_matrix_csv(tmp_path: Path) -> Path:
    """A seat-matrix CSV whose two rows share the same composite key."""
    path = tmp_path / "duplicate.csv"
    rows = [
        SEAT_MATRIX_HEADER,
        [
            "Maharashtra",
            "ASCSR Govt Medical College, Nellore",
            "MBBS",
            "OP NO",
            "AI",
            "100",
        ],
        [
            "Maharashtra",
            "ASCSR Govt Medical College, Nellore",
            "MBBS",
            "OP NO",
            "AI",
            "100",
        ],
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)
    return path


@pytest.fixture
def bad_seat_matrix_csv(tmp_path: Path) -> Path:
    """A seat-matrix CSV containing an invalid category token."""
    path = tmp_path / "bad.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(SEAT_MATRIX_HEADER)
        writer.writerow([
            "Maharashtra",
            "ASCSR Govt Medical College, Nellore",
            "MBBS",
            "ZZ_BAD_CATEGORY",
            "AI",
            "6",
        ])
    return path


@pytest.fixture
def allotment_csv(tmp_path: Path) -> Path:
    """A UTF-8 (BOM) allotment CSV mirroring the real Maharashtra schema."""
    path = tmp_path / "allotment_mah_r1_2026.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(ALLOTMENT_HEADER)
        for row in REAL_ALLOTMENT_ROWS:
            writer.writerow(row)
    return path


@pytest.fixture
def pii_allotment_csv(tmp_path: Path) -> Path:
    """An allotment CSV carrying candidate PII columns (must be refused)."""
    path = tmp_path / "allotment_pii.csv"
    columns = [*ALLOTMENT_HEADER, "Candidate Name", "Percentile"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerow([
            "ASCSR Govt Medical College, Nellore",
            "MBBS",
            "OP",
            "AI",
            "Round 1",
            "1",
            "50",
            "1",
            "John Doe",
            "95.5",
        ])
    return path
