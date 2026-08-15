"""Source-specific adapters package.

Sprint 3.1 implements the MCC (Medical Counselling Committee) contract pilot
for ``seat_matrix`` and ``allotments``. Future sprints add NMC, state
counselling committees, etc. New datasets extend this package; they must ship
a ``SourceContract``, a ``SourceAdapter``, and an ingestion pipeline that
returns a ``PipelineResult`` and is backed by a ``Loader``/``FileRegistry``
port so persistence and deduplication remain swappable.
"""
