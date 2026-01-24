import unittest
from typing import Union

from gloe import transformer
from gloe.transformers import _execute_flow
from gloe.utils import forward, forward_incoming, debug, attach
from tests.lib.transformers import sum_tuple2, square_root, square


class TestTransformerUtils(unittest.TestCase):
    def test_forward_incoming(self):
        test_forward = forward_incoming(sum_tuple2)

        self.assertEqual(test_forward((3, 3)), (6, (3, 3)))

    def test_attach(self):
        test_forward = attach(sum_tuple2)

        self.assertEqual(test_forward((3, 3)), (6, (3, 3)))

    def test_forward_repr(self):
        test_forward = forward[int]()

        self.assertEqual("int -> (forward) -> int", repr(test_forward))

        @transformer
        def test_union(num: float) -> Union[int, float]:
            return num

        union = square >> square_root >> test_union
        self.assertEqual(
            "float -> (3 transformers omitted) -> (int | float)", repr(union)
        )

        @transformer
        def test_tuple(num: float) -> tuple[int, float]:
            return 1, num

        _tuple = square >> square_root >> test_tuple
        self.assertEqual(
            "float -> (3 transformers omitted) -> (int, float)", repr(_tuple)
        )

    def test_debug(self):
        test_debug = forward[int]() >> debug()

        result = test_debug(5)
        self.assertEqual(result, 5)

    def test_composition_transform_method(self):
        test1 = forward[float]() >> square

        result = test1.transform(5)
        self.assertIsNone(result)
        test2 = forward[float]() >> (square, square)

        result2 = test2.transform(5)
        self.assertIsNone(result2)

    def test_execute_async_wrong_flow(self):
        flow = [2]
        with self.assertRaises(NotImplementedError):
            _execute_flow(flow, 1)  # type: ignore
