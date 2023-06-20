from inspect import Signature
from typing import Callable, Generic, Optional, TypeVar, Union

from typing_extensions import Self

from .transformers import Transformer
from .utils import forget

In = TypeVar("In")
ThenOut = TypeVar("ThenOut")
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")


class ConditionerTransformer(Generic[In, ThenOut, ElseOut], Transformer[In, Union[ThenOut, ElseOut]]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        then_transformer: Transformer[In, ThenOut],
        else_transformer: Transformer[In, ElseOut]
    ):
        super().__init__()
        self.condition = condition
        self.then_transformer = then_transformer
        self.else_transformer = else_transformer
        self.graph_node_props = {
            "shape": "diamond",
            "style": "filled",
            "port": "n"
        }
        self.children = [then_transformer, else_transformer]

    def transform(self, data: In) -> Union[ThenOut, ElseOut]:
        if self.condition(data):
            return self.then_transformer.transform(data)
        else:
            return self.else_transformer.transform(data)

    def signature(self) -> Signature:
        then_signature: Signature = self.then_transformer.signature()
        else_signature: Signature = self.else_transformer.signature()

        new_signature = then_signature.replace(
            return_annotation=Union[
                then_signature.return_annotation, else_signature.return_annotation
            ]
        )
        return new_signature

    def copy(
        self,
        transform: Callable[['Transformer', In], Union[ThenOut, ElseOut]] | None = None,
        regenerate_instance_id: bool = False
    ) -> Self:
        copied: Self = super().copy(transform, regenerate_instance_id)
        copied.then_transformer = copied.children[0]
        copied.else_transformer = copied.children[1]
        return copied

    def __len__(self):
        return len(self.then_transformer) + len(self.else_transformer)


class _IfThen(Generic[In, ThenOut]):
    def __init__(self, condition: Callable[[In], bool], then_transformer: Transformer[In, ThenOut]):
        super().__init__()
        self._condition = condition
        self._then_transformer: Transformer[In, ThenOut] = then_transformer

    def Else(self, else_transformer: Transformer[In, ElseOut]) -> Transformer[In, Union[ElseOut, ThenOut]]:

        new_transformer: ConditionerTransformer[In, ThenOut, ElseOut] = ConditionerTransformer(
            self._condition, self._then_transformer, else_transformer
        )
        new_transformer.__class__.__name__ = self.__class__.__name__
        return new_transformer

    def ElseIf(self, condition: Callable[[In], bool]) -> '_ElseIf[In, ThenOut]':

        else_if: '_ElseIf[In, ThenOut]' = _ElseIf(condition, self)
        else_if.__class__.__name__ = self.__class__.__name__
        return else_if

    def ElseNone(self) -> Transformer[In, Optional[ThenOut]]:

        new_transformer: ConditionerTransformer[In, ThenOut, None] = ConditionerTransformer(
            self._condition, self._then_transformer, forget
        )
        new_transformer.__class__.__name__ = self.__class__.__name__
        return new_transformer


class _ElseIf(Generic[In, ThenOut]):
    def __init__(self, condition: Callable[[In], bool], previous_if: _IfThen[In, ThenOut]):
        super().__init__()
        self._condition = condition
        self._previous_if: _IfThen[In, ThenOut] = previous_if

    def Then(
        self,
        next_transformer: Transformer[In, ElseIfOut]
    ) -> _IfThen[In, Union[ThenOut, ElseIfOut]]:
        if_then = _IfThen(self._condition, next_transformer)
        if_then.__class__.__name__ = self.__class__.__name__
        return if_then


class If(Generic[In]):
    def __init__(self, condition: Callable[[In], bool], name: str | None = None):
        super().__init__()
        self._condition = condition

        if name is not None:
            self.__class__.__name__ = name

    def Then(self, next_transformer: Transformer[In, ThenOut]) -> _IfThen[In, ThenOut]:
        if_then = _IfThen(self._condition, next_transformer)
        if_then.__class__.__name__ = self.__class__.__name__
        return if_then


def conditioner(func: Callable[[In], bool]) -> If[In]:
    condition = If(func)
    condition.__class__.__name__ = func.__name__
    return condition
