"""The positive typing programs must also execute with their asserted results."""

from unittest import IsolatedAsyncioTestCase

from .typing import positive_matrix


class PublicContractMatrix(IsolatedAsyncioTestCase):
    async def test_root_and_configuration_contracts(self) -> None:
        await positive_matrix.roots()

    async def test_topology_and_adapter_contracts(self) -> None:
        await positive_matrix.topology()

    async def test_values_and_callback_contracts(self) -> None:
        await positive_matrix.values_and_callbacks()
