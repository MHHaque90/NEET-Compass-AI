"""File-based ETL sources (CSV and Excel)."""

from __future__ import annotations

import pandas as pd

from app.infrastructure.etl.sources.csv_source import CSVSource
from app.infrastructure.etl.sources.excel_source import ExcelSource


def test_csv_source_reads_header_rows(tmp_path) -> None:
    path = tmp_path / "cutoffs.csv"
    path.write_text(
        "Institute Code,Course,Closing Rank\nMYS-01,MBBS,2500\nMYS-02,BDS,4100\n",
        encoding="utf-8",
    )

    rows = list(CSVSource(str(path)).read())

    assert len(rows) == 2
    assert rows[0]["Institute Code"] == "MYS-01"
    assert rows[0]["Closing Rank"] == "2500"


def test_excel_source_reads_sheet(tmp_path) -> None:
    path = tmp_path / "cutoffs.xlsx"
    frame = pd.DataFrame({"Institute Code": ["MYS-01"], "Course": ["MBBS"], "Closing Rank": [2500]})
    frame.to_excel(path, index=False)

    rows = list(ExcelSource(str(path)).read())

    assert len(rows) == 1
    assert rows[0]["Course"] == "MBBS"
    assert rows[0]["Closing Rank"] == 2500


def test_excel_source_skips_header_offset(tmp_path) -> None:
    path = tmp_path / "junk.xlsx"
    frame = pd.DataFrame({"title": ["ALL INDIA QUOTA CUTOFF"]})
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, header=False, startrow=0)
        header = pd.DataFrame({"Institute Code": ["MYS-01"], "Course": ["MBBS"]})
        header.to_excel(writer, index=False, startrow=2)

    rows = list(ExcelSource(str(path), header_row=2).read())

    assert len(rows) == 1
    assert rows[0]["Institute Code"] == "MYS-01"
