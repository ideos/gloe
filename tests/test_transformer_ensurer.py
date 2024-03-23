import unittest

from tests.lib.exceptions import (
    NumberIsEven,
    NumberLessThanOrEquals10,
    NumbersNotEqual,
    NumberIsOdd,
)
from tests.lib.ensurers import (
    is_odd,
    same_value,
    is_even,
    is_greater_than_10,
    same_value_int,
)
from gloe import ensure, transformer, partial_transformer


class TestTransformerEnsurer(unittest.TestCase):
    def test_ensure_decorator(self):
        @ensure(incoming=[is_even])
        @transformer
        def divide_by_2(num: int) -> float:
            return num / 2

        self.assertRaises(NumberIsOdd, lambda: divide_by_2(3))
        self.assertEqual(divide_by_2(2), 1)

    def test_output_ensurer(self):
        @ensure(outcome=[is_greater_than_10])
        @transformer
        def multiply_by_2(num: float) -> float:
            return num * 2

        self.assertRaises(NumberLessThanOrEquals10, lambda: multiply_by_2(4))
        self.assertEqual(multiply_by_2(6), 12)

        @ensure(changes=[same_value_int])
        @transformer
        def _plus1(num: int) -> int:
            return num + 1

        self.assertRaises(NumbersNotEqual, lambda: _plus1(4))

        @ensure(outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def identity(num: float) -> float:
            return num

        @ensure(changes=[same_value], outcome=[is_greater_than_10])
        @transformer
        def identity2(num: float) -> float:
            return num

        self.assertEqual(identity(11), 11)
        self.assertEqual(identity2(11), 11)
        self.assertRaises(NumberLessThanOrEquals10, lambda: identity(9))

    def test_many_ensurers(self):
        @ensure(incoming=[is_even], outcome=[is_greater_than_10])
        @transformer
        def multiply_by_2(num: int) -> float:
            return num * 2

        self.assertRaises(NumberIsOdd, lambda: multiply_by_2(3))
        self.assertRaises(NumberLessThanOrEquals10, lambda: multiply_by_2(4))
        self.assertRaises(NumberIsOdd, lambda: multiply_by_2(7))
        self.assertEqual(multiply_by_2(6), 12)

    def test_ensurer_init_incoming(self):
        @ensure(incoming=[is_even])
        @partial_transformer
        def multiply_by_even(n1: int, n2: int) -> int:
            return n1 * n2

        self.assertRaises(NumberIsOdd, lambda: multiply_by_even(2)(3))
        self.assertEqual(multiply_by_even(2)(4), 8)

    def test_ensurer_init_outcome(self):
        @ensure(incoming=[is_even])
        @partial_transformer
        def multiply_by_equals_even(n1: int, n2: int) -> int:
            return n1 * n2

        self.assertRaises(NumberIsOdd, lambda: multiply_by_equals_even(3)(3))
        self.assertEqual(multiply_by_equals_even(3)(2), 6)

    def test_ensurer_init_incoming_outcome(self):
        @ensure(incoming=[is_even], outcome=[is_even])
        @partial_transformer
        def multiply_by_even_equals_even(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_odd], outcome=[is_even])
        @partial_transformer
        def multiply_by_odd_equals_even(n1: int, n2: int) -> int:
            return n1 * n2

        self.assertRaises(NumberIsOdd, lambda: multiply_by_even_equals_even(4)(3))
        self.assertEqual(multiply_by_even_equals_even(4)(6), 24)

        self.assertRaises(NumberIsEven, lambda: multiply_by_odd_equals_even(3)(4))
        self.assertEqual(multiply_by_odd_equals_even(4)(3), 12)
