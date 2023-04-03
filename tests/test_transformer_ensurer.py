import unittest

from tests.lib.exceptions import NumberLessThanOrEquals10
from tests.lib.ensurers import NumberIsOdd, is_even, is_greater_than_10
from src.gloe.transformer import transformer
from src.gloe.transformer_ensurer import ensure_with


class TestTransformerEnsurer(unittest.TestCase):
    def test_ensure_with(self):
        @ensure_with(input_ensurers=[is_even])
        @transformer
        def divide_by_2(num: int) -> float:
            return num / 2

        self.assertRaises(NumberIsOdd, lambda: divide_by_2(3))
        self.assertEqual(divide_by_2(2), 1)

    def test_output_ensurer(self):
        @ensure_with(output_ensurers=[is_greater_than_10])
        @transformer
        def multiply_by_2(num: int) -> float:
            return num * 2

        self.assertRaises(NumberLessThanOrEquals10, lambda: multiply_by_2(4))
        self.assertEqual(multiply_by_2(6), 12)

    def test_many_ensurers(self):
        @ensure_with(input_ensurers=[is_even], output_ensurers=[is_greater_than_10])
        @transformer
        def multiply_by_2(num: int) -> float:
            return num * 2

        self.assertRaises(NumberIsOdd, lambda: multiply_by_2(3))
        self.assertRaises(NumberLessThanOrEquals10, lambda: multiply_by_2(4))
        self.assertRaises(NumberIsOdd, lambda: multiply_by_2(7))
        self.assertEqual(multiply_by_2(6), 12)
