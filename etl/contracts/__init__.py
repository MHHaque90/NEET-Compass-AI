"""Data Contracts & Source Compatibility Layer.

Sprint 2.5 - External data contracts that isolate
external counselling sources from the internal system.
"""

from etl.contracts.base import SourceContract
from etl.contracts.registry import ContractRegistry
from etl.contracts.version import ContractVersion

__all__ = ["ContractRegistry", "ContractVersion", "SourceContract"]
