import unittest
from typing import Iterable

from gloe import AsyncTransformer, async_transformer
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

        mapping1: AsyncTransformer[Iterable[float], list[float]] = (
            Map(square) >> MapAsync[float, float](async_plus1)
        )
        graph = square >> async_plus1
        mapping2: MapAsync[float, float] = MapAsync(graph)

        seq = [10.0, 9.0, 3.0, 2.0, -1.0]
        result1 = list(await mapping1(seq))
        result2 = list(await mapping2(seq))

        expected = [101.0, 82.0, 10.0, 5.0, 2.0]
        self.assertListEqual(expected, result1)
        self.assertListEqual(expected, result2)

    async def test_transformer_async_map_with_callable(self):
        async def double(num: int) -> int:
            return num * 2

        mapping: MapAsync[int, int] = MapAsync(double)

        self.assertListEqual([2, 4, 6], list(await mapping([1, 2, 3])))

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

    async def test_transformer_async_filter_with_sync_callable(self):
        def is_even(num: int) -> bool:
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

    async def test_transformer_async_map_over_with_callable(self):
        data = [1, 2, 3]

        async def add(num: int, inc: int) -> int:
            return num + inc

        mapping: MapOverAsync[int, int] = MapOverAsync(data, add)

        self.assertListEqual([2, 3, 4], list(await mapping(1)))
