import unittest
from typing import cast

from tests.lib.conditioners import if_not_zero
from tests.lib.transformers import *
from transformer import TransformerException, transformer


class TestConditionerTransformer(unittest.TestCase):
    def test_conditioned_flow(self):
        """
        Test the most simple conditioned case
        """

        conditioned_graph = square >> square_root >> if_not_zero.Then(sum1).Else(minus1)

        self.assertEqual(conditioned_graph(1), 2)
        self.assertEqual(conditioned_graph(0), -1)


if __name__ == '__main__':
    unittest.main()
