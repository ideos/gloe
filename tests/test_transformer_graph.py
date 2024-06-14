import unittest
from typing import Any
from gloe import transformer, BaseTransformer
from gloe._gloe_graph import GloeGraph
from gloe.collection import Map
from gloe.utils import forward

from tests.lib.conditioners import if_is_even
from tests.lib.transformers import (
    identity,
    square,
    square_root,
    plus1,
    minus1,
    divide_by_2,
    times2,
    sum_tuple2,
    sum_tuple3,
    mul_tuple2,
    natural_logarithm,
    logarithm,
    to_string,
    tuple_concatenate,
)


class TestTransformerGraph(unittest.TestCase):
    def _get_nodes_by_name(self, graph: GloeGraph) -> dict[str, str]:
        ids_by_name = {}
        for id, attrs in graph.nodes.items():
            _transformer = attrs.get("transformer")
            if _transformer is not None and isinstance(_transformer, BaseTransformer):
                ids_by_name[_transformer.label] = id
            elif label := attrs.get("_label"):
                ids_by_name[label] = id
        return ids_by_name

        return ids_by_name

    def _assert_graph_has_edges(
        self,
        graph: GloeGraph,
        expected_edges: list[tuple[str, str]],
    ):
        ids_by_name = self._get_nodes_by_name(graph)

        edges = [edge for edge, props in list(graph.edges.items())]

        edges_with_id = [
            (ids_by_name[edge[0]], ids_by_name[edge[1]]) for edge in expected_edges
        ]

        for edge in edges_with_id:
            self.assertIn(edge, edges)

    def _assert_edge_properties(
        self,
        graph: GloeGraph,
        expected_edges_props: dict[tuple[str, str], Any],
    ):
        ids_by_name = self._get_nodes_by_name(graph)
        edges_with_id = {
            (ids_by_name[edge[0]], ids_by_name[edge[1]]): props
            for edge, props in expected_edges_props.items()
        }
        current_edge_props = {(u, v): graph.edges[(u, v)] for u, v in edges_with_id}

        for edge, current_props in current_edge_props.items():
            expected_props = edges_with_id[edge]
            self.assertDictEqual(current_props | expected_props, current_props)

    def _assert_nodes_count(self, expected: int, graph: GloeGraph):
        nodes = graph.nodes.items()
        self.assertEqual(expected + 2, len(nodes))  # + 2 for begin and end nodes

    def _assert_edges_count(self, expected: int, graph: GloeGraph):
        edges = [edge for edge, props in list(graph.edges.items())]
        self.assertEqual(expected + 2, len(edges))  # + 2 for begin and end nodes

    def _assert_nodes_properties(
        self,
        nodes_properties: dict[str, dict[str, Any]],
        graph: GloeGraph,
    ):
        ids_by_name = self._get_nodes_by_name(graph)
        props_by_id = dict(graph.nodes)
        for name, properties in nodes_properties.items():
            node_id = ids_by_name[name]
            current_props = props_by_id[node_id]
            expected_props = nodes_properties[name]
            self.assertDictEqual(current_props | expected_props, current_props)

    def test_simplest_case(self):
        identity = square >> square_root >> plus1 >> minus1
        graph: GloeGraph = identity.graph()

        self._assert_nodes_count(4, graph)
        self._assert_edges_count(3, graph)

        expected_edges = [
            ("square", "square_root"),
            ("square_root", "plus1"),
            ("plus1", "minus1"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_simple_divergent_case(self):
        divergent = square >> (plus1, minus1) >> sum_tuple2

        graph: GloeGraph = divergent.graph()

        self._assert_nodes_count(6, graph)

        # Five edges:
        #                         +---->  plus1  ----+
        #  square --> (Gateway) --+                  +--> (Converge) --> sum_tuple2
        #                         +----> minus1 -----+
        self._assert_edges_count(6, graph)

        expected_edges = [
            ("square", "gateway_begin"),
            ("square", "gateway_begin"),
            ("gateway_begin", "plus1"),
            ("gateway_begin", "minus1"),
            ("plus1", "gateway_end"),
            ("minus1", "gateway_end"),
            ("gateway_end", "sum_tuple2"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_complex_divergent_case(self):
        divergent = (
            square
            >> (
                plus1 >> if_is_even.Then(square_root).Else(forward()),
                minus1 >> natural_logarithm,
                times2 >> divide_by_2,
            )
            >> sum_tuple3
        )
        graph: GloeGraph = divergent.graph()

        # Each divergent connection has a hidden node
        self._assert_nodes_count(12, graph)
        self._assert_edges_count(14, graph)

        expected_edges = [
            ("square", "gateway_begin"),
            ("gateway_begin", "minus1"),
            ("gateway_begin", "plus1"),
            ("gateway_begin", "times2"),
            ("plus1", "if_is_even"),
            ("if_is_even", "square_root"),
            ("if_is_even", "if_is_even_end"),
            ("square_root", "if_is_even_end"),
            ("minus1", "natural_logarithm"),
            ("times2", "divide_by_2"),
            ("if_is_even_end", "gateway_end"),
            ("natural_logarithm", "gateway_end"),
            ("divide_by_2", "gateway_end"),
            ("gateway_end", "sum_tuple3"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_nested_divergent_case(self):
        @transformer
        def aux_last(data: tuple[tuple[float, float], float]) -> float:
            ((n1, n2), n3) = data
            return n1 + n2 + n3

        divergent = (
            square
            >> (
                square_root >> plus1 >> (minus1 >> identity, natural_logarithm),
                times2 >> divide_by_2,
            )
            >> aux_last
        )

        graph: GloeGraph = divergent.graph()

        # Each divergent connection has a hidden node
        self._assert_nodes_count(13, graph)
        self._assert_edges_count(14, graph)

        expected_edges = [
            ("square_root", "plus1"),
            ("minus1", "identity"),
            ("times2", "divide_by_2"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_simple_conditional_case(self):
        conditional = square_root >> if_is_even.Then(plus1).Else(forward()) >> minus1

        graph: GloeGraph = conditional.graph()

        self._assert_nodes_count(5, graph)
        self._assert_edges_count(5, graph)

        expected_edges = [
            ("square_root", "if_is_even"),
            ("if_is_even", "plus1"),
            ("if_is_even", "if_is_even_end"),
            ("if_is_even_end", "minus1"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_complex_conditional_case(self):
        then_graph = plus1 >> square >> (times2, divide_by_2) >> sum_tuple2
        conditional = (
            square_root >> if_is_even.Then(then_graph).Else(forward()) >> minus1
        )

        graph: GloeGraph = conditional.graph()

        self._assert_nodes_count(11, graph)
        self._assert_edges_count(12, graph)

        expected_edges = [
            ("square_root", "if_is_even"),
            ("if_is_even", "plus1"),
            ("if_is_even", "if_is_even_end"),
            ("plus1", "square"),
            ("square", "gateway_begin"),
            ("square", "gateway_begin"),
            ("gateway_begin", "times2"),
            ("gateway_begin", "divide_by_2"),
            ("times2", "gateway_end"),
            ("divide_by_2", "gateway_end"),
            ("gateway_end", "sum_tuple2"),
            ("sum_tuple2", "if_is_even_end"),
            ("if_is_even", "if_is_even_end"),
            ("if_is_even_end", "minus1"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_repeated_nodes_case(self):
        repeated = (
            plus1 >> plus1 >> (plus1 >> plus1 >> plus1, minus1 >> minus1) >> sum_tuple2
        )

        graph: GloeGraph = repeated.graph()

        self._assert_nodes_count(10, graph)
        self._assert_edges_count(10, graph)

    def test_begin_node_case(self):
        begin1 = forward[float]() >> (plus1, minus1) >> sum_tuple2

        graph: GloeGraph = begin1.graph()

        self._assert_nodes_count(5, graph)
        self._assert_edges_count(5, graph)

        expected_edges = [
            ("gateway_begin", "plus1"),
            ("gateway_begin", "minus1"),
            ("plus1", "gateway_end"),
            ("minus1", "gateway_end"),
            ("gateway_end", "sum_tuple2"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_invisible_nodes_case(self):
        begin1 = forward[float]() >> (plus1, minus1) >> sum_tuple2

        begin2 = forward[float]() >> (divide_by_2, times2) >> mul_tuple2

        begin3 = begin1 >> begin2

        graph: GloeGraph = begin3.graph()

        self._assert_nodes_count(10, graph)
        self._assert_edges_count(11, graph)

    def test_partial_transformer_case(self):
        init_graph = logarithm(2) >> square

        graph: GloeGraph = init_graph.graph()

        self._assert_nodes_count(2, graph)
        self._assert_edges_count(1, graph)

        expected_edges = [
            ("logarithm", "square"),
        ]

        self._assert_graph_has_edges(graph, expected_edges)

    def test_nodes_properties_case(self):
        then_graph = plus1 >> square >> (times2, divide_by_2) >> sum_tuple2
        conditional = (
            square_root >> if_is_even.Then(then_graph).Else(forward()) >> minus1
        )

        graph = conditional.graph()

        box_nodes = [
            "plus1",
            "square",
            "times2",
            "divide_by_2",
            "sum_tuple2",
            "square_root",
            "minus1",
        ]
        box_nodes_properties = {
            node: {"label": node, "shape": "box"} for node in box_nodes
        }
        nodes_properties = {
            **box_nodes_properties,
            "gateway_end": {"label": "", "shape": "diamond"},
            "if_is_even": {"label": "if_is_even", "shape": "diamond"},
        }

        self._assert_nodes_properties(nodes_properties, graph)

    def test_edge_labels_case(self):
        single_edge = plus1 >> square
        graph = single_edge.graph()

        expected_edge_props = {("plus1", "square"): {"label": "float"}}

        self._assert_edge_properties(graph, expected_edge_props)

        divergent_edges = (
            plus1 >> (square >> to_string, square_root) >> tuple_concatenate
        )
        graph = divergent_edges.graph()
        expected_edge_props = {
            ("plus1", "gateway_begin"): {"label": "float"},
            ("gateway_begin", "square"): {"label": "float"},
            ("gateway_begin", "square_root"): {"label": "float"},
            ("square", "to_string"): {"label": "float"},
            ("to_string", "gateway_end"): {"label": "str"},
            ("square_root", "gateway_end"): {"label": "float"},
            ("gateway_end", "tuple_concatenate"): {"label": "(str, float)"},
        }

        self._assert_edge_properties(graph, expected_edge_props)

    def test_subgraphs(self):
        nested_transformer = forward[list[int]]() >> Map(square >> square_root)
        nested_graph = nested_transformer.graph()
        subgraphs = nested_graph.subgraphs
        self.assertEqual(len(subgraphs), 1)

        subgraph = subgraphs[0]
        self._assert_nodes_count(2, subgraph)
        self._assert_edges_count(1, subgraph)

        expected_edges = [
            ("square", "square_root"),
        ]

        self._assert_graph_has_edges(subgraph, expected_edges)
