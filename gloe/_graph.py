"""Deterministic graph projection. Inspection never executes pipeline stages."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ._core import Transformer


@dataclass
class Graph:
    """An independent graph snapshot with occurrence IDs and labelled edges."""

    nodes: dict[str, dict[str, str]] = field(default_factory=dict)
    edges: dict[tuple[str, str], dict[str, str]] = field(default_factory=dict)

    def to_dot(self, path: str | Path | None = None) -> str:
        def attrs(values: dict[str, str]) -> str:
            return ", ".join(
                f"{key}={json.dumps(value)}" for key, value in values.items()
            )

        lines = ["digraph pipeline {", "  rankdir=LR;"]
        lines.extend(f"  {node} [{attrs(data)}];" for node, data in self.nodes.items())
        lines.extend(
            f"  {start} -> {end} [{attrs(data)}];"
            for (start, end), data in self.edges.items()
        )
        lines.append("}")
        result = "\n".join(lines) + "\n"
        if path is not None:
            Path(path).write_text(result, encoding="utf-8")
        return result

    def to_image(self, path: str | Path, *, prog: str = "dot") -> None:
        try:
            import pygraphviz
        except ImportError as error:
            raise ImportError(
                "Image export requires Graphviz and gloe[plot]"
            ) from error
        graph = pygraphviz.AGraph(string=self.to_dot())
        graph.draw(str(path), prog=prog)


def build_graph(pipeline: Transformer[..., Any]) -> Graph:
    from ._core import Transformer, input

    graph = Graph()

    def node(label: str, kind: str = "stage") -> str:
        key = f"n{len(graph.nodes)}"
        graph.nodes[key] = {"label": label, "kind": kind}
        return key

    def edge(start: str, end: str, **attrs: str) -> None:
        graph.edges[start, end] = attrs

    def visit(value: object, previous: str) -> str:
        if type(value) in (Transformer, input):
            value = cast(Transformer[..., Any], value)
            if value._source is not None:
                previous = visit(value._source, previous)
            for stage in value._steps:
                previous = visit(stage, previous)
            return previous
        if isinstance(value, tuple):
            fork = node("fork", "fork")
            edge(previous, fork)
            outputs = [visit(branch, fork) for branch in value]
            join = node("join", "join")
            for index, output in enumerate(outputs):
                # Identity branches need distinct occurrences even with no stages.
                identity = node("identity", "identity") if output == fork else output
                if identity != output:
                    edge(fork, identity)
                edge(identity, join, label=str(index))
            if not value:
                edge(fork, join)
            return join
        label = getattr(value, "__gloe_label__", None)
        if label is None:
            label = getattr(value, "__name__", type(value).__name__)
        current = node(str(label))
        edge(previous, current)
        children = getattr(value, "__gloe_children__", ())
        for index, child in enumerate(children):
            # Callback bodies belong to the helper, not to its outer sequence.
            scope = node(f"callback {index}", "callback")
            edge(current, scope, style="dashed", label="uses")
            visit(child, scope)
        return current

    start = node("input", "input")
    end = visit(pipeline, start)
    edge(end, node("output", "output"))
    return graph
