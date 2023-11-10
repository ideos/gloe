import unittest

from src.gloe.utils import forward_incoming
from tests.lib.transformers import sum_tuple2


class TestTransformerUtils(unittest.TestCase):

    def test_forward_incoming(self):
        test_forward = forward_incoming(sum_tuple2)

        self.assertEqual(test_forward((3, 3)), (6, (3, 3)))

