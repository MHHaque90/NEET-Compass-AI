"""MCC abbreviation vocabulary and normalisation helpers.

The Medical Counselling Committee (MCC) does NOT publish a single stable
abbreviation scheme across its documents. The seat-matrix PDFs and the
allotment result CSVs use different tokens for the same concept, for example:

* Category "open seat" is ``OP`` in the seat matrix but ``GN`` in the
  allotment file.
* The PwD marker is ``PH`` in the seat matrix but ``PwD`` in the allotment
  file.
* Seat-matrix quotas are full names (``All India``, ``Open Seat Quota``)
  whereas the allotment file uses two-letter codes (``AI``, ``SO``).

These mappers collapse that source vocabulary onto the canonical
``category_id`` / ``quota_id`` strings declared by the canonical
``SeatMatrix`` / ``Allotment`` dataclasses. They are intentionally small,
total functions (unknown input -> best-effort slug) so ingestion of a
future MCC release never hard-fails on a new quota code we simply did not
enumerate.
"""

from __future__ import annotations

import re
from typing import Final

# --- Seat-matrix "Category" column -------------------------------------
# Values look like "BC NO", "OP PH", "EW NO" ...
# Base token -> canonical category_id (no PwD suffix).
SEAT_MATRIX_CATEGORY_BASE: Final[dict[str, str]] = {
    "OP": "gn",
    "BC": "bc",
    "EW": "ew",
    "SC": "sc",
    "ST": "st",
}

# Seat-matrix "Quota" column -> canonical quota_id.
SEAT_MATRIX_QUOTA_MAP: Final[dict[str, str]] = {
    "All India": "ai",
    "All India except Central / University": "ai",
    "Open Seat Quota": "so",
}

# --- Allotment-file "Category" column ----------------------------------
# Values look like "GN", "BC PwD", "ST PwD" ...
ALLOTMENT_CATEGORY_BASE: Final[dict[str, str]] = {
    "GN": "gn",
    "BC": "bc",
    "EW": "ew",
    "SC": "sc",
    "ST": "st",
}

# Allotment-file "Quota" column is a two-letter abbreviation; canonical id
# is the abbreviation lower-cased (AI -> ai, SO -> so, AM -> am, ...).
ALLOTMENT_QUOTA_ABBREVIATIONS: Final[frozenset[str]] = frozenset(
    {
        "SA", "SI", "AM", "AI", "BS", "BD", "BW", "PW", "PS", "DW", "IW",
        "DU", "EN", "ES", "FQ", "JP", "IP", "JM", "JI", "MM", "JO", "MJ",
        "JS", "MW", "NR", "AN", "JN", "SO",
    }
)

# Branch -> canonical course id (first token lower-cased).
_COURSE_FIRST_TOKEN: Final[dict[str, str]] = {
    "MBBS": "mbbs",
    "BDS": "bds",
    "B.Sc": "bsc_nursing",
}

# Trailing college code, e.g. "...Port Blair-744104 (200101)" -> "200101".
_COLLEGE_CODE_RE: Final[re.Pattern[str]] = re.compile(r"\((?P<code>\d{4,7})\)\s*$")


def _slug_token(token: str) -> str:
    """Lower-case, underscore-joined slug of a free-text token."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", token.strip()).strip("_").lower()
    return cleaned if cleaned else "unknown"


def normalize_seat_matrix_category(raw: str) -> tuple[str, bool]:
    """Normalise a seat-matrix ``Category`` value.

    Returns ``(category_id, pwd)``. ``PH`` suffix sets ``pwd`` and is folded
    into ``category_id`` as a ``_pwd`` suffix to keep the composite unique key
    faithful to the source row granularity.
    """
    token = raw.strip()
    pwd = token.endswith(" PH")
    if pwd:
        token = token.removesuffix(" PH").strip()
    elif token.endswith(" NO"):
        token = token.removesuffix(" NO").strip()
    base = SEAT_MATRIX_CATEGORY_BASE.get(token, _slug_token(token))
    category_id = f"{base}_pwd" if pwd else base
    return category_id, pwd


def normalize_allotment_category(raw: str) -> tuple[str, bool]:
    """Normalise an allotment-file ``Category`` value.

    Returns ``(category_id, pwd)``. ``PwD`` suffix sets ``pwd``.
    """
    token = raw.strip()
    pwd = token.endswith(" PwD")
    if pwd:
        token = token.removesuffix(" PwD").strip()
    base = ALLOTMENT_CATEGORY_BASE.get(token, _slug_token(token))
    category_id = f"{base}_pwd" if pwd else base
    return category_id, pwd


def normalize_seat_matrix_quota(raw: str) -> str:
    """Normalise a seat-matrix ``Quota`` value (full names -> short codes)."""
    token = raw.strip()
    mapped = SEAT_MATRIX_QUOTA_MAP.get(token)
    if mapped is not None:
        return mapped
    return _slug_token(token.split("/")[0].strip())


def normalize_allotment_quota(raw: str) -> str:
    """Normalise an allotment-file ``Quota`` abbreviation.

    MCC allotment files use a two-letter code (e.g. ``AI``, ``SO``); the
    canonical id is the code lower-cased. Anything unexpected is slugged.
    """
    token = raw.strip()
    if token in ALLOTMENT_QUOTA_ABBREVIATIONS:
        return token.lower()
    if " " in token or "/" in token:
        return _slug_token(token.split()[0])
    return _slug_token(token)


def normalize_course(raw: str) -> str:
    """Normalise a ``Branch`` / ``Course`` value to a canonical course id."""
    token = raw.strip()
    first = token.split()[0] if token else ""
    if first in _COURSE_FIRST_TOKEN:
        return _COURSE_FIRST_TOKEN[first]
    return _slug_token(first) if first else "unknown"


def extract_college_id(institute: str) -> str:
    """Extract the MCC college code from a full institute address string.

    MCC embeds the college code in trailing parentheses, e.g.
    ``"...ATLANTA POINT, PORT BLAIR-744104 (200101)"`` -> ``200101``.
    Falls back to a slug of the string when no code is present.
    """
    text = institute.strip()
    match = _COLLEGE_CODE_RE.search(text)
    if match:
        return match.group("code")
    return _slug_token(text)


def extract_college_name(institute: str) -> str:
    """Strip the trailing college code block from an institute address line."""
    text = institute.strip()
    match = _COLLEGE_CODE_RE.search(text)
    name = text[: match.start()].strip() if match else text
    return name.replace("\n", " ").replace("\r", " ").strip()


def split_state(institute: str) -> str:
    """Placeholder kept for downstream use; seat matrix carries ``StateName``."""
    return ""
