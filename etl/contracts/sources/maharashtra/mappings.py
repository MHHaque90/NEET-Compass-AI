"""Maharashtra abbreviation vocabulary and normalisation helpers.

Maharashtra CET Cell uses category tokens (``OP``, ``GN``, ``BC``, etc.) and
quota names that map onto the canonical ``category_id`` / ``quota_id`` strings
declared by the canonical ``SeatMatrix`` / ``Allotment`` dataclasses.

Category tokens seen in Maharashtra sources:
  - ``OP``  -> ``gn``  (open/merit)
  - ``GN``  -> ``gn``  (general)
  - ``BC``  -> ``bc``  (backward class)
  - ``EW``  -> ``ew``  (ethnically weak)
  - ``SC``  -> ``sc``  (scheduled caste)
  - ``ST``  -> ``st``  (scheduled tribe)

Quota tokens seen in Maharashtra sources:
  - ``AI``    -> ``ai``  (All India)
  - ``MNG``   -> ``mm``  (Management/NRI)
  - ``SO``    -> ``so``  (State Open/Others)
"""

from __future__ import annotations

import re
from typing import Final

# --- Category token map ----------------------------------------------------
# Base token -> canonical category_id (no PwD suffix).
MAHARASHTRA_CATEGORY_BASE: Final[dict[str, str]] = {
    "OP": "gn",
    "GN": "gn",
    "BC": "bc",
    "EW": "ew",
    "SC": "sc",
    "ST": "st",
}


def _slug_token(token: str) -> str:
    """Lower-case, underscore-joined slug of a free-text token."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", token.strip()).strip("_").lower()
    return cleaned if cleaned else "unknown"


def normalize_maharashtra_category(raw: str) -> tuple[str, bool]:
    """Normalise a Maharashtra ``Category`` value.

    Returns ``(category_id, pwd)``. ``PH`` / ``PwD`` / ``NO`` suffix sets
    ``pwd`` and is stripped before the base token lookup, keeping the composite
    unique key faithful to the source row granularity.
    """
    token = raw.strip()
    pwd = token.endswith(" PwD") or token.endswith(" PH") or token.endswith(" NO")
    if pwd:
        token = token.removesuffix(" PwD").removesuffix(" PH").removesuffix(" NO").strip()
    base = MAHARASHTRA_CATEGORY_BASE.get(token, _slug_token(token))
    category_id = f"{base}_pwd" if pwd else base
    return category_id, pwd


def normalize_maharashtra_quota(raw: str) -> str:
    """Normalise a Maharashtra ``Quota`` value.

    Mappings:
      - ``AI``     -> ``ai``  (All India)
      - ``MNG``   -> ``mm``  (Management/NRI)
      - ``SO``    -> ``so``  (State Open)
      - others    -> slugged
    """
    token = raw.strip().upper()
    mapped = {
        "AI": "ai",
        "MNG": "mm",
        "SO": "so",
    }.get(token)
    if mapped is not None:
        return mapped
    return _slug_token(token)
