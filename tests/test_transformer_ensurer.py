import unittest

from lib.ensurers import same_value
from lib.exceptions import NumbersNotEqual
from tests.lib.exceptions import NumberLessThanOrEquals10
from tests.lib.ensurers import NumberIsOdd, is_even, is_greater_than_10
from src.gloe import transformer, ensure


class TestTransformerEnsurer(unittest.TestCase):
    def test_ensure_with(self):
        @ensure(income=[is_even])
        @transformer
        def divide_by_2(num: int) -> float:
            return num / 2

        self.assertRaises(NumberIsOdd, lambda: divide_by_2(3))
        self.assertEqual(divide_by_2(2), 1)

    def test_output_ensurer(self):
        @ensure(outcome=[is_greater_than_10])
        @transformer
        def multiply_by_2(num: int) -> float:
            return num * 2

        self.assertRaises(NumberLessThanOrEquals10, lambda: multiply_by_2(4))
        self.assertEqual(multiply_by_2(6), 12)

        @ensure(outcome=[same_value])
        @transformer
        def sum1(num: int) -> int:
            return num + 1

        self.assertRaises(NumbersNotEqual, lambda: sum1(4))

        @ensure(outcome=[same_value, is_greater_than_10])
        @transformer
        def identity(num: int) -> int:
            return num

        self.assertEqual(identity(11), 11)
        self.assertRaises(NumberLessThanOrEquals10, lambda: identity(9))

    def test_many_ensurers(self):
        @ensure(income=[is_even], outcome=[is_greater_than_10])
        @transformer
        def multiply_by_2(num: int) -> float:
            return num * 2

        self.assertRaises(NumberIsOdd, lambda: multiply_by_2(3))
        self.assertRaises(NumberLessThanOrEquals10, lambda: multiply_by_2(4))
        self.assertRaises(NumberIsOdd, lambda: multiply_by_2(7))
        self.assertEqual(multiply_by_2(6), 12)
