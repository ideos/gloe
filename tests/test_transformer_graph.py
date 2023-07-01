import unittest
from typing import Any

from networkx import DiGraph

from lib.conditioners import if_is_even
from lib.transformers import divide_by_2, logarithm, minus1, \
    mul_tuple2, natural_logarithm, \
    square, \
    square_root, \
    sum1, \
    sum_tuple2, \
    sum_tuple3, times2
from src.gloe import Begin, Transformer
from src.gloe.utils import forward


class TestTransformerGraph(unittest.TestCase):
    def _get_nodes_by_name(self, transformer: Transformer) -> dict[str, str]:
        ids_by_name = {
            node.__class__.__name__: str(id)
            for id, node in transformer.graph_nodes.items()
        }

        return ids_by_name

    def _assert_graph_has_edges(
        self,
        transformer: Transformer,
        graph: DiGraph,
        expected_edges: list[tuple[str, str]]
    ):
        ids_by_name = self._get_nodes_by_name(transformer)

        edges = [edge for edge, props in list(graph.edges.items())]

        edges_with_id = [(ids_by_name[edge[0]], ids_by_name[edge[1]]) for edge in expected_edges]

        for edge in edges_with_id:
            self.assertIn(edge, edges)

    def _assert_nodes_count(self, expected: int, graph: DiGraph):
        nodes = graph.nodes.items()
        self.assertEqual(expected, len(nodes))

    def _assert_edges_count(self, expected: int, graph: DiGraph):
        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(expected, len(edges))

    def _assert_nodes_properties(
        self,
        nodes_properties: dict[str, dict[str, Any]],
        transformer: Transformer,
        graph: DiGraph
    ):
        ids_by_name = self._get_nodes_by_name(transformer)
        props_by_id = dict(graph.nodes)
        for name, properties in nodes_properties.items():
            node_id = ids_by_name[name]
            current_props = props_by_id[node_id]
            expected_props = nodes_properties[name]
            self.assertDictEqual(current_props | expected_props, current_props)

    def test_simplest_case(self):
        identity = square >> square_root >> sum1 >> minus1
        graph: DiGraph = identity.graph()

        self._assert_nodes_count(4, graph)
        self._assert_edges_count(3, graph)

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

        self._assert_nodes_count(5, graph)

        # Five edges:
        #           +---->  sum1  ----+
        #  square --+                 +--> (Converge) --> sum_tuple2
        #           +----> minus1 ----+
        self._assert_edges_count(5, graph)

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

        self._assert_nodes_count(11, graph)  # Each divergent connection has a hidden node
        self._assert_edges_count(13, graph)

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

        self._assert_nodes_count(10, graph)  # Each divergent connection has a hidden node
        self._assert_edges_count(11, graph)

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

        self._assert_nodes_count(5, graph)
        self._assert_edges_count(5, graph)

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

        self._assert_nodes_count(10, graph)
        self._assert_edges_count(11, graph)

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

        self._assert_nodes_count(9, graph)
        self._assert_edges_count(9, graph)

    def test_begin_node_case(self):

        begin = Begin[float]() >> (
            sum1,
            minus1
        ) >> sum_tuple2

        graph: DiGraph = begin.graph()

        self._assert_nodes_count(5, graph)
        self._assert_edges_count(5, graph)

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

        self._assert_nodes_count(9, graph)
        self._assert_edges_count(10, graph)

    def test_transformer_init_case(self):
        init_graph = logarithm(2) >> square

        graph: DiGraph = init_graph.graph()

        self._assert_nodes_count(2, graph)
        self._assert_edges_count(1, graph)

        expected_edges = [
            ('logarithm', 'square'),
        ]

        self._assert_graph_has_edges(init_graph, graph, expected_edges)

    def test_nodes_properties_case(self):
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

        graph = conditional.graph()

        box_nodes = [
            'sum1', 'square', 'times2', 'divide_by_2', 'sum_tuple2', 'square_root', 'minus1',
        ]
        box_nodes_properties = {
            node: {'label': node, 'shape': 'box'}
            for node in box_nodes
        }
        nodes_properties = {
            **box_nodes_properties,
            'Converge': {
                'label': '',
                'shape': 'diamond'
            },
            'if_is_even': {
                'label': 'if_is_even',
                'shape': 'diamond'
            }
        }

        self._assert_nodes_properties(nodes_properties, conditional, graph)
