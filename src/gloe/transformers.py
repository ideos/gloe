import copy
import types
import uuid
import inspect
from abc import ABC, abstractmethod
from functools import cached_property
from inspect import Signature
import networkx as nx
from networkx import DiGraph, Graph
from types import GenericAlias
from typing import Any, \
    Callable, \
    Generic, \
    Tuple, \
    TypeAlias, TypeVar, \
    Union, cast, overload
from uuid import UUID
from itertools import groupby
from typing_extensions import Self

from ._utils import _format_return_annotation
from .sequential_pass import SequentialPass

_A = TypeVar("_A")
_S = TypeVar("_S")
_U = TypeVar("_U")

_R1 = TypeVar("_R1")
_R2 = TypeVar("_R2")
_R3 = TypeVar("_R3")
_R4 = TypeVar("_R4")
_R5 = TypeVar("_R5")
_R6 = TypeVar("_R6")


class TransformerHandler(Generic[_A, _S], ABC):

    @abstractmethod
    def handle(self, input_data: _A, output: _S):
        pass


PreviousTransformer: TypeAlias = Union[
    None,
    'Transformer',
    tuple['Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer']
]


class TransformerException(Exception):

    def __init__(
        self,
        internal_exception: Union['TransformerException', Exception],
        raiser_transformer: 'Transformer',
        message: str | None = None
    ):
        self.internal_exception = internal_exception
        self.raiser_transformer = raiser_transformer
        internal_exception.__context__ = self
        super().__init__(message)


