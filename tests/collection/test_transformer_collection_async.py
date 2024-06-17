import unittest

from gloe import async_transformer
from gloe.collection import Map, FilterAsync, MapAsync, MapOverAsync
from tests.lib.transformers import (
    square,
    plus1,
    async_sum_tuple2,
    async_plus1,
)


class TestTransformerCollectionAsync(unittest.IsolatedAsyncioTestCase):

    async def test_transformer_async_map(self):
        """
        Test the mapping transformer
        """

        mapping1 = Map(square) >> MapAsync(async_plus1)
        graph = square >> async_plus1
        mapping2 = MapAsync(graph)

        seq = [10.0, 9.0, 3.0, 2.0, -1.0]
        result1 = list(await mapping1(seq))
        result2 = list(await mapping2(seq))

        expected = [101.0, 82.0, 10.0, 5.0, 2.0]
        self.assertListEqual(expected, result1)
        self.assertListEqual(expected, result2)

    async def test_transformer_async_filter(self):
        """
        Test the filter transformer
        """

        @async_transformer
        async def is_even(num: int) -> bool:
            return num % 2 == 0

        _filter = FilterAsync(is_even)

        seq = [10, 9, 3, 2, 1]
        result = await _filter(seq)

        expected = [10, 2]
        self.assertListEqual(expected, list(result))

    async def test_transformer_async_map_over(self):
        """
        Test the mapping transformer
        """

        data = [10.0, 9.0, 3.0, 2.0, -1.0]
        mapping = MapOverAsync(data, async_sum_tuple2) >> Map(plus1)

        result = list(await mapping(-1.0))

        self.assertListEqual(result, data)
