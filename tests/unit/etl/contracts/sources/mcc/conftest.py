"""Pytest fixtures shared by the MCC contract-pilot tests.

The row constants mirror the real MCC 2025 seat-matrix PDF tables (AIQ +
AIIMS cycles) and the MCC allotment CSV schema, so adapter/parser tests run
against real provenance rather than invented column names.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pytest

SEAT_MATRIX_HEADER: list[str] = [
    "StateName", "InstituteType", "Institute", "Quota", "Branch", "Category", "TotalSeats",
]

# Real rows extracted from seatmatrix_aiq_r1_2025.pdf + seatmatrix_aiims_bhu_jipmer_r1_2025.pdf.
# Institute text carries the MCC college code in trailing parentheses.
REAL_SEAT_MATRIX_ROWS: list[list[str]] = [
    [
        "Andaman And Nicobar Islands",
        "All India except Central / University",
        "Andaman and Nicobar Islands Institute of Medical S, Director ANIIMS, "
        "DHS Annexe Building, / Atlanta Point, Port Blair-744104 (200101)",
        "All India",
        "MBBS (MBBS)",
        "BC NO",
        "5",
    ],
    [
        "Andaman And Nicobar Islands",
        "All India except Central / University",
        "Andaman and Nicobar Islands Institute of Medical S, Director ANIIMS, "
        "DHS Annexe Building, / Atlanta Point, Port Blair-744104 (200101)",
        "All India",
        "MBBS (MBBS)",
        "EW NO",
        "2",
    ],
    [
        "Andaman And Nicobar Islands",
        "All India except Central / University",
        "Andaman and Nicobar Islands Institute of Medical S, Director ANIIMS, "
        "DHS Annexe Building, / Atlanta Point, Port Blair-744104 (200101)",
        "All India",
        "MBBS (MBBS)",
        "SC NO",
        "3",
    ],
    [
        "Andaman And Nicobar Islands",
        "All India except Central / University",
        "Andaman and Nicobar Islands Institute of Medical S, Director ANIIMS, "
        "DHS Annexe Building, / Atlanta Point, Port Blair-744104 (200101)",
        "All India",
        "MBBS (MBBS)",
        "ST NO",
        "2",
    ],
    [
        "Andhra Pradesh",
        "All India except Central / University",
        "ASCSR Govt Medical College, Nellore, OPP. TO AC SUBBA REDDY STADIUM "
        "DARGAMITTA NELLORE, / SPSR NELLORE DISTRICT, ANDHRA PRADESH (200446)",
        "All India",
        "MBBS (MBBS)",
        "BC NO",
        "6",
    ],
    [
        "Andhra Pradesh",
        "All India except Central / University",
        "ASCSR Govt Medical College, Nellore, OPP. TO AC SUBBA REDDY STADIUM "
        "DARGAMITTA NELLORE, / SPSR NELLORE DISTRICT, ANDHRA PRADESH (200446)",
        "All India",
        "MBBS (MBBS)",
        "BC PH",
        "1",
    ],
    [
        "Andhra Pradesh",
        "All India except Central / University",
        "ASCSR Govt Medical College, Nellore, OPP. TO AC SUBBA REDDY STADIUM "
        "DARGAMITTA NELLORE, / SPSR NELLORE DISTRICT, ANDHRA PRADESH (200446)",
        "Open Seat Quota",
        "MBBS (MBBS)",
        "OP NO",
        "10",
    ],
    [
        "Andhra Pradesh",
        "All India Institute Of Medical/Science(AIIMS)",
        "AIIMS Mangalagiri, ALL INDIA INSTITUTE OF MEDICAL / SCIENCES NEAR "
        "TADEPALLI MANGALAGIRI GUNTUR (Dt), / ANDHRA PRADESH (200510)",
        "Open Seat Quota",
        "MBBS (MBBS)",
        "OP NO",
        "46",
    ],
]

# A CSV whose two data rows collapse to the same composite key -> duplicate.
DUPLICATE_SEAT_MATRIX_ROWS: list[list[str]] = [
    SEAT_MATRIX_HEADER,  # re-used as a data row is avoided; see fixture below
]


ALLOTMENT_HEADER: list[str] = [
    "Institute Code", "Institute Name", "Course", "Quota", "Category",
    "Round", "Rank", "Score", "Seats",
]

# Real-shaped MCC allotment CSV rows (machine-readable schema, per-round file).
REAL_ALLOTMENT_ROWS: list[list[str]] = [
    [
        "200510", "AIIMS Mangalagiri, Guntur", "MBBS (MBBS)", "AI", "GN",
        "Round 3", "42531", "188.50", "1",
    ],
    [
        "200510", "AIIMS Mangalagiri, Guntur", "MBBS (MBBS)", "AI", "GN PwD",
        "Round 3", "510024", "142.25", "1",
    ],
    [
        "200446", "ASCSR Govt Medical College, Nellore", "MBBS (MBBS)", "SO",
        "BC", "Round 3", "98214", "176.00", "1",
    ],
    [
        "200446", "ASCSR Govt Medical College, Nellore", "BDS (BDS)", "SO",
        "SC", "Round 3", "213410", "130.50", "1",
    ],
]


@pytest.fixture
def seat_matrix_csv(tmp_path: Path) -> Path:
    """A UTF-8 (BOM) seat-matrix CSV mirroring the real MCC AIQ/AIIMS tables."""
    path = tmp_path / "seatmatrix_aiq_r1_2025.csv"
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
            "Andhra Pradesh", "All India except Central / University",
            "ASCSR Govt Medical College, Nellore (200446)", "All India",
            "MBBS (MBBS)", "BC NO", "6",
        ],
        [
            "Andhra Pradesh", "All India except Central / University",
            "ASCSR Govt Medical College, Nellore (200446)", "All India",
            "MBBS (MBBS)", "BC NO", "6",
        ],
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)
    return path


@pytest.fixture
def bad_seat_matrix_csv(tmp_path: Path) -> Path:
    """A seat-matrix CSV containing an invalid quota category token."""
    path = tmp_path / "bad.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(SEAT_MATRIX_HEADER)
        writer.writerow([
            "Andhra Pradesh", "All India except Central / University",
            "ASCSR Govt Medical College, Nellore (200446)", "All India",
            "MBBS (MBBS)", "ZZ BAD CATEGORY", "6",
        ])
    return path


@pytest.fixture
def allotment_csv(tmp_path: Path) -> Path:
    """A UTF-8 (BOM) allotment CSV mirroring the real MCC schema."""
    path = tmp_path / "allotment_r3_2025.csv"
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
    columns = [*ALLOTMENT_HEADER, "Candidate Name", "Percentile", "Contact No"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerow([
            "200510", "AIIMS Mangalagiri", "MBBS (MBBS)", "AI", "GN",
            "Round 3", "42531", "188.50", "1", "John Doe", "95.5", "9876543210",
        ])
    return path


@pytest.fixture
def sample_seat_matrix_pdf() -> Path:
    """Path to a real MCC seat-matrix PDF, when available in the environment."""
    env = os.environ.get("MCC_SAMPLE_SEATMATRIX_PDF")
    if not env or not Path(env).exists():
        pytest.skip("set MCC_SAMPLE_SEATMATRIX_PDF to exercise real PDF extraction")
    return Path(env)
