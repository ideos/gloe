from typing import TypeVar
from collections.abc import Coroutine
from typing import Any

from gloe.utils import forward
from typing_extensions import assert_type

from gloe import transformer, Transformer
from tests.lib.transformers import square, plus1, times2
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")


class TestMultiArgsTransformerTypes(MypyTestSuite):
    def test_transformer_multiple_args(self):
        """
        Test the transformer with multiple args typing
        """

        @transformer
        def sum2(num1: int, num2: float) -> float:
            return num1 + num2

        assert_type(sum2, Transformer[int, float, float])

        @transformer
        def sum3(num1: int, num2: int, num3: int) -> int:
            return num1 + num2 + num3

        assert_type(sum3, Transformer[int, int, int, int])

    def test_noargs_transformer(self):
        """
        Test the transformer with no args typing
        """

        @transformer
        def randint() -> int:
            return 6

        assert_type(randint, Transformer[None, int])

    def test_composition(self):
        @transformer
        def sum2(num1: float, num2: float) -> float:
            return num1 + num2

        @transformer
        def sum3(num1: float, num2: float, num3: float) -> float:
            return num1 + num2 + num3

        pipeline = sum2 >> square

        assert_type(pipeline, Transformer[float, float, float])

        pipeline2 = forward[float]() >> (square, square) >> sum2

        assert_type(pipeline2, Transformer[float, float])

        pipeline3 = sum2 >> (square, square) >> sum2

        assert_type(pipeline3, Transformer[float, float, float])

        pipeline4 = forward[float]() >> (square, plus1, times2) >> sum3

        assert_type(pipeline4, Transformer[float, float])

        pipeline5 = forward[tuple[float, float, float]]() >> sum3

        assert_type(pipeline5, Transformer[tuple[float, float, float], float])

    def test_async_composition(self):
        @transformer
        async def async_sum3(num1: float, num2: float, num3: float) -> float:
            return num1 + num2 + num3

        pipeline = forward[float]() >> (square, plus1, times2) >> async_sum3

        assert_type(pipeline, Transformer[float, Coroutine[Any, Any, float]])

        pipeline2 = forward[tuple[float, float, float]]() >> async_sum3

        assert_type(
            pipeline2,
            Transformer[tuple[float, float, float], Coroutine[Any, Any, float]],
        )
