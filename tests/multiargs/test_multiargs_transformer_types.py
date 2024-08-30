from typing import TypeVar

from gloe.utils import forward
from typing_extensions import assert_type

from gloe import transformer, MultiArgsTransformer, Transformer
from tests.lib.transformers import square
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

        assert_type(sum2, MultiArgsTransformer[int, float, float])

        @transformer
        def sum3(num1: int, num2: int, num3: int) -> int:
            return num1 + num2 + num3

        assert_type(sum3, MultiArgsTransformer[int, int, int, int])

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

        pipeline = sum2 >> square

        assert_type(pipeline, MultiArgsTransformer[float, float, float])

        pipeline2 = forward[float]() >> (square, square) >> sum2

        assert_type(pipeline2, Transformer[float, float])

        pipeline3 = sum2 >> (square, square) >> sum2

        assert_type(pipeline3, MultiArgsTransformer[float, float, float])
