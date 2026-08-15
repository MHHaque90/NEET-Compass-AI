"""Domain enumerations.

These are the canonical, validated vocabulary of the NEET counselling
domain. Values are stored in the database as their `.value` strings and
validated at the application boundary (Pydantic), so the persistence layer
never has to guess the meaning of a free-text column.
"""

from __future__ import annotations

from enum import StrEnum


class Category(StrEnum):
    """Socio-educational reservation categories used in NEET counselling."""

    GENERAL = "GENERAL"
    GENERAL_EWS = "GENERAL_EWS"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"


class QuotaType(StrEnum):
    """Whether the seat pool is All India Quota or State Domicile Quota."""

    AIQ = "AIQ"
    STATE = "STATE"


class Gender(StrEnum):
    """NEET publishes separate closing ranks for Female-only seats."""

    NEUTRAL = "NEUTRAL"
    MALE = "MALE"
    FEMALE = "FEMALE"


class PwdStatus(StrEnum):
    """Persons-with-disabilities reservation flag."""

    NONE = "NONE"
    PWD = "PWD"


class Course(StrEnum):
    MBBS = "MBBS"
    BDS = "BDS"


class CollegeOwnership(StrEnum):
    """Ownership/management type drives fee structure and AIQ participation."""

    GOVERNMENT = "GOVERNMENT"
    GOVERNMENT_AIDED = "GOVERNMENT_AIDED"
    CENTRAL = "CENTRAL"  # e.g. AIIMS, JIPMER
    DEEMED = "DEEMED"
    PRIVATE = "PRIVATE"


class CounsellingRound(StrEnum):
    """Counselling rounds. `STRAY` is the open stray-vacancy round."""

    ROUND_1 = "ROUND_1"
    ROUND_2 = "ROUND_2"
    ROUND_3 = "ROUND_3"
    ROUND_4 = "ROUND_4"
    ROUND_5 = "ROUND_5"
    STRAY = "STRAY"


class MinorityStatus(StrEnum):
    """Minority-institution quota eligibility."""

    NONE = "NONE"
    MINORITY = "MINORITY"


class IndiaState(StrEnum):
    """Indian states and union territories (NEET counselling jurisdictions)."""

    ANDHRA_PRADESH = "ANDHRA_PRADESH"
    ARUNACHAL_PRADESH = "ARUNACHAL_PRADESH"
    ASSAM = "ASSAM"
    BIHAR = "BIHAR"
    CHHATTISGARH = "CHHATTISGARH"
    GOA = "GOA"
    GUJARAT = "GUJARAT"
    HARYANA = "HARYANA"
    HIMACHAL_PRADESH = "HIMACHAL_PRADESH"
    JHARKHAND = "JHARKHAND"
    KARNATAKA = "KARNATAKA"
    KERALA = "KERALA"
    MADHYA_PRADESH = "MADHYA_PRADESH"
    MAHARASHTRA = "MAHARASHTRA"
    MANIPUR = "MANIPUR"
    MEGHALAYA = "MEGHALAYA"
    MIZORAM = "MIZORAM"
    NAGALAND = "NAGALAND"
    ODISHA = "ODISHA"
    PUNJAB = "PUNJAB"
    RAJASTHAN = "RAJASTHAN"
    SIKKIM = "SIKKIM"
    TAMIL_NADU = "TAMIL_NADU"
    TELANGANA = "TELANGANA"
    TRIPURA = "TRIPURA"
    UTTAR_PRADESH = "UTTAR_PRADESH"
    UTTARAKHAND = "UTTARAKHAND"
    WEST_BENGAL = "WEST_BENGAL"
    DELHI = "DELHI"
    JAMMU_AND_KASHMIR = "JAMMU_AND_KASHMIR"
    LADAKH = "LADAKH"
    PUDUCHERRY = "PUDUCHERRY"
    ANDAMAN_AND_NICOBAR = "ANDAMAN_AND_NICOBAR"
    CHANDIGARH = "CHANDIGARH"
    DADRA_AND_NAGAR_HAVELI = "DADRA_AND_NAGAR_HAVELI"
    DAMAN_AND_DIU = "DAMAN_AND_DIU"
    LAKSHADWEEP = "LAKSHADWEEP"


class RecommendationStatus(StrEnum):
    """Lifecycle of a generated recommendation record."""

    PENDING = "PENDING"  # requested, engine not yet run
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"  # produced with partial data / fallback engine
    FAILED = "FAILED"
