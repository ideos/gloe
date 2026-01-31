from typing import TypeVar, Any
from collections.abc import Awaitable, Coroutine

from typing_extensions import assert_type

from gloe import (
    Transformer,
    async_transformer,
    transformer,
)
from gloe.experimental import bridge
from gloe.utils import forward
from tests.lib.transformers import (
    square,
    square_root,
    plus1,
    minus1,
    to_string,
    tuple_concatenate,
    sum_tuple2,
    async_plus1,
)
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")


class TestBasicTransformerTypes(MypyTestSuite):
    def test_transformer_simple_typing(self):
        """
        Test the most simple transformer typing
        """

        graph = square
        assert_type(graph, Transformer[float, float])

    def test_simple_flow_typing(self):
        """
        Test the most simple transformer typing
        """

        graph = square >> square_root

        assert_type(graph, Transformer[float, float])

    def test_flow_with_mixed_types(self):
        """
        Test the most simple transformer typing
        """

        graph = square >> square_root >> to_string

        assert_type(graph, Transformer[float, str])

    def test_divergent_flow_types(self):
        """
        Test the most simple transformer typing
        """

        graph2 = square >> square_root >> (to_string, square)
        assert_type(graph2, Transformer[float, tuple[str, float]])

        graph3 = square >> square_root >> (to_string, square, to_string)
        assert_type(graph3, Transformer[float, tuple[str, float, str]])

        graph4 = square >> square_root >> (to_string, square, to_string, square)
        assert_type(graph4, Transformer[float, tuple[str, float, str, float]])

        graph5 = (
            square >> square_root >> (to_string, square, to_string, square, to_string)
        )
        assert_type(graph5, Transformer[float, tuple[str, float, str, float, str]])

        graph6 = (
            square
            >> square_root
            >> (to_string, square, to_string, square, to_string, square)
        )
        assert_type(
            graph6, Transformer[float, tuple[str, float, str, float, str, float]]
        )

        graph7 = (
            square
            >> square_root
            >> (to_string, square, to_string, square, to_string, square, to_string)
        )
        assert_type(
            graph7, Transformer[float, tuple[str, float, str, float, str, float, str]]
        )

    def test_bridge(self):
        num_bridge = bridge[float]("num")

        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()

        assert_type(graph, Transformer[float, tuple[float, float]])

    def test_async_transformer(self):
        @async_transformer
        async def _square(num: int) -> float:
            return float(num * num)

        @transformer
        async def async_square(num: int) -> float:
            return float(num * num)

        async_pipeline = _square >> to_string
        async_pipeline2 = forward[int]() >> _square >> to_string
        async_pipeline3 = forward[int]() >> (_square, _square >> to_string)
        async_pipeline4 = _square >> (to_string, forward[float]())
        async_pipeline5 = _square >> (to_string, forward[float]()) >> tuple_concatenate
        async_pipeline6 = async_square >> to_string
        async_pipeline7 = async_square >> (to_string, forward[float]())

        assert_type(_square, Transformer[int, Awaitable[float]])
        assert_type(async_pipeline, Transformer[int, Awaitable[str]])
        assert_type(async_pipeline2, Transformer[int, Awaitable[str]])
        assert_type(async_pipeline3, Transformer[int, Awaitable[tuple[float, str]]])
        assert_type(async_pipeline4, Transformer[int, Awaitable[tuple[str, float]]])
        assert_type(async_pipeline5, Transformer[int, Awaitable[str]])
        assert_type(async_square, Transformer[int, Coroutine[Any, Any, float]])
        assert_type(async_pipeline6, Transformer[int, Awaitable[str]])
        assert_type(
            async_pipeline7,
            Transformer[int, Awaitable[tuple[str, float]]],
        )

    def test_mixed_sync_async_typing(self):
        @transformer
        async def async_square(num: float) -> float:
            return float(num * num)

        mixed_pipeline = plus1 >> async_plus1 >> square >> to_string

        assert_type(mixed_pipeline, Transformer[float, Awaitable[str]])

        mixed_divergent = plus1 >> (async_plus1, square >> async_plus1) >> sum_tuple2

        assert_type(mixed_divergent, Transformer[float, Awaitable[float]])

        mixed_with_async_root = plus1 >> async_square >> (to_string, square)

        assert_type(
            mixed_with_async_root,
            Transformer[float, Awaitable[tuple[str, float]]],
        )
