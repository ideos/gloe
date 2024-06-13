from typing import Any


class GloeGraph:
    def __init__(self, name: str = ""):
        self.name = name
        self.attrs: dict[str, Any] = {}
        self.nodes: dict[str, Any] = {}
        self.edges: dict[tuple[str, str], Any] = {}
        self.subgraphs: list["GloeGraph"] = []

    def add_node(self, id: str, **attrs):
        self.nodes[id] = attrs

    def add_edge(self, u: str, v: str, **attrs):
        _attrs = {key: val for key, val in attrs.items() if val is not None}

        self.edges[(u, v)] = _attrs

    def add_subgraph(self, subgraph: "GloeGraph"):
        self.subgraphs.append(subgraph)

    def to_agraph(self, with_edge_labels: bool = True):
        try:
            import pygraphviz  # noqa: F401

        except ImportError as err:
            raise ImportError(
                "Please, the module pygraphviz is required for this method,"
                + " install with "
                + """"conda install --channel conda-forge pygraphviz" or """
                + """"pip install pygraphviz". More information is available in """
                + "https://pygraphviz.github.io/documentation/stable/install.html"
            ) from err

        A = pygraphviz.AGraph(
            name=self.name, compound=True, directed=True, style="dotted", **self.attrs
        )

        subgraphs_stack = [(self, self.subgraphs)]
        sub_agraph = A
        while len(subgraphs_stack) > 0:
            graph, subgraphs = subgraphs_stack.pop(0)
            for subgraph in subgraphs:
                sub_agraph = sub_agraph.add_subgraph(
                    name=subgraph.name, **subgraph.attrs
                )

                for node, nodedata in subgraph.nodes.items():
                    sub_agraph.add_node(node, **nodedata)

                for (u, v), edgedata in subgraph.edges.items():
                    if not with_edge_labels and "label" in edgedata:
                        del edgedata["label"]
                    sub_agraph.add_edge(u, v, **edgedata)

                if len(subgraph.subgraphs) > 0:
                    subgraphs_stack.append((subgraph, subgraph.subgraphs))

        for node, nodedata in self.nodes.items():
            A.add_node(node, **nodedata)

        for (u, v), edgedata in self.edges.items():
            if not with_edge_labels and "label" in edgedata:
                del edgedata["label"]
            A.add_edge(u, v, **edgedata)

        return A
