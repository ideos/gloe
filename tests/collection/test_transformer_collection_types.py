from typing import TypeVar

from typing_extensions import assert_type

from gloe import Transformer, transformer, async_transformer
from gloe.collection import Map, Filter, MapOver, MapOverAsync
from gloe.utils import forward
from tests.lib.transformers import format_currency, check_is_even, sum_tuple2
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")


class TestTransformerCollectionTypes(MypyTestSuite):
    def test_transformer_map(self):
        """
        Test the transformer map collection operation
        """

        mapped_logarithm = forward[list[float]]() >> Map(
            format_currency(thousands_separator=",")
        )

        assert_type(mapped_logarithm, Transformer[list[float], list[str]])

    def test_transformer_filter(self):
        """
        Test the transformer map collection operation
        """

        mapped_logarithm = forward[list[float]]() >> Filter(check_is_even)

        assert_type(mapped_logarithm, Transformer[list[float], list[float]])

    def test_transformer_map_multiargs(self):
        @transformer
        def concat(arg1: str, arg2: int) -> str:
            return arg1 + str(arg2)

        mapping = Map(concat)

        assert_type(mapping, Map[tuple[str, int], str])

    def test_transformer_map_over_tuple_mapping(self):
        mapping = MapOver([1.0, 2.0], sum_tuple2)

        assert_type(mapping, MapOver[float, float])

    def test_transformer_map_over_multiargs(self):
        @transformer
        def scale_add(scale: float, offset: float, item: float) -> float:
            return scale * item + offset

        mapping = MapOver([1.0, 2.0], scale_add)

        assert_type(mapping, MapOver[float, float, float])

    def test_transformer_async_map_over_multiargs(self):
        @async_transformer
        async def scale_add(scale: float, offset: float, item: float) -> float:
            return scale * item + offset

        mapping = MapOverAsync([1.0, 2.0], scale_add)

        assert_type(mapping, MapOverAsync[float, float, float])
