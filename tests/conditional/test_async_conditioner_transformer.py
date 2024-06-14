import unittest

from gloe import If
from tests.lib.conditioners import if_not_zero
from tests.lib.transformers import (
    square,
    plus1,
    minus1,
    async_plus1,
)


class TestAsyncConditionerTransformer(unittest.IsolatedAsyncioTestCase):

    async def test_conditioner_unsupported_argument(self):
        """
        Test length property of conditioner transformers
        """

        def _plus2(num: float) -> float:
            return num + 2

        graph = if_not_zero.Then(async_plus1).Else(_plus2)  # type: ignore
        with self.assertRaises(NotImplementedError):
            await graph(0)

    async def test_conditioner_in_graph(self):
        graph2 = plus1 >> if_not_zero.Then(async_plus1).Else(minus1)
        self.assertEqual(2, await graph2(0))

    async def test_async_chained_conditioner(self):
        graph2 = (
            If[float](lambda x: x < 0)
            .Then(async_plus1)
            .ElseIf(lambda x: x > 10)
            .Then(square)
            .Else(minus1)
        )
        self.assertEqual(121, await graph2(11))
