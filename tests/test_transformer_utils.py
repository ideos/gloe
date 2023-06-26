import unittest

from src.gloe.utils import forward_income
from tests.lib.transformers import sum_tuple2


class TestTransformerUtils(unittest.TestCase):

    def test_forward_income(self):
        test_forward = forward_income(sum_tuple2)

        self.assertEqual(test_forward((3, 3)), (6, (3, 3)))

