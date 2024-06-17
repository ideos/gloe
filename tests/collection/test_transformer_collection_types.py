from typing import TypeVar, Iterable

from typing_extensions import assert_type

from gloe import Transformer
from gloe.collection import Map, Filter
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

        assert_type(mapped_logarithm, Transformer[list[float], Iterable[str]])

    def test_transformer_filter(self):
        """
        Test the transformer map collection operation
        """

        mapped_logarithm = forward[list[float]]() >> Filter(check_is_even)

        assert_type(mapped_logarithm, Transformer[list[float], Iterable[float]])
