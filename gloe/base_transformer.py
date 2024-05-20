import copy
import types
import uuid
import inspect
from abc import ABC, abstractmethod
from inspect import Signature

import networkx as nx
from networkx import DiGraph, Graph
from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
    Union,
    Iterable,
    get_args,
    get_origin,
    Type,
    Optional,
    Awaitable,
)
from uuid import UUID
from itertools import groupby

from typing_extensions import Self, TypeAlias

from gloe._plotting_utils import PlottingSettings, NodeType, export_dot_props
from gloe._typing_utils import _format_return_annotation

__all__ = ["BaseTransformer", "TransformerException", "PreviousTransformer"]

_NextOut = TypeVar("_NextOut")
_Self = TypeVar("_Self", bound="BaseTransformer")

_Out2 = TypeVar("_Out2")
_Out3 = TypeVar("_Out3")
_Out4 = TypeVar("_Out4")
_Out5 = TypeVar("_Out5")
_Out6 = TypeVar("_Out6")
_Out7 = TypeVar("_Out7")


PreviousTransformer: TypeAlias = Union[
    None,
    _Self,
    tuple[_Self, _Self],
    tuple[_Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self, _Self, _Self],
    tuple[_Self, _Self, _Self, _Self, _Self, _Self, _Self],
]

TransformerChildren: TypeAlias = list["BaseTransformer"]


class TransformerException(Exception):
    def __init__(
        self,
        internal_exception: Union["TransformerException", Exception],
        raiser_transformer: "BaseTransformer",
        message: Union[str, None] = None,
    ):
        self._internal_exception = internal_exception
        self.raiser_transformer = raiser_transformer
        self._traceback = internal_exception.__traceback__
        internal_exception.__cause__ = self
        super().__init__(message)

    @property
    def internal_exception(self):
        return self._internal_exception.with_traceback(self._traceback)


_In = TypeVar("_In", contravariant=True)
_Out = TypeVar("_Out", covariant=True)


Flow = list["BaseTransformer"]


