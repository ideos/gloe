from __future__ import annotations

import tempfile
import unittest
from importlib.util import find_spec
from pathlib import Path
from unittest import TestCase

import gloe

from .scenarios import increment, stringify


class GraphProjectionTests(TestCase):
    def test_graph_inspection_never_executes_stage_code(self) -> None:
        def dangerous(value: int) -> int:
            raise AssertionError("graph inspection executed a stage")

        graph = (gloe.input() >> dangerous >> increment).graph()
        labels = [data["label"] for data in graph.nodes.values()]
        self.assertEqual(labels, ["input", "dangerous", "increment", "output"])
        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(
            {data["kind"] for data in graph.nodes.values()},
            {"input", "stage", "output"},
        )

    def test_repeated_functions_keep_distinct_occurrences(self) -> None:
        graph = (gloe.input() >> increment >> increment).graph()
        self.assertEqual(
            [data["label"] for data in graph.nodes.values()].count("increment"),
            2,
        )
        self.assertEqual(len(graph.edges), 3)

    def test_nested_fanout_has_distinct_forks_joins_and_identity(self) -> None:
        left = gloe.input() >> increment >> (increment, stringify)
        pipe = gloe.input() >> (left, stringify)
        graph = pipe.graph()
        labels = [data["label"] for data in graph.nodes.values()]
        self.assertEqual(labels.count("fork"), 2)
        self.assertEqual(labels.count("join"), 2)
        self.assertEqual(labels.count("identity"), 0)
        self.assertEqual(len(graph.nodes), 10)
        self.assertEqual(len(graph.edges), 11)
        self.assertEqual(pipe.sync(2), ((4, "3"), "2"))

    def test_identity_branch_is_projected_as_an_occurrence(self) -> None:
        pipe = gloe.input() >> (gloe.input(), increment)
        graph = pipe.graph()
        self.assertIn("identity", [data["label"] for data in graph.nodes.values()])
        self.assertEqual(pipe.sync(2), (2, 3))

    def test_configured_and_root_functions_keep_useful_labels(self) -> None:
        @gloe.transformer
        def add(value: int, *, amount: int) -> int:
            return value + amount

        configured = gloe.input() >> add(amount=2)
        root = gloe.Transformer(increment) >> stringify
        self.assertEqual(
            [data["label"] for data in configured.graph().nodes.values()],
            ["input", "add", "output"],
        )
        self.assertEqual(
            [data["label"] for data in root.graph().nodes.values()],
            ["input", "increment", "stringify", "output"],
        )

    def test_callback_helpers_are_nested_with_dashed_use_edges(self) -> None:
        graph = (gloe.input() >> gloe.map(increment)).graph()
        callback_nodes = [
            node for node, data in graph.nodes.items() if data["kind"] == "callback"
        ]
        self.assertEqual(len(callback_nodes), 1)
        self.assertTrue(
            any(
                edge[0] != callback_nodes[0]
                and attrs.get("style") == "dashed"
                and attrs.get("label") == "uses"
                for edge, attrs in graph.edges.items()
            )
        )

    def test_extending_pipeline_does_not_change_original_graph(self) -> None:
        original = gloe.input() >> increment
        before = original.graph()
        extended = original >> stringify
        self.assertEqual(
            [data["label"] for data in original.graph().nodes.values()],
            [data["label"] for data in before.nodes.values()],
        )
        self.assertEqual(
            [data["label"] for data in extended.graph().nodes.values()],
            ["input", "increment", "stringify", "output"],
        )

    def test_dot_export_returns_text_and_writes_requested_path(self) -> None:
        pipe = gloe.input() >> increment
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pipeline.dot"
            dot = pipe.to_dot(path)
            self.assertEqual(dot, path.read_text(encoding="utf-8"))
            self.assertIn("digraph pipeline", dot)
            self.assertIn("increment", dot)

    @unittest.skipUnless(
        find_spec("pygraphviz") is not None,
        "optional Graphviz dependency is not installed",
    )
    def test_image_export_writes_svg_when_graphviz_is_available(self) -> None:
        pipe = gloe.input() >> increment
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pipeline.svg"
            pipe.to_image(path)
            self.assertTrue(path.exists())
            self.assertIn("<svg", path.read_text(encoding="utf-8"))
