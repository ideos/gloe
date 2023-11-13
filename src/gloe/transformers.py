import copy
import traceback
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
    Union, cast, overload, Iterable, get_args, get_origin
from uuid import UUID
from itertools import groupby

from ._utils import _format_return_annotation, _match_types, _specify_types
from .exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")

_Out2 = TypeVar("_Out2")
_Out3 = TypeVar("_Out3")
_Out4 = TypeVar("_Out4")
_Out5 = TypeVar("_Out5")
_Out6 = TypeVar("_Out6")
_Out7 = TypeVar("_Out7")


PreviousTransformer: TypeAlias = Union[
    None,
    'Transformer',
    tuple['Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer']
]


class TransformerException(Exception):

    def __init__(
        self,
        internal_exception: Union['TransformerException', Exception],
        raiser_transformer: 'Transformer',
        message: str | None = None
    ):
        self._internal_exception = internal_exception
        self.raiser_transformer = raiser_transformer
        self._traceback = internal_exception.__traceback__
        internal_exception.__cause__ = self
        super().__init__(message)

    @property
    def internal_exception(self):
        return self._internal_exception.with_traceback(self._traceback)


class Transformer(Generic[_In, _Out], ABC):
    """
    A Transformer is generic block with the responsibility to take an input of type `T`
    and transform it to an output of type `S`.


    Typical usage example:

    class Stringifier(Transformer[dict, str]):
        ...

    """

    @staticmethod
    def _merge_serial_connection(
        transformer1: 'Transformer[_In, _Out]', _transformer2: 'Transformer[_Out, _NextOut]'
    ) -> 'Transformer[_In, _NextOut]':
        if transformer1.previous is None:
            transformer1 = transformer1.copy(regenerate_instance_id=True)

        transformer2 = _transformer2.copy(regenerate_instance_id=True)
        transformer2._set_previous(transformer1)

        signature1: Signature = transformer1.signature()
        signature2: Signature = transformer2.signature()

        input_generic_vars = _match_types(transformer2.input_type, signature1.return_annotation)
        output_generic_vars = _match_types(signature1.return_annotation, transformer2.input_type)
        generic_vars = {**input_generic_vars, **output_generic_vars}

        def transformer1_signature(_) -> Signature:
            return signature1.replace(
                return_annotation=_specify_types(signature1.return_annotation, generic_vars)
            )

        setattr(transformer1, 'signature', types.MethodType(transformer1_signature, transformer1))

        class NewTransformer(Transformer[_In, _NextOut]):
            def transform(self, data: _In) -> _NextOut:
                transformer2_call = transformer2.__call__
                transformer1_call = transformer1.__call__
                transformed = transformer2_call(transformer1_call(data))
                return transformed

            def signature(self) -> Signature:
                first_param = list(signature2.parameters.values())[0]
                new_parameter = first_param.replace(annotation=_specify_types(transformer2.input_type, generic_vars))
                new_signature = signature2 \
                    .replace(
                        parameters=[new_parameter],
                        return_annotation=_specify_types(signature2.return_annotation, generic_vars)
                    )
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
        incident_transformer: 'Transformer[_In, _Out]',
        *receiving_transformers: 'Transformer[_Out, Any]'
    ) -> 'Transformer[_In, tuple]':
        if incident_transformer.previous is None:
            incident_transformer = incident_transformer.copy(regenerate_instance_id=True)

        receiving_transformers = tuple([
            receiving_transformer.copy(regenerate_instance_id=True)
            for receiving_transformer in receiving_transformers
        ])

        for receiving_transformer in receiving_transformers:
            receiving_transformer._set_previous(incident_transformer)

        incident_signature: Signature = incident_transformer.signature()
        receiving_signatures: list[Signature] = []

        for receiving_transformer in receiving_transformers:
            generic_vars = _match_types(receiving_transformer.input_type, incident_signature.return_annotation)

            receiving_signature = receiving_transformer.signature()
            return_annotation = receiving_signature.return_annotation

            new_return_annotation = _specify_types(return_annotation, generic_vars)

            new_signature = receiving_signature.replace(return_annotation=new_return_annotation)
            receiving_signatures.append(new_signature)

            def _signature(_) -> Signature:
                return new_signature

            if receiving_transformer.previous == incident_transformer:
                setattr(receiving_transformer, 'signature', types.MethodType(_signature, receiving_transformer))

        def split_result(data: _In) -> Tuple[Any, ...]:
            intermediate_result = incident_transformer(data)
            return tuple([
                receiving_transformer(intermediate_result)
                for receiving_transformer in receiving_transformers
            ])

        class NewTransformer(Transformer[_In, Tuple[Any, ...]]):

            def transform(self, data: _In) -> Tuple[Any, ...]:
                return split_result(data)

            def signature(self) -> Signature:
                receiving_signature_returns = [r.return_annotation for r in receiving_signatures]
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
        self.previous: PreviousTransformer = None
        self.children: list[Transformer] = []
        self.invisible = False
        self.id = uuid.uuid4()
        self.instance_id = uuid.uuid4()
        self.label = self.__class__.__name__
        self.graph_node_props: dict[str, Any] = {
            "shape": "box"
        }
        self.events = []
        self.__class__.__annotations__ = self.transform.__annotations__

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Transformer):
            return self.id == other.id
        return NotImplemented

    @abstractmethod
    def transform(self, data: _In) -> _Out:
        """Main method to be implemented and responsible to perform the transformer logic"""

    def copy(
        self,
        transform: Callable[['Transformer', _In], _Out] | None = None,
        regenerate_instance_id: bool = False
    ) -> 'Transformer[_In, _Out]':
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

    def signature(self) -> Signature:
        orig_bases = getattr(self, '__orig_bases__', [])
        transformer_args = [
            get_args(base)
            for base in orig_bases
            if get_origin(base) == Transformer
        ]
        generic_args = [
            get_args(base)
            for base in orig_bases
            if get_origin(base) == Generic
        ]

        orig_class = getattr(self, '__orig_class__', None)

        specific_args = {}
        if len(transformer_args) == 1 and len(generic_args) == 1 and orig_class is not None:
            generic_arg = generic_args[0]
            transformer_arg = transformer_args[0]
            specific_args = {
                generic: specific
                for generic, specific in zip(generic_arg, get_args(orig_class))
                if generic in transformer_arg
            }

        signature = inspect.signature(self.transform)
        new_return_annotation = specific_args.get(signature.return_annotation, signature.return_annotation)
        return signature.replace(return_annotation=new_return_annotation)

    @property
    def output_type(self) -> Any:
        signature = self.signature()
        return signature.return_annotation

    @property
    def output_annotation(self) -> str:
        output_type = self.output_type

        return_type = _format_return_annotation(
            output_type, None, None
        )
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

    def __repr__(self):
        return f'{self.input_annotation} -> ({type(self).__name__}) -> {self.output_annotation}'

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

    def _dag(
        self,
        net: DiGraph,
        next_node: Union['Transformer', None] = None,
        custom_data: dict[str, Any] = {}
    ):
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

                if len(previous.children) == 0 and (not previous.invisible or previous.previous is None):
                    previous_node_id = previous._add_net_node(net)
                    net.add_edge(previous_node_id, next_node_id, label=previous.output_annotation)

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

    # pragma: not covered
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
        subgraphs: Iterable[Tuple] = groupby(boxed_nodes, key=lambda x: x[1]['parent_id'])
        for parent_id, nodes in subgraphs:
            nodes = list(nodes)
            node_ids = [node[0] for node in nodes]
            if len(nodes) > 0:
                label = nodes[0][1]['box_label']
                agraph.add_subgraph(node_ids, label=label, name=f'cluster_{parent_id}', style="dotted")
        agraph.write(path)

    def __len__(self):
        return 1

    def __call__(self, data: _In) -> _Out:
        transform_exception = None

        transformed: _Out | None = None
        try:
            transformed = self.transform(data)
        except Exception as exception:
            if type(exception.__cause__) == TransformerException:
                transform_exception = exception.__cause__
            else:
                tb = traceback.extract_tb(exception.__traceback__)

                # TODO: Make this filter condition stronger
                transformer_frames = [
                    frame for frame in tb
                    if frame.name == self.__class__.__name__ or frame.name == 'transform'
                ]

                if len(transformer_frames) == 1:
                    transformer_frame = transformer_frames[0]
                    exception_message = (
                        f'\n  '
                        f'File "{transformer_frame.filename}", line {transformer_frame.lineno}, '
                        f'in transformer "{self.__class__.__name__}"\n  '
                        f'  >> {transformer_frame.line}'
                    )
                else:
                    exception_message = f'An error occurred in transformer "{self.__class__.__name__}"'

                transform_exception = TransformerException(
                    internal_exception=exception,
                    raiser_transformer=self,
                    message=exception_message
                )

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return cast(_Out, transformed)

        raise NotImplementedError

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[_Out, _NextOut]', 'Transformer[_Out, _Out2]']
    ) -> 'Transformer[_In, Tuple[_NextOut, _Out2]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple['Transformer[_Out, _NextOut]', 'Transformer[_Out, _Out2]', 'Transformer[_Out, _Out3]']
    ) -> 'Transformer[_In, Tuple[_NextOut, _Out2, _Out3]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_Out, _NextOut]', 'Transformer[_Out, _Out2]', 'Transformer[_Out, _Out3]',
            'Transformer[_Out, _Out4]'
        ]
    ) -> 'Transformer[_In, Tuple[_NextOut, _Out2, _Out3, _Out4]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_Out, _NextOut]', 'Transformer[_Out, _Out2]', 'Transformer[_Out, _Out3]',
            'Transformer[_Out, _Out4]', 'Transformer[_Out, _Out5]'
        ]
    ) -> 'Transformer[_In, Tuple[_NextOut, _Out2, _Out3, _Out4, _Out5]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_Out, _NextOut]', 'Transformer[_Out, _Out2]', 'Transformer[_Out, _Out3]',
            'Transformer[_Out, _Out4]', 'Transformer[_Out, _Out5]', 'Transformer[_Out, _Out6]'
        ]
    ) -> 'Transformer[_In, Tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[_Out, _NextOut]', 'Transformer[_Out, _Out2]', 'Transformer[_Out, _Out3]',
            'Transformer[_Out, _Out4]', 'Transformer[_Out, _Out5]', 'Transformer[_Out, _Out6]',
            'Transformer[_Out, _Out7]'
        ]
    ) -> 'Transformer[_In, Tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6, _Out7]]':
        pass

    @overload
    def __rshift__(self, next_transformer: 'Transformer[_Out, _NextOut]') -> 'Transformer[_In, _NextOut]':
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

            unsupported_elem = [
                elem
                for elem in next_step
                if not isinstance(elem, Transformer)
            ]
            raise UnsupportedTransformerArgException(unsupported_elem[0])
        else:
            raise UnsupportedTransformerArgException(next_step)


