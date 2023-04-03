import unittest
from typing import cast

from tests.lib.transformers import *
from transformer import TransformerException, transformer


class TestFunctionTransformer(unittest.TestCase):
    def test_linear_flow(self):
        """
        Test the most simple linear case
        """

        linear_graph = square >> square_root

        integer = 10
        result = linear_graph(integer)

        self.assertEqual(result, integer)

    def test_divergence_flow(self):
        """
        Test the most simple divergent case
        """

        divergent_graph = square >> (
            square_root,
            square
        )

        integer = 10
        result = divergent_graph(integer)

        self.assertEqual(result, (integer, 10000))

    def test_convergent_flow(self):
        """
        Test the most simple convergent case
        """

        convergent_graph = square >> (
            square_root,
            square
        ) >> sum_tuple2

        integer = 10
        result = convergent_graph(integer)

        self.assertEqual(result, 10000 + 10)

    def test_divergent_many_branches_flow(self):
        """
        Test the divergent case with many branches
        """

        convergent_graph = square >> (
            square_root,
            square,
            square_root,
            square,
            square_root,
            square
        )

        integer = 10
        result = convergent_graph(integer)

        self.assertEqual(result, (10, 10000, 10, 10000, 10, 10000))

    def test_dynamically_created_flow(self):
        """
        Test the dynamically created graph using a iteration
        """

        graph = square >> square_root

        for i in range(10):
            graph = graph >> square >> square_root

        result = graph(10)
        self.assertEqual(result, 10)

    def test_exhausting_large_flow(self):
        """
        Test the instantiation of large graph
        """
        graph = sum1
        max_iters = 480
        for i in range(max_iters):
            graph = graph >> sum1

        result = graph(0)
        self.assertEqual(result, max_iters + 1)

    def test_graph_length_property(self):
        graph = square >> square_root

        for i in range(160):
            graph = graph >> square >> square_root

        self.assertEqual(len(graph), 160 * 2 + 2)

        graph2 = square >> square_root >> (
            square >> square_root,
            square >> square_root,
            square >> square_root
        ) >> sum_tuple3 >> square >> square_root >> (
            square >> square_root,
            square >> square_root
        )

        self.assertEqual(len(graph2), 15)

    def test_transformer_equality(self):
        graph = square >> square_root
        self.assertEqual(square, square)
        self.assertEqual(square, square.copy())
        self.assertNotEqual(graph, square_root)
        self.assertNotEqual(square, square_root)

    def test_transformer_pydoc_keeping(self):

        @transformer
        def to_string(num: int) -> str:
            """
            This transformer receives a number as input and return its representation as a string
            """
            return str(num)

        self.assertEqual(
            to_string.__doc__,
            """
            This transformer receives a number as input and return its representation as a string
            """
        )

    def test_transformer_signature_representation(self):
        signature = square.__signature__()

        self.assertEqual(str(signature), '(num: float) -> float')

    def test_transformer_nodes_retrieve(self):
        graph = square >> square_root >> square >> square_root
        nodes = graph.graph_nodes()

        expected_nodes = {
            square.id: square,
            square_root.id: square_root
        }
        self.assertDictEqual(expected_nodes, nodes)

        graph2 = square >> square_root >> (
            square >> square_root,
            square >> square_root
        )
        nodes = graph2.graph_nodes()

        expected_nodes = {
            square.id: square,
            square_root.id: square_root
        }
        self.assertDictEqual(expected_nodes, nodes)

    def test_transformer_error_forward(self):
        """
        Test if an error raised inside a transformer can be caught outside it
        """
        graph = minus1 >> natural_logarithm
        self.assertRaises(LnOfNegativeNumber, lambda: graph(0))

    def test_transformer_error_handling(self):
        """
        Test if a raised error stores the correct TransformerException in its context
        """

        graph = minus1 >> natural_logarithm
        try:
            graph(0)
        except LnOfNegativeNumber as exception:
            self.assertEqual(type(exception.__context__), TransformerException)

            exception_ctx = cast(TransformerException, exception.__context__)
            self.assertEqual(natural_logarithm.id, exception_ctx.raiser_transformer.id)


if __name__ == '__main__':
    unittest.main()
