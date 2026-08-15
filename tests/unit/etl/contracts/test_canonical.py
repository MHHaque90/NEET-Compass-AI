"""Tests for canonical models."""

from etl.contracts.canonical import (
    Allotment,
    Category,
    College,
    Course,
    District,
    Fee,
    HistoricalCutoff,
    Quota,
    Round,
    SeatMatrix,
    SourceMetadata,
    State,
)


class TestCanonicalModels:
    """Tests for canonical model dataclasses."""

    def test_college(self) -> None:
        c = College(college_id="c1", college_name="AIIMS")
        assert c.college_id == "c1"

    def test_course(self) -> None:
        c = Course(course_id="cr1", course_name="MBBS")
        assert c.course_name == "MBBS"

    def test_seat_matrix(self) -> None:
        s = SeatMatrix(
            college_id="c1",
            course_id="cr1",
            quota_id="q1",
            category_id="cat1",
            total_seats=100,
            effective_year=2026,
        )
        assert s.total_seats == 100

    def test_allotment(self) -> None:
        a = Allotment(college_id="c1", course_id="cr1", effective_year=2026)
        assert a.college_id == "c1"

    def test_historical_cutoff(self) -> None:
        h = HistoricalCutoff(
            college_id="c1",
            course_id="cr1",
            year=2026,
            round_id="r1",
            quota_id="q1",
            category_id="cat1",
        )
        assert h.year == 2026

    def test_fee(self) -> None:
        f = Fee(college_id="c1", course_id="cr1", quota_id="q1", fee_amount=50000.0)
        assert f.fee_amount == 50000.0

    def test_quota(self) -> None:
        q = Quota(quota_id="q1", quota_name="AIQ")
        assert q.quota_name == "AIQ"

    def test_category(self) -> None:
        c = Category(category_id="cat1", category_name="General")
        assert c.category_name == "General"

    def test_round(self) -> None:
        r = Round(round_id="r1", round_name="Round 1")
        assert r.round_name == "Round 1"

    def test_state(self) -> None:
        s = State(state_id="s1", state_name="Delhi")
        assert s.state_name == "Delhi"

    def test_district(self) -> None:
        d = District(district_id="d1", district_name="New Delhi", state_id="s1")
        assert d.state_id == "s1"

    def test_source_metadata(self) -> None:
        m = SourceMetadata(
            source_id="mcc",
            authority="mcc",
            dataset="allotments",
            effective_year=2026,
            publication_version="1.0",
            contract_version="1.0.0",
            retrieval_timestamp="2026-01-01T00:00:00Z",
        )
        assert m.source_id == "mcc"