class BaseTransformer(Generic[_In, _Out], ABC):
    def __init__(self):
        self._children: TransformerChildren = []
        self.id = uuid.uuid4()
        self.instance_id = uuid.uuid4()
        self.is_atomic = False
        self._label = self.__class__.__name__
        self._already_copied = False
        self._plotting_settings: PlottingSettings = PlottingSettings(
            invisible=False,
            node_type=NodeType.Transformer,
        )
        self._flow: Flow = [self]

    @property
    def label(self) -> str:
        """
        Label used in visualization.

        When the transformer is created by the `@transformer` decorator, it is the
        name of the function.

        When creating a transformer by extending the `Transformer` class, it is the name
        of the class.
        """
        return self._label

    @property
    def children(self) -> TransformerChildren:
        """
        Used when a transformer encapsulates other transformer. The encapsulated
        transformers are called children transformers.
        """
        return self._children

    @property
    def plotting_settings(self) -> PlottingSettings:
        """
        Defines how the transformer will be plotted.
        """
        return self._plotting_settings

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, BaseTransformer):
            return self.id == other.id
        return NotImplemented

    def _copy(
        self: Self,
        transform: Optional[Callable[[Self, _In], _Out]] = None,
        regenerate_instance_id: bool = False,
        transform_method: str = "transform",
        force: bool = False,
    ) -> Self:
        if self._already_copied and not force:
            return self

        copied: Self = copy.copy(self)

        func_type = types.MethodType
        if transform is not None:
            setattr(copied, transform_method, func_type(transform, copied))

        old_instance_id = self.instance_id
        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()

        copied._children = [
            child.copy(regenerate_instance_id=True) for child in self.children
        ]

        copied._flow = [
            (
                copied
                if child.instance_id == old_instance_id
                else child.copy(regenerate_instance_id=regenerate_instance_id)
            )
            for child in self._flow
        ]
        copied._already_copied = True
        return copied

    def copy(
        self: Self,
        transform: Optional[Callable[[Self, _In], _Out]] = None,
        regenerate_instance_id: bool = False,
        force: bool = False,
    ) -> Self:
        return self._copy(transform, regenerate_instance_id, "transform", force)

    @property
    def graph_nodes(self) -> dict[UUID, Optional["BaseTransformer"]]:
        graph = self.graph()

        nodes = {}
        for node_id, attrs in graph.nodes.items():
            nodes[node_id] = attrs.get("transformer")

        return nodes

    @abstractmethod
    def signature(self) -> Signature:
        """Transformer function-like signature"""

    @abstractmethod
    def __call__(self, data: _In) -> Union[_Out, Awaitable[_Out]]:
        """Transformer function-like signature"""

    def _signature(self, klass: Type, transform_method: str = "transform") -> Signature:
        orig_bases = getattr(self, "__orig_bases__", [])
        transformer_args = [
            get_args(base) for base in orig_bases if get_origin(base) == klass
        ]
        generic_args = [
            get_args(base) for base in orig_bases if get_origin(base) == Generic
        ]

        orig_class = getattr(self, "__orig_class__", None)

        specific_args = {}
        if (
            len(transformer_args) == 1
            and len(generic_args) == 1
            and orig_class is not None
        ):
            generic_arg = generic_args[0]
            transformer_arg = transformer_args[0]
            specific_args = {
                generic: specific
                for generic, specific in zip(generic_arg, get_args(orig_class))
                if generic in transformer_arg
            }

        signature = inspect.signature(getattr(self, transform_method))
        new_return_annotation = specific_args.get(
            signature.return_annotation, signature.return_annotation
        )
        parameters = list(signature.parameters.values())
        if len(parameters) > 0:
            parameter = parameters[0]
            parameter = parameter.replace(
                annotation=specific_args.get(parameter.annotation, parameter.annotation)
            )
            parameters = [parameter]

        return signature.replace(
            return_annotation=new_return_annotation,
            parameters=parameters,
        )

    @property
    def output_type(self) -> Any:
        signature = self.signature()
        return signature.return_annotation

    @property
    def output_annotation(self) -> str:
        output_type = self.output_type

        return_type = _format_return_annotation(output_type, None, None)
        return return_type

    @property
    def input_type(self) -> Any:
        parameters = list(self.signature().parameters.items())
        if len(parameters) > 0:
            parameter_type = parameters[0][1].annotation
            return parameter_type

    @property
    def input_annotation(self) -> str:
        return self.input_type.__name__

    def _add_net_node(self, net: Graph, custom_data: dict[str, Any] = {}):
        node_id = self.node_id
        graph_node_props = export_dot_props(self.plotting_settings, self.instance_id)
        props = {
            **graph_node_props,
            **custom_data,
            "label": self.label,
            "transformer": self,
        }
        if node_id not in net.nodes:
            net.add_node(node_id, **props)
        else:
            nx.set_node_attributes(net, {node_id: props})
        return node_id

    def _add_child_node(
        self,
        child: "BaseTransformer",
        child_net: DiGraph,
        parent_id: str,
        next_node: "BaseTransformer",
    ):
        child._dag(child_net, next_node, custom_data={"parent_id": parent_id})

    @property
    def node_id(self) -> str:
        return str(self.instance_id)

    def _add_children_subgraph(self, net: DiGraph, next_node: "BaseTransformer"):
        next_node_id = next_node.node_id
        children_nets = [DiGraph() for _ in self.children]
        visible_previous = self.visible_previous

        for child, child_net in zip(self.children, children_nets):
            self._add_child_node(child, child_net, self.node_id, next_node)
            net.add_nodes_from(child_net.nodes.data())
            net.add_edges_from(child_net.edges.data())

            child_root_node = [
                n for n in child_net.nodes if child_net.in_degree(n) == 0
            ][0]
            child_final_node = [
                n for n in child_net.nodes if child_net.out_degree(n) == 0
            ][0]

            if self.plotting_settings.invisible:
                if type(visible_previous) is tuple:
                    for prev in visible_previous:
                        net.add_edge(
                            prev.node_id, child_root_node, label=prev.output_annotation
                        )
                elif isinstance(visible_previous, BaseTransformer):
                    net.add_edge(
                        visible_previous.node_id,
                        child_root_node,
                        label=visible_previous.output_annotation,
                    )
            else:
                node_id = self._add_net_node(net)
                net.add_edge(node_id, child_root_node)

            if child_final_node != next_node_id:
                net.add_edge(
                    child_final_node, next_node_id, label=next_node.input_annotation
                )

    # def _dag(
    #     self,
    #     net: DiGraph,
    #     next_node: Union["BaseTransformer", None] = None,
    #     custom_data: dict[str, Any] = {},
    # ):
    #     in_nodes = [edge[1] for edge in net.in_edges()]
    #
    #     previous = self.previous
    #     if previous is not None:
    #         if type(previous) is tuple:
    #             if self.plotting_settings.invisible and next_node is not None:
    #                 next_node_id = next_node._add_net_node(net)
    #                 _next_node = next_node
    #             else:
    #                 next_node_id = self._add_net_node(net, custom_data)
    #                 _next_node = self
    #
    #             for prev in previous:
    #                 previous_node_id = prev.node_id
    #
    #                 # TODO: check the impact of the below line to the Mapper transformer
    #                 if not prev.plotting_settings.invisible and len(prev.children) == 0:
    #                     net.add_edge(
    #                         previous_node_id, next_node_id, label=prev.output_annotation
    #                     )
    #
    #                 if previous_node_id not in in_nodes:
    #                     prev._dag(net, _next_node, custom_data)
    #
    #         elif isinstance(previous, BaseTransformer):
    #             if self.plotting_settings.invisible and next_node is not None:
    #                 next_node_id = next_node._add_net_node(net)
    #                 _next_node = next_node
    #             else:
    #                 next_node_id = self._add_net_node(net, custom_data)
    #                 _next_node = self
    #
    #             previous_node_id = previous.node_id
    #
    #             if len(previous.children) == 0 and (
    #                 not previous.plotting_settings.invisible
    #                 or previous.previous is None
    #             ):
    #                 previous_node_id = previous._add_net_node(net)
    #                 net.add_edge(
    #                     previous_node_id, next_node_id, label=previous.output_annotation
    #                 )
    #
    #             if previous_node_id not in in_nodes:
    #                 previous._dag(net, _next_node, custom_data)
    #     else:
    #         self._add_net_node(net, custom_data)
    #
    #     if len(self.children) > 0 and next_node is not None:
    #         self._add_children_subgraph(net, next_node)
    def _dag(
        self,
        net: nx.DiGraph,
        root_nodes: list[Union[str, "BaseTransformer"]],
        flow: Flow,
    ) -> list["BaseTransformer"]:
        prev_nodes = root_nodes
        for node in flow:
            if isinstance(node, list):
                last_nodes = []
                for flow in node:
                    last_node = self._dag(net, prev_nodes, flow)
                    last_nodes.extend(last_node)
                converge_id = str(uuid.uuid4())
                net.add_node(converge_id, label="", shape="diamond")
                for last_node in last_nodes:
                    if isinstance(last_node, str):
                        net.add_edge(last_node, converge_id)
                    else:
                        net.add_edge(
                            last_node.node_id,
                            converge_id,
                            label=last_node.output_annotation,
                        )
                prev_nodes = [converge_id]
            else:
                node_id = node._add_net_node(net)
                for prev_node in prev_nodes:
                    if isinstance(prev_node, str):
                        net.add_edge(prev_node, node_id, label=node.input_annotation)
                    else:
                        net.add_edge(
                            prev_node.node_id,
                            node_id,
                            label=prev_node.output_annotation,
                        )
                prev_nodes = [node]
        return prev_nodes

    def graph(self) -> DiGraph:
        net = nx.DiGraph()
        net.graph["splines"] = "ortho"
        net.add_node("begin", label="", shape="circle")

        last_nodes = self._dag(net, ["begin"], self._flow)

        net.add_node("end", label="", shape="doublecircle")
        for last_node in last_nodes:
            net.add_edge(last_node.node_id, "end", label=last_node.output_annotation)
        return net

    def export(self, path: str, with_edge_labels: bool = True):  # pragma: no cover
        """Export Transformer object in dot format"""

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

        net = self.graph()
        boxed_nodes = [
            node
            for node in net.nodes.data()
            if "parent_id" in node[1] and "bounding_box" in node[1]
        ]
        if not with_edge_labels:
            for u, v in net.edges:
                net.edges[u, v]["label"] = ""

        agraph = nx.nx_agraph.to_agraph(net)
        subgraphs: Iterable[tuple] = groupby(
            boxed_nodes, key=lambda x: x[1]["parent_id"]
        )
        for parent_id, nodes in subgraphs:
            nodes = list(nodes)
            node_ids = [node[0] for node in nodes]
            if len(nodes) > 0:
                label = nodes[0][1]["box_label"]
                agraph.add_subgraph(
                    node_ids, label=label, name=f"cluster_{parent_id}", style="dotted"
                )
        agraph.write(path)

    def __len__(self):
        return 1
