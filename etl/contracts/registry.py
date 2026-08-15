"""Contract registry for registration and lookup."""

from __future__ import annotations

from etl.contracts.base import SourceContract
from etl.contracts.errors import ContractNotFoundError, IncompatibleVersionError
from etl.contracts.version import ContractVersion


class ContractRegistry:
    """Registry for managing source contracts.

    Supports registration and lookup by:
    - source_id
    - dataset
    - contract_version
    """

    def __init__(self) -> None:
        self._contracts: dict[str, dict[str, dict[str, SourceContract]]] = {}

    def register(self, contract: SourceContract) -> None:
        """Register a source contract."""
        source_key = contract.source_id
        dataset_key = contract.dataset
        version_key = str(contract.contract_version)

        if source_key not in self._contracts:
            self._contracts[source_key] = {}
        if dataset_key not in self._contracts[source_key]:
            self._contracts[source_key][dataset_key] = {}

        self._contracts[source_key][dataset_key][version_key] = contract

    def get_contract(
        self,
        source_id: str,
        dataset: str,
        version: str | None = None,
    ) -> SourceContract:
        """Get a registered contract.

        Args:
            source_id: Source identifier (e.g., 'mcc', 'nmc')
            dataset: Dataset name (e.g., 'allotments', 'seat_matrix')
            version: Optional version string. If None, returns latest.

        Returns:
            The matching SourceContract.

        Raises:
            ContractNotFoundError: If no contract matches.

        """
        if source_id not in self._contracts:
            raise ContractNotFoundError(source_id=source_id, dataset=dataset)

        if dataset not in self._contracts[source_id]:
            raise ContractNotFoundError(source_id=source_id, dataset=dataset)

        versions = self._contracts[source_id][dataset]

        if not versions:
            raise ContractNotFoundError(source_id=source_id, dataset=dataset)

        if version is None:
            return self._get_latest_version(versions)

        if version not in versions:
            raise ContractNotFoundError(source_id=source_id, dataset=dataset, version=version)

        return versions[version]

    def get_compatible_contract(
        self,
        source_id: str,
        dataset: str,
        required_version: ContractVersion,
    ) -> SourceContract:
        """Get a contract compatible with the required version.

        Raises:
            IncompatibleVersionError: If no compatible version found.

        """
        if source_id not in self._contracts:
            raise ContractNotFoundError(source_id=source_id, dataset=dataset)

        if dataset not in self._contracts[source_id]:
            raise ContractNotFoundError(source_id=source_id, dataset=dataset)

        versions = self._contracts[source_id][dataset]

        for contract in versions.values():
            if contract.contract_version.is_compatible_with(required_version):
                return contract

        raise IncompatibleVersionError(
            source_id=source_id,
            dataset=dataset,
            required=str(required_version),
            provided="no compatible version",
        )

    def list_sources(self) -> list[str]:
        """List all registered source IDs."""
        return list(self._contracts.keys())

    def list_datasets(self, source_id: str) -> list[str]:
        """List all datasets for a source."""
        if source_id not in self._contracts:
            return []
        return list(self._contracts[source_id].keys())

    def list_versions(self, source_id: str, dataset: str) -> list[str]:
        """List all versions for a source/dataset."""
        if source_id not in self._contracts:
            return []
        if dataset not in self._contracts[source_id]:
            return []
        return list(self._contracts[source_id][dataset].keys())

    def has_contract(self, source_id: str, dataset: str, version: str | None = None) -> bool:
        """Check if a contract exists."""
        try:
            self.get_contract(source_id, dataset, version)
            return True
        except ContractNotFoundError:
            return False

    def _get_latest_version(self, versions: dict[str, SourceContract]) -> SourceContract:
        """Get the contract with the highest version."""
        latest_version: ContractVersion | None = None
        latest_contract: SourceContract | None = None

        for contract in versions.values():
            ver = contract.contract_version
            if (
                latest_version is None
                or ver.major > latest_version.major
                or (ver.major == latest_version.major and ver.minor > latest_version.minor)
            ):
                latest_version = ver
                latest_contract = contract

        if latest_contract is None:
            raise ContractNotFoundError(source_id="", dataset="")
        return latest_contract
