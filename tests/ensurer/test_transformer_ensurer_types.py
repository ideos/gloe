from typing import TypeVar

from typing_extensions import assert_type

from gloe import (
    Transformer,
    transformer,
    partial_transformer,
    ensure,
)
from tests.lib.ensurers import is_even, same_value, same_value_int, is_greater_than_10
from tests.type_utils.mypy_test_suite import MypyTestSuite

In = TypeVar("In")
Out = TypeVar("Out")


class TestTransformerEnsurerTypes(MypyTestSuite):

    def test_transformer_ensurer(self):
        @ensure(incoming=[is_even])
        @transformer
        def t1(n1: int) -> int:
            return n1 * n1

        @ensure(outcome=[is_even])
        @transformer
        def t2(n1: int) -> int:
            return n1 * n1

        @ensure(changes=[same_value_int])
        @transformer
        def t3(n1: int) -> int:
            return n1 * n1

        @ensure(incoming=[is_even], outcome=[is_even])
        @transformer
        def t4(n1: int) -> int:
            return n1 * n1

        @ensure(incoming=[is_even], outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def t5(n1: int) -> float:
            return n1 * n1

        @ensure(outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def t6(num: float) -> float:
            return num

        assert_type(t1, Transformer[int, int])
        assert_type(t2, Transformer[int, int])
        assert_type(t3, Transformer[int, int])
        assert_type(t4, Transformer[int, int])
        assert_type(t5, Transformer[int, float])
        assert_type(t6, Transformer[float, float])

    def test_transformer_init_ensurer(self):
        @ensure(incoming=[is_even])
        @partial_transformer
        def ti1(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(outcome=[is_even])
        @partial_transformer
        def ti2(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(changes=[same_value_int])
        @partial_transformer
        def ti3(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_even], outcome=[is_even])
        @partial_transformer
        def ti4(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_even], changes=[same_value_int])
        @partial_transformer
        def ti5(n1: int, n2: int) -> int:
            return n1 * n2

        assert_type(ti1(2), Transformer[int, int])
        assert_type(ti2(2), Transformer[int, int])
        assert_type(ti3(2), Transformer[int, int])
        assert_type(ti4(2), Transformer[int, int])
        assert_type(ti5(2), Transformer[int, int])
