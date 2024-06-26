import unittest

from gloe import UnsupportedTransformerArgException
from tests.lib.conditioners import if_is_even, if_not_zero
from tests.lib.transformers import square, square_root, plus1, minus1, to_string

conditioned_graph = square >> (
    if_is_even.Then(plus1 >> minus1)
    .ElseIf(lambda x: x == 1.0)
    .Then(plus1 >> plus1)
    .ElseIf(lambda x: x == 25.0)
    .Then(minus1 >> minus1)
    .Else(square_root)
)


class TestConditionerTransformer(unittest.TestCase):
    def test_conditioner_transformer_name(self):
        """
        Test the name of a ConditionerTransformer
        """
        graph = if_not_zero.Then(plus1).Else(minus1)
        self.assertEqual("if_not_zero", graph.__class__.__name__)

    def test_conditioned_flow(self):
        """
        Test the most simple conditioned case
        """

        conditioned_graph = (
            square >> square_root >> if_not_zero.Then(plus1).Else(minus1)
        )

        self.assertEqual(conditioned_graph(1), 2)
        self.assertEqual(conditioned_graph(0), -1)

    def test_else_none(self):
        """
        Test the else None case
        """
        graph = if_not_zero.Then(plus1).ElseNone()
        self.assertEqual(2, graph(1))
        self.assertIsNone(graph(0))

    def test_flow_with_many_conditions(self):
        """
        Test the case of a flow with many conditions
        """

        conditioned_graph = (
            square
            >> square_root
            >> (
                if_not_zero.Then(plus1 >> minus1).Else(minus1),
                if_not_zero.Then(to_string).Else(to_string),
            )
        )

        self.assertEqual(conditioned_graph(1), (1.0, "1.0"))
        self.assertEqual(conditioned_graph(0), (-1.0, "0.0"))

    def test_chained_conditions(self):
        """
        Test the case of a flow with chained conditions
        """

        self.assertEqual(3.0, conditioned_graph(1.0))
        self.assertEqual(3.0, conditioned_graph(3.0))
        self.assertEqual(16.0, conditioned_graph(4.0))
        self.assertEqual(23.0, conditioned_graph(5.0))

    def test_conditioner_transformer_length(self):
        """
        Test length property of conditioner transformers
        """

        self.assertEqual(8.0, len(conditioned_graph))

    def test_conditioner_unsupported_argument(self):
        """
        Test length property of conditioner transformers
        """

        def _plus2(num: float) -> float:
            return num + 2

        with self.assertRaises(UnsupportedTransformerArgException):
            if_not_zero.Then(_plus2).ElseNone()  # type: ignore

        with self.assertRaises(UnsupportedTransformerArgException):
            if_not_zero.Then(plus1).Else(_plus2)  # type: ignore

        with self.assertRaises(UnsupportedTransformerArgException):
            (
                if_not_zero.Then(plus1)  # type: ignore
                .ElseIf(lambda x: x > 10)
                .Then(_plus2)
                .ElseNone()
            )
