"""Domain entities — the building blocks of the admission-intelligence model.

Entities are pure data structures with **no infrastructure imports and no
business rules that depend on the outside world**. They validate their own
invariants (rank ranges, budget sanity) and expose thin, self-contained
behaviour (e.g. ``College.is_within_budget``). Cross-entity orchestration
lives in the application layer, not here.
"""

from app.domain.entities.allotment import AllotmentRecord
from app.domain.entities.candidate import CandidateProfile
from app.domain.entities.college import College
from app.domain.entities.recommendation import Recommendation

__all__ = [
    "AllotmentRecord",
    "CandidateProfile",
    "College",
    "Recommendation",
]
