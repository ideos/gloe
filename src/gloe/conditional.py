from inspect import Signature
from typing import Any, Callable, Generic, TypeVar, Union
from uuid import UUID

import networkx as nx
from networkx import DiGraph
from typing_extensions import Self

from .transformer import Transformer

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class ConditionerTransformer(Generic[A, B, C], Transformer[A, Union[B, C]]):
    def __init__(
        self,
        condition: Callable[[A], bool],
        then_transformer: Transformer[A, B],
        else_transformer: Transformer[A, C]
    ):
        super().__init__()
        self.condition = condition
        self.then_transformer = then_transformer
        self.else_transformer = else_transformer
        self.children = [then_transformer, else_transformer]

    def transform(self, data: A) -> Union[B, C]:
        if self.condition(data):
            return self.then_transformer.transform(data)
        else:
            return self.else_transformer.transform(data)

    @property
    def signature(self) -> Signature:
        then_signature: Signature = self.then_transformer.signature
        else_signature: Signature = self.else_transformer.signature

        new_signature = then_signature.replace(
            return_annotation=f"""({then_signature.return_annotation} | {else_signature.return_annotation})"""
        )
        return new_signature

    def copy(
        self,
        transform: Callable[['Transformer', A], Union[B, C]] | None = None,
        copy_previous: str = 'first_previous'
    ) -> Self:
        copied: Self = super().copy(transform, copy_previous)
        copied.then_transformer = self.then_transformer.copy()
        copied.else_transformer = self.else_transformer.copy()
        return copied

    def __len__(self):
        return len(self.then_transformer) + len(self.else_transformer)

    def graph_nodes(self) -> dict[UUID, 'Transformer']:
        transformer1_nodes = self.then_transformer.graph_nodes()
        transformer2_nodes = self.else_transformer.graph_nodes()
        return {**transformer1_nodes, **transformer2_nodes}

    def _add_net_node(self, net: DiGraph, custom_data: dict[str, Any] = {}):
        node_id = str(self.instance_id)
        if node_id not in net.nodes:
            net.add_node(
                node_id,
                shape='diamond',
                style='filled',
                label=self.__class__.__name__,
                **custom_data
            )
        else:
            nx.set_node_attributes(
                net, {
                    node_id: {
                        "shape": "diamond",
                        "diamond": "filled",
                        "label": self.__class__.__name__,
                        **custom_data
                    }
                }
            )
        return node_id


class _IfThen(Generic[A, B]):
    def __init__(self, condition: Callable[[A], bool], then_transformer: Transformer[A, B]):
        super().__init__()
        self._condition = condition
        self._then_transformer: Transformer[A, B] = then_transformer

    def Else(self, else_transformer: Transformer[A, C]) -> Transformer[A, Union[C, B]]:

        new_transformer: ConditionerTransformer[A, B, C] = ConditionerTransformer(
            self._condition, self._then_transformer, else_transformer
        )
        new_transformer.__class__.__name__ = self.__class__.__name__
        # self._then_transformer._set_previous(new_transformer)
        # else_transformer._set_previous(new_transformer)
        return new_transformer


class If(Generic[A]):
    def __init__(self, condition: Callable[[A], bool]):
        super().__init__()
        self._condition = condition

    def Then(self, next_transformer: Transformer[A, B]) -> _IfThen[A, B]:
        if_then = _IfThen(self._condition, next_transformer)
        if_then.__class__.__name__ = self.__class__.__name__
        return if_then


def conditioner(func: Callable[[A], bool]) -> If[A]:
    condition = If(func)
    condition.__class__.__name__ = func.__name__
    return condition
