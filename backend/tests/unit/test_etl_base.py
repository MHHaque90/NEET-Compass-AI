"""ETL pipeline runner with fakes."""

from __future__ import annotations

from app.infrastructure.etl.base import Loader, Pipeline, Source, Transformer


class FakeSource(Source):
    def __init__(self, rows: list[dict]) -> None:
        super().__init__(path="fake://source")
        self._rows = rows

    def read(self):
        return iter(self._rows)


class FakeTransformer(Transformer):
    def transform(self, rows):
        for row in rows:
            yield {"tag": "x", **row}


class FakeLoader(Loader):
    def __init__(self) -> None:
        self.loaded: list[dict] = []

    def load(self, rows):
        self.loaded.extend(rows)
        return len(rows)


def test_pipeline_counts_and_loads() -> None:
    loader = FakeLoader()
    pipeline = Pipeline(
        name="test",
        source=FakeSource([{"a": 1}, {"a": 2}]),
        transformer=FakeTransformer(),
        loader=loader,
    )

    result = pipeline.run()

    assert result == {"raw": 2, "normalized": 2, "loaded": 2}
    assert loader.loaded == [{"tag": "x", "a": 1}, {"tag": "x", "a": 2}]


def test_pipeline_handles_empty_source() -> None:
    loader = FakeLoader()
    pipeline = Pipeline(
        name="test-empty",
        source=FakeSource([]),
        transformer=FakeTransformer(),
        loader=loader,
    )

    result = pipeline.run()

    assert result == {"raw": 0, "normalized": 0, "loaded": 0}
    assert loader.loaded == []
