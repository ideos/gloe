from typing import TypeVar

from typing_extensions import assert_type

from gloe import Transformer
from gloe.collection import Map, Filter, MapOver
from gloe.utils import forward
from tests.lib.transformers import format_currency, check_is_even
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

    def test_transformer_map_callable(self):
        """
        Test the transformer map collection operation with a callable
        """

        def to_str(num: int) -> str:
            return str(num)

        mapped_values = forward[list[int]]() >> Map(to_str)

        assert_type(mapped_values, Transformer[list[int], list[str]])

    def test_transformer_filter(self):
        """
        Test the transformer map collection operation
        """

        mapped_logarithm = forward[list[float]]() >> Filter(check_is_even)

        assert_type(mapped_logarithm, Transformer[list[float], list[float]])

    def test_transformer_filter_callable(self):
        """
        Test the transformer filter operation with a callable
        """

        def is_positive(num: int) -> bool:
            return num > 0

        filtered_values = forward[list[int]]() >> Filter(is_positive)

        assert_type(filtered_values, Transformer[list[int], list[int]])

    def test_transformer_map_over_callable(self):
        """
        Test the transformer map over operation with a callable
        """

        def format_value(num: int, suffix: str) -> str:
            return f"{num}{suffix}"

        mapped_values = forward[int]() >> MapOver(["a", "b"], format_value)

        assert_type(mapped_values, Transformer[int, list[str]])