class Transformer(Generic[_A, _S], SequentialPass['Transformer'], ABC):
    """
    A Transformer is generic block with the responsibility to take an input of type `T`
    and transform it to an output of type `S`.


    Typical usage example:

    class Stringifier(Transformer[dict, str]):
        ...

    """

    @staticmethod
    def _merge_serial_connection(
        transformer1: 'Transformer[_A, _S]', _transformer2: 'Transformer[_S, _U]'
    ) -> 'Transformer[_A, _U]':
        if transformer1.previous is None:
            transformer1 = transformer1.copy(regenerate_instance_id=True)

        transformer2 = _transformer2.copy(regenerate_instance_id=True)
        transformer2._set_previous(transformer1)

        class NewTransformer(Transformer[_A, _U]):
            def transform(self, data: _A) -> _U:
                transformer2_call = transformer2.__call__
                transformer1_call = transformer1.__call__
                transformed = transformer2_call(transformer1_call(data))
                return transformed

            def signature(self) -> Signature:
                transformer1_signature: Signature = transformer1.signature()
                transformer2_signature: Signature = transformer2.signature()
                new_signature = transformer2_signature \
                    .replace(parameters=list(transformer1_signature.parameters.values()))
                return new_signature

            def __len__(self):
                return len(transformer1) + len(transformer2)

        new_transformer = NewTransformer()

        new_transformer.__class__.__name__ = transformer2.__class__.__name__
        new_transformer.label = transformer2.label
        new_transformer.children = transformer2.children
        new_transformer.invisible = transformer2.invisible
        new_transformer.graph_node_props = transformer2.graph_node_props
        new_transformer._set_previous(transformer2.previous)

        # if len(transformer2.children) > 0:
        #     setattr(new_transformer, '_add_net_node', transformer2._add_net_node)
        #     setattr(new_transformer, '_add_child_node', transformer2._add_child_node)

        return new_transformer

    @staticmethod
    def _merge_diverging_connection(
        incident_transformer: 'Transformer[_A, _S]',
        *receiving_transformers: 'Transformer[_S, Any]'
    ) -> 'Transformer[_A, tuple]':
        if incident_transformer.previous is None:
            incident_transformer = incident_transformer.copy(regenerate_instance_id=True)

        receiving_transformers = tuple([
            receiving_transformer.copy(regenerate_instance_id=True)
            for receiving_transformer in receiving_transformers
        ])

        for receiving_transformer in receiving_transformers:
            receiving_transformer._set_previous(incident_transformer)

        def split_result(data: _A) -> Tuple[Any, ...]:
            intermediate_result = incident_transformer(data)
            return tuple([
                receiving_transformer(intermediate_result)
                for receiving_transformer in receiving_transformers
            ])

        class NewTransformer(Transformer[_A, Tuple[Any, ...]]):

            def transform(self, data: _A) -> Tuple[Any, ...]:
                return split_result(data)

            def signature(self) -> Signature:
                incident_signature: Signature = incident_transformer.signature()
                receiving_signature_returns: list[str] = [
                    receiving_transformer.signature().return_annotation
                    for receiving_transformer in receiving_transformers
                ]
                new_signature = incident_signature.replace(
                    return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns))
                )
                return new_signature

            def __len__(self):
                lengths = [len(t) for t in receiving_transformers]
                return sum(lengths) + len(incident_transformer)

        new_transformer = NewTransformer()
        new_transformer.previous = cast(PreviousTransformer, receiving_transformers)
        new_transformer.__class__.__name__ = 'Converge'
        new_transformer.label = ''
        new_transformer.graph_node_props = {
            "shape": "diamond",
            "width": 0.5,
            "height": 0.5
        }

        return new_transformer

    def __init__(self):
        self._handlers: list[TransformerHandler[_A, _S]] = []
        self.previous: PreviousTransformer = None
        self.children: list[Transformer] = []
        self.invisible = False
        self.id = uuid.uuid4()
        self.instance_id = uuid.uuid4()
        self.label = self.__class__.__name__
        self.graph_node_props: dict[str, Any] = {
            "shape": "box"
        }
        self.__class__.__annotations__ = self.transform.__annotations__

    def __hash__(self):
        return self.id.int

    def __eq__(self, other):
        if isinstance(other, Transformer):
            return self.id == other.id
        return NotImplemented

    @abstractmethod
    def transform(self, data: _A) -> _S:
        pass

    def add_handler(self, handler: TransformerHandler[_A, _S]):
        if handler not in self._handlers:
            self._handlers = self._handlers + [handler]

        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
                for previous_transformer in previous:
                    previous_transformer.add_handler(handler)
            elif isinstance(previous, Transformer):
                previous.add_handler(handler)

    def copy(
        self,
        transform: Callable[['Transformer', _A], _S] | None = None,
        regenerate_instance_id: bool = False
    ) -> Self:
        copied = copy.copy(self)

        func_type = types.MethodType
        if transform is not None:
            setattr(copied, 'transform', func_type(transform, copied))

        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()

        if self.previous is not None:
            # copy_next_previous = 'none' if copy_previous == 'first_previous' else copy_previous
            if type(self.previous) == tuple:
                new_previous: list[Transformer] = [
                    previous_transformer.copy()
                    for previous_transformer in self.previous
                ]
                copied.previous = cast(PreviousTransformer, tuple(new_previous))
            elif isinstance(self.previous, Transformer):
                copied.previous = self.previous.copy()

        copied.children = [child.copy(regenerate_instance_id=True) for child in self.children]

        return copied

    @property
    def graph_nodes(self) -> dict[UUID, 'Transformer']:
        nodes = {self.instance_id: self}

        if self.previous is not None:
            if type(self.previous) == tuple:
                for prev in self.previous:
                    nodes = {
                        **nodes,
                        **prev.graph_nodes
                    }
            elif isinstance(self.previous, Transformer):
                nodes = {
                    **nodes,
                    **self.previous.graph_nodes
                }

        for child in self.children:
            nodes = {
                **nodes,
                **child.graph_nodes
            }

        return nodes

    def _set_previous(self, previous: PreviousTransformer):
        if self.previous is None:
            self.previous = previous
        elif type(self.previous) == tuple:
            for previous_transformer in self.previous:
                previous_transformer._set_previous(previous)
        elif isinstance(self.previous, Transformer):
            self.previous._set_previous(previous)

    def ancestors(self) -> set['Transformer']:
        ancestors: set['Transformer'] = set()
        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
                ancestors = set(previous)
                for previous_transformer in previous:
                    ancestors = ancestors.union(previous_transformer.ancestors())
            elif isinstance(previous, Transformer):
                ancestors = {previous}
                ancestors = ancestors.union(previous.ancestors())

        return ancestors

    def signature(self) -> Signature:
        signature = inspect.signature(self.transform)
        return signature

    @property
    def output_annotation(self) -> str:
        return _format_return_annotation(self.signature().return_annotation)

    @property
    def input_annotation(self) -> str:
        parameters = list(self.signature().parameters.items())
        if len(parameters) == 0:
            return ''
        parameter_type = parameters[0][1]
        return parameter_type.annotation.__name__

    def __get_bound_types(self) -> tuple[str, str]:
        transform_signature = self.signature()
        input_param = str([
            v
            for k, v in transform_signature.parameters.items()
            if k != 'self'
        ][0])

        if input_param is not None:
            input_param = input_param.split(": ")[1]

        output_param = transform_signature.return_annotation

        return input_param, output_param

    def __repr__(self):
        signature = self.signature()
        parameter = list(signature.parameters.items())[0][1].annotation
        return f'{parameter.__name__} -> ({type(self).__name__}) -> {signature.return_annotation}'

    def _add_net_node(self, net: Graph, custom_data: dict[str, Any] = {}):
        node_id = self.node_id
        props = {
            **self.graph_node_props,
            **custom_data,
            "label": self.label
        }
        if node_id not in net.nodes:
            net.add_node(node_id, **props)
        else:
            nx.set_node_attributes(net, {
                node_id: props
            })
        return node_id

    def _add_child_node(
        self,
        child: 'Transformer',
        child_net: DiGraph,
        parent_id: str,
        next_node: 'Transformer'
    ):
        child._dag(child_net, next_node, custom_data={'parent_id': parent_id})

    @property
    def node_id(self) -> str:
        return str(self.instance_id)

    @cached_property
    def visible_previous(self) -> PreviousTransformer:
        previous = self.previous

        if isinstance(previous, Transformer):
            if previous.invisible:
                if previous.previous is None:
                    return previous

                if type(previous.previous) == tuple:
                    return previous.previous

                return previous.visible_previous
            else:
                return previous

        return previous

    def _add_children_subgraph(self, net: DiGraph, next_node: 'Transformer'):
        next_node_id = next_node.node_id
        children_nets = [DiGraph() for _ in self.children]
        visible_previous = self.visible_previous

        for child, child_net in zip(self.children, children_nets):
            self._add_child_node(child, child_net, self.node_id, next_node)
            net.add_nodes_from(child_net.nodes.data())
            net.add_edges_from(child_net.edges.data())

            child_root_node = [n for n in child_net.nodes if child_net.in_degree(n) == 0][0]
            child_final_node = [n for n in child_net.nodes if child_net.out_degree(n) == 0][0]

            if self.invisible:
                if type(visible_previous) == tuple:
                    for prev in visible_previous:
                        net.add_edge(prev.node_id, child_root_node, label=prev.output_annotation)
                elif isinstance(visible_previous, Transformer):
                    net.add_edge(
                        visible_previous.node_id,
                        child_root_node,
                        label=visible_previous.output_annotation
                    )
            else:
                node_id = self._add_net_node(net)
                net.add_edge(node_id, child_root_node)

            if child_final_node != next_node_id:
                net.add_edge(child_final_node, next_node_id, label=next_node.input_annotation)

    def _dag(self, net: DiGraph, next_node: Union['Transformer', None] = None, custom_data: dict[str, Any] = {}):
        in_nodes = [edge[1] for edge in net.in_edges()]

        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
                if self.invisible and next_node is not None:
                    next_node_id = next_node._add_net_node(net)
                    _next_node = next_node
                else:
                    next_node_id = self._add_net_node(net, custom_data)
                    _next_node = self

                for prev in previous:
                    previous_node_id = prev.node_id

                    # TODO: check the impact of the below line to the Mapper transformer
                    if not prev.invisible and len(prev.children) == 0:
                        net.add_edge(previous_node_id, next_node_id, label=prev.output_annotation)

                    if previous_node_id not in in_nodes:
                        prev._dag(net, _next_node, custom_data)
            elif isinstance(previous, Transformer):
                if self.invisible and next_node is not None:
                    next_node_id = next_node._add_net_node(net)
                    _next_node = next_node
                else:
                    next_node_id = self._add_net_node(net, custom_data)
                    _next_node = self

                previous_node_id = previous.node_id

                if len(previous.children) == 0 and not previous.invisible and not self.invisible:
                    previous_node_id = previous._add_net_node(net)
                    net.add_edge(previous_node_id, next_node_id, label=_next_node.output_annotation)

                if previous_node_id not in in_nodes:
                    previous._dag(net, _next_node, custom_data)
        else:
            self._add_net_node(net, custom_data)

        if len(self.children) > 0 and next_node is not None:
            self._add_children_subgraph(net, next_node)

    def graph(self) -> DiGraph:
        net = nx.DiGraph()
        net.graph['splines'] = 'ortho'
        self._dag(net)
        return net

    def export(self, path: str, with_edge_labels: bool = True):
        net = self.graph()
        boxed_nodes = [
            node for node in net.nodes.data()
            if 'parent_id' in node[1] and 'bounding_box' in node[1]
        ]
        if not with_edge_labels:
            for u, v in net.edges:
                net.edges[u, v]['label'] = ''

        agraph = nx.nx_agraph.to_agraph(net)
        subgraphs = groupby(boxed_nodes, key=lambda x: x[1]['parent_id'])
        for parent_id, nodes in subgraphs:
            nodes = list(nodes)
            node_ids = [node[0] for node in nodes]
            if len(nodes) > 0:
                label = nodes[0][1]['box_label']
                agraph.add_subgraph(node_ids, label=label, name=f'cluster_{parent_id}', style="dotted")
        agraph.write(path)

    def __len__(self):
        return 1

    def __call__(self, data: _A) -> _S:
        transform_exception = None

        transformed: _S | None = None
        try:
            transformed = self.transform(data)

            for handler in self._handlers:
                handler.handle(data, transformed)
        except TransformerException as exception:
            transform_exception = TransformerException(
                internal_exception=exception.internal_exception,
                raiser_transformer=self,
                message=f"Error occurred in node with ID {self.id}."
            )
        except Exception as exception:
            if type(exception.__context__) == TransformerException:
                transform_exception = cast(TransformerException, exception.__context__)
            else:
                transform_exception = TransformerException(
                    internal_exception=exception,
                    raiser_transformer=self,
                    message=f"Error occurred in node [{self.__class__.__name__}]."
                )

        if transform_exception is not None:
            # print(traceback.format_tb(internal_exception.previous_exception.__traceback__))
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return transformed

        raise NotImplementedError

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[_S, _U]', 'Transformer[_S, _R1]']
    ) -> 'Transformer[_A, Tuple[_U, _R1]]':
        pass

    @overload
    def __rshift__(
        self, transformers: Tuple[
            'Transformer[_S, _U]', 'Transformer[_S, _R1]', 'Transformer[_S, _R2]']
    ) -> 'Transformer[_A, Tuple[_U, _R1, _R2]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_S, _U]', 'Transformer[_S, _R1]', 'Transformer[_S, _R2]', 'Transformer[_S, _R3]'
        ]
    ) -> 'Transformer[_A, Tuple[_U, _R1, _R2, _R3]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_S, _U]', 'Transformer[_S, _R1]', 'Transformer[_S, _R2]', 'Transformer[_S, _R3]', 'Transformer[_S, _R4]'
        ]
    ) -> 'Transformer[_A, Tuple[_U, _R1, _R2, _R3, _R4]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_S, _U]', 'Transformer[_S, _R1]', 'Transformer[_S, _R2]', 'Transformer[_S, _R3]', 'Transformer[_S, _R4]', 'Transformer[_S, _R5]'
        ]
    ) -> 'Transformer[_A, Tuple[_U, _R1, _R2, _R3, _R4, _R5]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_S, _U]', 'Transformer[_S, _R1]', 'Transformer[_S, _R2]', 'Transformer[_S, _R3]', 'Transformer[_S, _R4]', 'Transformer[_S, _R5]', 'Transformer[_S, _R6]'
        ]
    ) -> 'Transformer[_A, Tuple[_U, _R1, _R2, _R3, _R4, _R5, _R6]]':
        pass

    @overload
    def __rshift__(self, next_transformer: 'Transformer[_S, _U]') -> 'Transformer[_A, _U]':
        pass

    def __rshift__(self, next_step: Any):
        if isinstance(next_step, Transformer):
            return self._merge_serial_connection(self, next_step)

        elif type(next_step) == tuple:
            is_all_transformers = all(
                isinstance(next_transformer, Transformer)
                for next_transformer in next_step
            )
            if is_all_transformers:
                return self._merge_diverging_connection(self, *next_step)

            raise Exception("Unsupported transformer argument")
        else:
            raise Exception("Unsupported transformer argument")


class Begin(Generic[_A], Transformer[_A, _A]):
    def __init__(self):
        super().__init__()
        self.invisible = True

    def __repr__(self):
        return str(self.previous)

    def transform(self, data: _A) -> _A:
        return data
