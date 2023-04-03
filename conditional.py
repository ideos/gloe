from inspect import Signature
from typing import Callable, Generic, TypeVar, Union
from uuid import UUID

from transformer import Transformer

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class _IfThen(Generic[A, B]):
    def __init__(self, condition: Callable[[A], bool], then_transformer: Transformer[A, B]):
        super().__init__()
        self._condition = condition
        self._then_transformer: Transformer[A, B] = then_transformer

    def Else(self, else_transformer: Transformer[A, C]) -> Transformer[A, Union[C, B]]:
        this = self

        class ConditionerTransformer(Transformer[A, Union[B, C]]):
            def transform(self, data: A) -> Union[B, C]:
                if this._condition(data):
                    return this._then_transformer.transform(data)
                else:
                    return else_transformer.transform(data)

            def __signature__(self) -> Signature:
                then_signature: Signature = this._then_transformer.__signature__()
                else_signature: Signature = else_transformer.__signature__()

                new_signature = then_signature.replace(
                    return_annotation=f"""({then_signature.return_annotation} | {else_signature.return_annotation})"""
                )
                return new_signature

            def __len__(self):
                return len(this._then_transformer) + len(else_transformer)

            def graph_nodes(self) -> dict[UUID, 'Transformer']:
                transformer1_nodes = this._then_transformer.graph_nodes()
                transformer2_nodes = else_transformer.graph_nodes()
                return {**transformer1_nodes, **transformer2_nodes}

        new_transformer = ConditionerTransformer()
        return new_transformer


class If(Generic[A]):
    def __init__(self, condition: Callable[[A], bool]):
        super().__init__()
        self._condition = condition

    def Then(self, next_transformer: Transformer[A, B]) -> _IfThen[A, B]:
        return _IfThen(self._condition, next_transformer)


def conditioner(func: Callable[[A], bool]) -> If[A]:
    return If(func)
