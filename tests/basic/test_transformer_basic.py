import asyncio
import unittest
from typing import cast

from gloe import (
    TransformerException,
    UnsupportedTransformerArgException,
    transformer,
    Transformer,
)
from tests.lib.transformers import (
    square,
    square_root,
    sum_tuple2,
    sum_tuple3,
    plus1,
    minus1,
    natural_logarithm,
    LnOfNegativeNumber,
)


class TestTransformerBasic(unittest.TestCase):
    def test_transformer_wrong_signature(self):
        with self.assertWarns(RuntimeWarning):

            @transformer  # type: ignore
            def many_args(arg1: str, arg2: int):
                return arg1, arg2

    def test_transformer_hash(self):
        self.assertEqual(hash(square.id), square.__hash__())

    def test_linear_flow(self):
        """
        Test the most simple linear case
        """

        linear_graph = square >> square_root

        integer = 10
        result = linear_graph(integer)

        self.assertEqual(integer, result)

    def test_unsupported_argument(self):
        def just_a_normal_function():
            return None

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {just_a_normal_function}",
        ):
            _ = square >> just_a_normal_function  # type: ignore

        with self.assertRaises(
            UnsupportedTransformerArgException,
            msg=f"Unsupported transformer argument: {just_a_normal_function}",
        ):
            _ = square >> (just_a_normal_function, plus1)  # type: ignore

    def test_divergence_flow(self):
        """
        Test the most simple divergent case
        """

        divergent_graph = square >> (square_root, square)

        integer = 10
        result = divergent_graph(integer)

        self.assertEqual(result, (integer, 10000))

    def test_convergent_flow(self):
        """
        Test the most simple convergent case
        """

        convergent_graph = square >> (square_root, square) >> sum_tuple2

        integer = 10
        result = convergent_graph(integer)

        self.assertEqual(10000 + 10, result)

    def test_divergent_many_branches_flow(self):
        """
        Test the divergent case with many gateways
        """

        convergent_graph = square >> (
            square_root,
            square,
            square_root,
            square,
            square_root,
            square,
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
        max_iters = 320

        def ramification(
            branch: Transformer[float, float]
        ) -> Transformer[float, float]:
            return plus1 >> (plus1, branch) >> sum_tuple2

        graph = plus1
        for i in range(max_iters):
            graph = ramification(graph)

        result = graph(0)

        self.assertEqual(result, 52001)

    def test_recursive_flow(self):
        """
        Test the instantiation of large graph
        """
        graph = plus1 >> plus1
        graph = graph >> graph
        graph = graph >> graph
        graph = graph >> graph
        graph = graph >> graph
        graph = graph >> graph
        graph = graph >> graph
        graph = graph >> graph

        result = graph(0)
        self.assertEqual(result, 256)

    def test_graph_length_property(self):
        graph = square >> square_root

        for i in range(160):
            graph = graph >> square >> square_root

        self.assertEqual(len(graph), 160 * 2 + 2)

        graph2 = (
            square
            >> square_root
            >> (square >> square_root, square >> square_root, square >> square_root)
            >> sum_tuple3
            >> square
            >> square_root
            >> (square >> square_root, square >> square_root)
        )

        self.assertEqual(len(graph2), 15)

    def test_transformer_equality(self):
        graph = square >> square_root
        self.assertEqual(square, square)
        self.assertEqual(square, square.copy())
        self.assertNotEqual(graph, square_root)
        self.assertNotEqual(square, square_root)

        with self.assertRaises(NotImplementedError):
            self.assertEqual(square, 1)

    def test_transformer_pydoc_keeping(self):
        @transformer
        def to_string(num: int) -> str:
            """This transformer receives a number as input and return its representation
            as a string"""
            return str(num)

        self.assertEqual(
            to_string.__doc__,
            """This transformer receives a number as input and return its representation
            as a string""",
        )

    def test_transformer_signature_representation(self):
        signature = square.signature()

        self.assertEqual(str(signature), "(num: float) -> float")

    def test_transformer_error_forward(self):
        """
        Test if an error raised inside a transformer can be caught outside it
        """
        graph = minus1 >> natural_logarithm
        self.assertRaises(LnOfNegativeNumber, lambda: graph(0))

    def test_transformer_error_handling(self):
        """
        Test if a raised error stores the correct TransformerException as its cause
        """

        graph = minus1 >> natural_logarithm
        try:
            graph(-1)
        except LnOfNegativeNumber as exception:
            self.assertEqual(type(exception.__cause__), TransformerException)

            exception_ctx = cast(TransformerException, exception.__cause__)
            self.assertEqual(natural_logarithm, exception_ctx.raiser_transformer)

    def test_transformers_on_a_running_event_loop(self):
        async def run_main():
            graph = square >> square_root
            graph(9)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_main())
