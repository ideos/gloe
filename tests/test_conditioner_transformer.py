import unittest

from tests.lib.conditioners import if_is_even
from tests.lib.conditioners import if_not_zero
from tests.lib.transformers import *


class TestConditionerTransformer(unittest.TestCase):
    def test_conditioned_flow(self):
        """
        Test the most simple conditioned case
        """

        conditioned_graph = square >> square_root >> if_not_zero.Then(plus1).Else(minus1)

        self.assertEqual(conditioned_graph(1), 2)
        self.assertEqual(conditioned_graph(0), -1)

    def test_flow_with_many_conditions(self):
        """
        Test the case of a flow with many conditions
        """

        conditioned_graph = square >> square_root >> (
            if_not_zero.Then(plus1 >> minus1).Else(minus1),
            if_not_zero.Then(to_string).Else(to_string)
        )

        self.assertEqual(conditioned_graph(1), (1.0, '1.0'))
        self.assertEqual(conditioned_graph(0), (-1.0, '0.0'))

    def test_chained_conditions(self):
        """
        Test the case of a flow with chained conditions
        """
        def check(x: float) -> bool:
            print('\nx\n')
            return x == 1.0

        conditioned_graph = square >> (
            if_is_even.Then(plus1 >> minus1)
            .ElseIf(check).Then(plus1 >> plus1)
            .ElseIf(lambda x: x == 25.0).Then(minus1 >> minus1)
            .Else(square_root)
        )
        print(conditioned_graph(1.0))
        print(conditioned_graph(3.0))
        # self.assertEqual(3.0, conditioned_graph(1.0))
        self.assertEqual(3.0, conditioned_graph(3.0))
        self.assertEqual(4.0, conditioned_graph(4.0))
        self.assertEqual(23.0, conditioned_graph(5.0))


if __name__ == '__main__':
    unittest.main()
