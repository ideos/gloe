import unittest

from gloe.utils import forward, forward_incoming, debug
from tests.lib.transformers import sum_tuple2, square_root, square


class TestTransformerUtils(unittest.TestCase):
    def test_forward_incoming(self):
        test_forward = forward_incoming(sum_tuple2)

        self.assertEqual(test_forward((3, 3)), (6, (3, 3)))

    def test_forward_repr(self):
        test_forward = forward[int]()

        self.assertEqual("int -> (forward) -> int", repr(test_forward))

        two_nodes = square >> square_root
        self.assertEqual("float -> (2 transformers omitted) -> float", repr(two_nodes))

    def test_debug(self):
        test_debug = forward[int]() >> debug()

        result = test_debug(5)
        self.assertEqual(result, 5)

    def test_composition_transform_method(self):
        test1 = forward[float]() >> square

        result = test1.transform(5)
        self.assertIsNone(result)
        test2 = forward[float]() >> (square, square)

        result = test2.transform(5)
        self.assertIsNone(result)
