"""Pytest fixtures shared by the Karnataka KEA contract-pilot tests.

The row constants mirror the expected KEA data schema, so adapter/parser tests
run against real provenance rather than invented column names.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


SEAT_MATRIX_HEADER: list[str] = [
    "Institute",
    "Course",
    "Category",
    "Quota",
    "TotalSeats",
]


# Real-shaped Karnataka KEA seat-matrix rows (machine-readable schema).
# Category tokens: GM, SC, ST, CAT-1, 2A, 3B
# Quota tokens: AI, SO
REAL_SEAT_MATRIX_ROWS: list[list[str]] = [
    [
        "RV College of Engineering",
        "MBBS",
        "GM",
        "AI",
        "150",
    ],
    [
        "RV College of Engineering",
        "MBBS",
        "SC",
        "AI",
        "50",
    ],
    [
        "RV College of Engineering",
        "MBBS",
        "ST",
        "AI",
        "10",
    ],
    [
        "RV College of Engineering",
        "MBBS",
        "CAT-1",
        "AI",
        "30",
    ],
    [
        "BMC Medical College",
        "BDS",
        "GM",
        "AI",
        "100",
    ],
    [
        "BMC Medical College",
        "BDS",
        "SC",
        "AI",
        "25",
    ],
    [
        "BMC Medical College",
        "BDS",
        "GM PwD",
        "AI",
        "5",
    ],
    [
        "BMC Medical College",
        "BDS",
        "ST",
        "SO",
        "8",
    ],
]


# A CSV whose two data rows collapse to the same composite key -> duplicate.
DUPLICATE_SEAT_MATRIX_ROWS: list[list[str]] = [
    SEAT_MATRIX_HEADER,
    [
        "RV College of Engineering",
        "MBBS",
        "GM",
        "AI",
        "150",
    ],
    [
        "RV College of Engineering",
        "MBBS",
        "GM",
        "AI",
        "150",
    ],
]


ALLOTMENT_HEADER: list[str] = [
    "Institute",
    "Course",
    "Category",
    "Quota",
    "Round",
    "OpeningRank",
    "ClosingRank",
    "SeatCount",


]


# Real-shaped Karnataka KEA allotment CSV rows (machine-readable schema).
# 4 rows covering categories: gn (GM), sc (SC), st_pwd (ST PwD), so (COMEDK/SO).
REAL_ALLOTMENT_ROWS: list[list[str]] = [
    [
        "RV College of Engineering",
        "MBBS",
        "GM",
        "AI",
        "Round 1",
        "1",
        "5000",
        "1",
    ],
    [
        "RV College of Engineering",
        "MBBS",
        "SC",
        "AI",
        "Round 1",
        "5001",
        "10000",
        "1",
    ],
    [
        "RV College of Engineering",
        "MBBS",
        "ST PwD",
        "AI",
        "Round 1",
        "10001",
        "15000",
        "1",
    ],
    [
        "RV College of Engineering",
        "BDS",
        "GM",
        "COMEDK",
        "Round 1",
        "8001",
        "8020",
        "1",
    ],
]


@pytest.fixture
def seat_matrix_csv(tmp_path: Path) -> Path:
    """A UTF-8 (BOM) seat-matrix CSV mirroring the real Karnataka KEA schema."""
    path = tmp_path / "seatmatrix_ka_r1_2026.csv"
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
            "RV College of Engineering",
            "MBBS",
            "GM",
            "AI",
            "150",
        ],
        [
            "RV College of Engineering",
            "MBBS",
            "GM",
            "AI",
            "150",
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
            "RV College of Engineering",
            "MBBS",
            "ZZ_BAD_CATEGORY",
            "AI",
            "6",
        ])
    return path


@pytest.fixture
def allotment_csv(tmp_path: Path) -> Path:
    """A UTF-8 (BOM) allotment CSV mirroring the real Karnataka KEA schema."""
    path = tmp_path / "allotment_ka_r1_2026.csv"
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
            "RV College of Engineering",
            "MBBS",
            "GM",
            "AI",
            "Round 1",
            "1",
            "5000",
            "1",
            "John Doe",
            "95.5",
        ])
    return path