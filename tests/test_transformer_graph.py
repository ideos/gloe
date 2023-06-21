import unittest

from networkx import DiGraph

from lib.conditioners import if_is_even
from lib.transformers import divide_by_2, minus1, \
    mul_tuple2, natural_logarithm, \
    square, \
    square_root, \
    sum1, \
    sum_tuple2, \
    sum_tuple3, times2
from src.gloe import Begin
from src.gloe.utils import forward


class TestTransformerGraph(unittest.TestCase):
    def _assert_graph_has_edges(self, transformer, graph, expected_edges):

        ids_by_name = {
            node.__class__.__name__: str(id)
            for id, node in transformer.graph_nodes.items()
        }

        edges = [edge for edge, props in list(graph.edges.items())]

        edges_with_id = [(ids_by_name[edge[0]], ids_by_name[edge[1]]) for edge in expected_edges]

        for edge in edges_with_id:
            self.assertIn(edge, edges)

    def test_simplest_case(self):
        identity = square >> square_root >> sum1 >> minus1
        graph: DiGraph = identity.graph()
        nodes = graph.nodes.items()
        self.assertEqual(4, len(nodes))

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(3, len(edges))

        expected_edges = [
            ('square', 'square_root'),
            ('square_root', 'sum1'),
            ('sum1', 'minus1')
        ]

        self._assert_graph_has_edges(identity, graph, expected_edges)

    def test_simple_divergent_case(self):
        divergent = square >> (
            sum1,
            minus1
        ) >> sum_tuple2

        graph: DiGraph = divergent.graph()

        nodes = graph.nodes.items()
        self.assertEqual(5, len(nodes))  # Each divergent connection has a hidden node

        edges = [edge for edge, props in list(graph.edges.items())]
        # Five edges:
        #           +---->  sum1  ----+
        #  square --+                 +--> (Converge) --> sum_tuple2
        #           +----> minus1 ----+
        self.assertEqual(5, len(edges))

        expected_edges = [
            ('square', 'sum1'),
            ('square', 'minus1'),
            ('sum1', 'Converge'),
            ('minus1', 'Converge'),
            ('Converge', 'sum_tuple2')
        ]

        self._assert_graph_has_edges(divergent, graph, expected_edges)

    def test_complex_divergent_case(self):
        divergent = square >> (
            sum1 >> if_is_even.Then(square_root).Else(forward),
            minus1 >> natural_logarithm,
            times2 >> divide_by_2
        ) >> sum_tuple3

        graph: DiGraph = divergent.graph()

        nodes = graph.nodes.items()
        self.assertEqual(11, len(nodes))  # Each divergent connection has a hidden node

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(13, len(edges))

        expected_edges = [
            ('square', 'sum1'),
            ('square', 'minus1'),
            ('square', 'times2'),
            ('sum1', 'if_is_even'),
            ('if_is_even', 'square_root'),
            ('if_is_even', 'forward'),
            ('square_root', 'Converge'),
            ('forward', 'Converge'),
            ('minus1', 'natural_logarithm'),
            ('times2', 'divide_by_2'),
            ('natural_logarithm', 'Converge'),
            ('divide_by_2', 'Converge'),
            ('Converge', 'sum_tuple3')
        ]

        self._assert_graph_has_edges(divergent, graph, expected_edges)

    def test_nested_divergent_case(self):
        divergent = square >> (
            square_root >> sum1 >> (
                minus1,
                natural_logarithm
            ),
            times2 >> divide_by_2
        ) >> sum_tuple2

        graph: DiGraph = divergent.graph()

        nodes = graph.nodes.items()
        self.assertEqual(10, len(nodes))  # Each divergent connection has a hidden node

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(11, len(edges))

        expected_edges = [
            ('square', 'square_root'),
            ('square', 'times2'),
            ('square_root', 'sum1'),
            ('sum1', 'minus1'),
            ('sum1', 'natural_logarithm'),
            ('times2', 'divide_by_2'),
        ]

        self._assert_graph_has_edges(divergent, graph, expected_edges)

    def test_simple_conditional_case(self):

        conditional = square_root >> if_is_even.Then(sum1).Else(forward) >> minus1

        graph: DiGraph = conditional.graph()

        nodes = graph.nodes.items()
        self.assertEqual(5, len(nodes))

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(5, len(edges))

        expected_edges = [
            ('square_root', 'if_is_even'),
            ('if_is_even', 'sum1'),
            ('if_is_even', 'forward'),
            ('sum1', 'minus1'),
            ('forward', 'minus1'),
        ]

        self._assert_graph_has_edges(conditional, graph, expected_edges)

    def test_complex_conditional_case(self):

        then_graph = (
            sum1 >> square >> (
                times2,
                divide_by_2
            ) >> sum_tuple2
        )
        conditional = (
            square_root >>
            if_is_even.Then(then_graph).Else(forward) >>
            minus1
        )

        graph: DiGraph = conditional.graph()

        nodes = graph.nodes.items()
        self.assertEqual(10, len(nodes))

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(11, len(edges))

        expected_edges = [
            ('square_root', 'if_is_even'),
            ('if_is_even', 'sum1'),
            ('if_is_even', 'forward'),
            ('sum1', 'square'),
            ('square', 'times2'),
            ('square', 'divide_by_2'),
            ('times2', 'Converge'),
            ('divide_by_2', 'Converge'),
            ('Converge', 'sum_tuple2'),
            ('sum_tuple2', 'minus1'),
            ('forward', 'minus1'),
        ]

        self._assert_graph_has_edges(conditional, graph, expected_edges)

    def test_repeated_nodes_case(self):

        repeated = sum1 >> sum1 >> (
            sum1 >> sum1 >> sum1,
            minus1 >> minus1
        ) >> sum_tuple2

        graph: DiGraph = repeated.graph()

        nodes = graph.nodes.items()
        self.assertEqual(9, len(nodes))

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(9, len(edges))

    def test_begin_node_case(self):

        begin = Begin[float]() >> (
            sum1,
            minus1
        ) >> sum_tuple2

        graph: DiGraph = begin.graph()

        nodes = graph.nodes.items()
        self.assertEqual(5, len(nodes))

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(5, len(edges))

        expected_edges = [
            ('Begin', 'sum1'),
            ('Begin', 'minus1'),
            ('sum1', 'Converge'),
            ('minus1', 'Converge'),
            ('Converge', 'sum_tuple2')
        ]

        self._assert_graph_has_edges(begin, graph, expected_edges)

    def test_invisible_nodes_case(self):

        begin1 = Begin[float]() >> (
            sum1,
            minus1
        ) >> sum_tuple2

        begin2 = Begin[float]() >> (
            divide_by_2,
            times2
        ) >> mul_tuple2

        begin = begin1 >> begin2

        graph: DiGraph = begin.graph()

        nodes = graph.nodes.items()
        self.assertEqual(9, len(nodes))

        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(10, len(edges))
