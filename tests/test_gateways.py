import unittest

from gloe.gateways import sequential, parallel
from tests.lib.transformers import plus1, minus1, async_plus1, sum_tuple2


class TestGateways(unittest.TestCase):
    def test_parallel_gateway(self):
        graph = parallel(plus1, minus1)

        self.assertEqual((11.0, 9.0), graph(10.0))

    def test_sequential_gateway(self):
        graph = sequential(plus1, minus1)

        self.assertEqual((11.0, 9.0), graph(10.0))


class TestAsyncGateways(unittest.IsolatedAsyncioTestCase):
    async def test_async_parallel_gateway(self):
        graph = parallel(async_plus1, plus1) >> sum_tuple2
        result = await graph(10.0)

        self.assertEqual(22.0, result)

    async def test_async_sequential_gateway(self):
        graph = sequential(async_plus1, plus1) >> sum_tuple2
        result = await graph(10.0)
        self.assertEqual(22.0, result)
