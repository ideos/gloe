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
from gloe import (
    ensure,
    transformer,
    partial_transformer,
    UnsupportedTransformerArgException,
    Transformer,
)
from tests.lib.transformers import square, divide_by_2, plus1, identity, times2


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

    def test_function_ensure(self):
        even_ensurer = ensure(incoming=[is_even])

        def build_divide_by_2_pipeline() -> Transformer[int, float]:
            return divide_by_2

        ensured_is_even_pipeline = even_ensurer(build_divide_by_2_pipeline)

        ensured_divide_by_2 = ensured_is_even_pipeline()

        self.assertRaises(NumberIsOdd, lambda: ensured_divide_by_2(3))
        self.assertEqual(ensured_divide_by_2(2), 1)

    def test_output_function_ensurer(self):
        # outcome
        greater_than_10_ensurer = ensure(outcome=[is_greater_than_10])

        def build_square_pipeline() -> Transformer[float, float]:
            return square

        ensured_is_greater_than_10_pipeline = greater_than_10_ensurer(
            build_square_pipeline
        )

        ensured_square = ensured_is_greater_than_10_pipeline()

        self.assertRaises(NumberLessThanOrEquals10, lambda: ensured_square(2))
        self.assertEqual(ensured_square(6), 36)

        # changes
        same_value_int_ensurer = ensure(changes=[same_value_int])

        def build_plus_1_pipeline() -> Transformer[int, int]:
            return plus1

        ensured_same_value_int_pipeline = same_value_int_ensurer(build_plus_1_pipeline)

        ensured_plus_1 = ensured_same_value_int_pipeline()

        self.assertRaises(NumbersNotEqual, lambda: ensured_plus_1(4))

        # outcome and changes
        greater_than_10_and_same_value_ensurer = ensure(
            outcome=[is_greater_than_10], changes=[same_value]
        )

        def build_identity_pipeline() -> Transformer[float, float]:
            return identity

        ensured_greater_than_10_and_same_value_pipeline = (
            greater_than_10_and_same_value_ensurer(build_identity_pipeline)
        )

        # changes and outcome
        ensured_identity = ensured_greater_than_10_and_same_value_pipeline()

        same_value_and_greater_than_10_ensurer = ensure(
            changes=[same_value], outcome=[is_greater_than_10]
        )

        ensured_same_value_and_greater_than_10_pipeline = (
            same_value_and_greater_than_10_ensurer(build_identity_pipeline)
        )

        ensured_identity2 = ensured_same_value_and_greater_than_10_pipeline()

        self.assertEqual(ensured_identity(11), 11)
        self.assertEqual(ensured_identity2(11), 11)
        self.assertRaises(NumberLessThanOrEquals10, lambda: ensured_identity(9))

    def test_function_many_ensurers(self):
        even_and_greater_than_10_ensurer = ensure(
            incoming=[is_even], outcome=[is_greater_than_10]
        )

        def build_multiply_by_2_pipeline() -> Transformer[int, float]:
            return times2

        ensured_even_and_greater_than_10_pipeline = even_and_greater_than_10_ensurer(
            build_multiply_by_2_pipeline
        )

        ensured_multiply_by_2 = ensured_even_and_greater_than_10_pipeline()

        self.assertRaises(NumberIsOdd, lambda: ensured_multiply_by_2(3))
        self.assertRaises(NumberLessThanOrEquals10, lambda: ensured_multiply_by_2(4))
        self.assertRaises(NumberIsOdd, lambda: ensured_multiply_by_2(7))
        self.assertEqual(ensured_multiply_by_2(6), 12)

    def test_function_ensurer_init_incoming(self):
        even_ensurer = ensure(incoming=[is_even])

        def build_multiply_by_even_pipeline(n: int) -> Transformer[int, int]:
            @partial_transformer
            def multiply_by_even(n1: int, n2: int) -> int:
                return n1 * n2

            return multiply_by_even(n)

        ensured_multiply_by_even_pipeline = even_ensurer(
            build_multiply_by_even_pipeline
        )

        self.assertRaises(NumberIsOdd, lambda: ensured_multiply_by_even_pipeline(2)(3))
        self.assertEqual(ensured_multiply_by_even_pipeline(2)(4), 8)

    def test_function_ensurer_init_outcome(self):
        even_ensurer = ensure(incoming=[is_even])

        def build_multiply_by_equals_even_pipeline(n: int) -> Transformer[int, int]:
            @partial_transformer
            def multiply_by_equals_even(n1: int, n2: int) -> int:
                return n1 * n2

            return multiply_by_equals_even(n)

        ensured_multiply_by_equals_even_pipeline = even_ensurer(
            build_multiply_by_equals_even_pipeline
        )

        self.assertRaises(
            NumberIsOdd, lambda: ensured_multiply_by_equals_even_pipeline(3)(3)
        )
        self.assertEqual(ensured_multiply_by_equals_even_pipeline(3)(2), 6)

    def test_function_ensurer_init_incoming_outcome(self):
        incoming_outcome_even_ensurer = ensure(incoming=[is_even], outcome=[is_even])

        def build_multiply_by_even_equals_even_pipeline(
            n: int,
        ) -> Transformer[int, int]:
            @partial_transformer
            def multiply_by_even_equals_even(n1: int, n2: int) -> int:
                return n1 * n2

            return multiply_by_even_equals_even(n)

        ensured_multiply_by_even_equals_even = incoming_outcome_even_ensurer(
            build_multiply_by_even_equals_even_pipeline
        )

        incoming_odd_outcome_even_ensurer = ensure(incoming=[is_odd], outcome=[is_even])

        def build_multiply_by_odd_equals_even_pipeline(n: int) -> Transformer[int, int]:
            @partial_transformer
            def multiply_by_odd_equals_even(n1: int, n2: int) -> int:
                return n1 * n2

            return multiply_by_odd_equals_even(n)

        ensured_multiply_by_odd_equals_even = incoming_odd_outcome_even_ensurer(
            build_multiply_by_odd_equals_even_pipeline
        )

        self.assertRaises(
            NumberIsOdd, lambda: ensured_multiply_by_even_equals_even(4)(3)
        )
        self.assertEqual(ensured_multiply_by_even_equals_even(4)(6), 24)

        self.assertRaises(
            NumberIsEven, lambda: ensured_multiply_by_odd_equals_even(3)(4)
        )
        self.assertEqual(ensured_multiply_by_odd_equals_even(4)(3), 12)

    def test_function_ensurer_exception(self):
        odd_ensurer = ensure(incoming=[is_odd])

        def generic_identity(n):
            return n

        ensured_pipeline = odd_ensurer(generic_identity)

        self.assertRaises(
            UnsupportedTransformerArgException, lambda: ensured_pipeline(1)
        )
        self.assertRaises(
            UnsupportedTransformerArgException, lambda: odd_ensurer("generic_string")
        )
