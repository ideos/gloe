import unittest

from tests.lib.conditioners import if_not_zero
from tests.lib.transformers import *


class TestConditionerTransformer(unittest.TestCase):
    def test_conditioned_flow(self):
        """
        Test the most simple conditioned case
        """

        conditioned_graph = square >> square_root >> if_not_zero.Then(sum1).Else(minus1)

        self.assertEqual(conditioned_graph(1), 2)
        self.assertEqual(conditioned_graph(0), -1)

    def test_flow_with_many_conditions(self):
        """
        Test the case of a flow with many conditions
        """

        conditioned_graph = square >> square_root >> (
            if_not_zero.Then(sum1 >> minus1).Else(minus1),
            if_not_zero.Then(to_string).Else(to_string)
        )

        self.assertEqual(conditioned_graph(1), (1.0, '1.0'))
        self.assertEqual(conditioned_graph(0), (-1.0, '0.0'))


if __name__ == '__main__':
    unittest.main()
