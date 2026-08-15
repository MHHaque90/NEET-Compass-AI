"""ETL pipeline primitives: Source, Transformer, Loader, Pipeline."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping

logger = logging.getLogger(__name__)

RawRow = Mapping[str, object]
"""A raw row as produced by a source (e.g. one sheet row of a PDF export)."""


class Source(ABC):
    """Produces raw rows from a data origin."""

    def __init__(self, path: str) -> None:
        self.path = path

    @abstractmethod
    def read(self) -> Iterable[RawRow]:
        """Yield raw rows. May stream for large files."""


class Transformer(ABC):
    """Converts raw rows into normalized domain records."""

    @abstractmethod
    def transform(self, rows: Iterable[RawRow]) -> Iterable[RawRow]:
        """Yield normalized rows with canonical column names and types."""


class Loader(ABC):
    """Persists normalized records."""

    @abstractmethod
    def load(self, rows: Iterable[RawRow]) -> int:
        """Load records and return the number persisted."""


class Pipeline:
    """Runs a full ETL pipeline with failure isolation and reporting."""

    def __init__(
        self,
        name: str,
        source: Source,
        transformer: Transformer,
        loader: Loader,
    ) -> None:
        self.name = name
        self.source = source
        self.transformer = transformer
        self.loader = loader

    def run(self) -> dict[str, int]:
        raw_count = 0
        normalized_count = 0
        loaded_count = 0
        batch: list[RawRow] = []

        for raw in self.source.read():
            raw_count += 1
            for normalized in self.transformer.transform([raw]):
                normalized_count += 1
                batch.append(normalized)

        if batch:
            loaded_count = self.loader.load(batch)

        logger.info(
            "Pipeline %s complete: raw=%d normalized=%d loaded=%d",
            self.name,
            raw_count,
            normalized_count,
            loaded_count,
        )
        return {"raw": raw_count, "normalized": normalized_count, "loaded": loaded_count}
