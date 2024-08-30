import unittest

from gloe.exceptions import TransformerRequiresMultiArgs
from gloe.utils import forward

from gloe import transformer
from tests.lib.transformers import square, sum_tuple2, plus1


@transformer
def sum2(num1: float, num2: float) -> float:
    return num1 + num2


class TestMultiArgsTransformer(unittest.TestCase):
    def test_basic_call(self):
        @transformer
        def many_args(arg1: str, arg2: int) -> str:
            return arg1 + str(arg2)

        self.assertEqual(many_args("hello", 1), "hello1")

    def test_serial_composition(self):

        pipeline1 = forward[tuple[float, float]]() >> sum2

        self.assertEqual(pipeline1((1, 2)), 3)

        pipeline2 = sum2 >> square

        self.assertEqual(pipeline2(1, 2), 9)

    def test_diverging_composition(self):

        pipeline1 = forward[float]() >> (square, square) >> sum2

        self.assertEqual(pipeline1(1), 2)

        pipeline2 = sum2 >> (square, square)

        self.assertEqual(pipeline2(1, 2), (9, 9))

    def test_composition_transform_method(self):
        test1 = sum2 >> plus1

        result = test1.transform((5, 3))
        self.assertIsNone(result)

        test2 = sum2 >> (plus1, plus1)

        result2 = test2.transform((5, 3))
        self.assertIsNone(result2)

    def test_single_arg_exception(self):
        @transformer
        def concat(arg1: str, arg2: str) -> str:
            return arg1 + arg2

        with self.assertRaises(TransformerRequiresMultiArgs):
            concat("test")  # type: ignore[call-arg]

    def test_noargs_basic_call(self):
        @transformer
        def randint() -> int:
            return 6  # random.randint(1, 10)

        self.assertEqual(randint(), 6)

    def test_noargs_diverging_composition(self):
        @transformer
        def randfloat() -> float:
            return 6.0

        pipeline = randfloat >> (square, square) >> sum_tuple2

        self.assertEqual(pipeline(), 72.0)
