from dataclasses import dataclass
from inspect import Signature
from types import GenericAlias, UnionType
from typing import Callable, Generic, Optional, TypeVar, Union

from gloe.transformers import Transformer
from gloe.utils import forget


In = TypeVar("In")
ThenOut = TypeVar("ThenOut")
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


@dataclass
class _Implication(Generic[In, ThenOut]):
    condition: Callable[[In], bool]
    then_transformer: Transformer[In, ThenOut]


class ConditionerTransformer(
    Generic[In, ThenOut, ElseOut], Transformer[In, Union[ThenOut, ElseOut]]
):
    def __init__(
        self,
        implications: list[_Implication[In, ThenOut]],
        else_transformer: Transformer[In, ElseOut],
    ):
        super().__init__()
        self.implications = implications
        self.else_transformer = else_transformer
        self._graph_node_props = {"shape": "diamond", "style": "filled", "port": "n"}
        self._children = [
            *[impl.then_transformer for impl in implications],
            else_transformer,
        ]

    def transform(self, data: In) -> Union[ThenOut, ElseOut]:
        for implication in self.implications:
            if implication.condition(data):
                return implication.then_transformer.transform(data)

        return self.else_transformer.transform(data)

    def signature(self) -> Signature:
        else_signature: Signature = self.else_transformer.signature()
        return_signature: list[Signature] = [
            impl.then_transformer.signature().return_annotation
            for impl in self.implications
        ] + [else_signature.return_annotation]
        new_signature = else_signature.replace(
            return_annotation=GenericAlias(UnionType, tuple(return_signature))
        )
        return new_signature

    def copy(
        self,
        transform: Callable[["Transformer", In], Union[ThenOut, ElseOut]] | None = None,
        regenerate_instance_id: bool = False,
    ) -> "ConditionerTransformer[In, ThenOut, ElseOut]":
        copied: ConditionerTransformer[In, ThenOut, ElseOut] = super().copy(
            transform, regenerate_instance_id
        )
        copied.implications = [
            _Implication(
                impl.condition, impl.then_transformer.copy(regenerate_instance_id=True)
            )
            for impl in copied.implications
        ]
        copied.else_transformer = self.else_transformer.copy(regenerate_instance_id=True)
        copied._children = [
            *[impl.then_transformer for impl in copied.implications],
            copied.else_transformer,
        ]
        return copied

    def __len__(self):
        then_transformers_len = [len(impl.then_transformer) for impl in self.implications]
        return sum(then_transformers_len) + len(self.else_transformer)


class _IfThen(Generic[In, ThenOut, PrevThenOut]):
    def __init__(
        self,
        implication: _Implication[In, ThenOut],
        name: str,
        prev_implications: list[_Implication[In, PrevThenOut]] = [],
    ):
        super().__init__()
        self._implication = implication
        self._prev_implications = prev_implications
        self._name = name
        self._implications: list[
            _Implication[In, Union[ThenOut, PrevThenOut]]
        ] = self._prev_implications + [self._implication]

    def Else(
        self, else_transformer: Transformer[In, ElseOut]
    ) -> Transformer[In, Union[ThenOut, PrevThenOut, ElseOut]]:
        new_transformer: ConditionerTransformer[
            In, Union[ThenOut, PrevThenOut], ElseOut
        ] = ConditionerTransformer(self._implications, else_transformer)

        new_transformer.__class__.__name__ = self._name
        new_transformer._label = self._name

        return new_transformer

    def ElseIf(
        self, condition: Callable[[In], bool]
    ) -> "_ElseIf[In, Union[ThenOut, PrevThenOut]]":
        else_if: "_ElseIf[In, Union[ThenOut, PrevThenOut]]" = _ElseIf(
            condition, self._implications, self._name
        )
        else_if.__class__.__name__ = self.__class__.__name__
        return else_if

    def ElseNone(
        self,
    ) -> Transformer[In, Optional[Union[ThenOut, PrevThenOut]]]:
        new_transformer: ConditionerTransformer[
            In, Union[ThenOut, PrevThenOut], None
        ] = ConditionerTransformer(self._implications, forget)
        new_transformer.__class__.__name__ = self.__class__.__name__
        return new_transformer


class _ElseIf(Generic[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: list[_Implication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__()
        self._condition = condition
        self._prev_implications: list[_Implication[In, PrevThenOut]] = prev_implications
        self._name = name

    def Then(
        self, next_transformer: Transformer[In, ElseIfOut]
    ) -> _IfThen[In, ElseIfOut, PrevThenOut]:
        implication = _Implication[In, ElseIfOut](self._condition, next_transformer)
        if_then = _IfThen[In, ElseIfOut, PrevThenOut](
            implication, self._name, self._prev_implications
        )
        return if_then


class If(Generic[In]):
    """
    It is used to start a condition chaining

    Example:
        The below example send a different email for admin and non admin users::

            send_email = (
                If(lambda user: "admin" in user.roles)
                    .Then(fetch_admin_data >> send_admin_email)
                .Else(send_member_email)
            )

    Args:
        condition: callable returning a boolean.
        name: optional argument that adds a label to condition node during plotting.
    """

    def __init__(self, condition: Callable[[In], bool], name: str | None = None):
        super().__init__()
        self._condition = condition
        self._name: str = name or condition.__name__

    def Then(
        self, next_transformer: Transformer[In, ThenOut]
    ) -> _IfThen[In, ThenOut, ThenOut]:
        """ """
        implication = _Implication[In, ThenOut](self._condition, next_transformer)
        if_then = _IfThen[In, ThenOut, ThenOut](implication, name=self._name)
        return if_then


def condition(func: Callable[[In], bool]) -> If[In]:
    """
    The condition decorator is responsible to build an instance of :code:`If[T]`
    class given a :code:`Callable[[T], bool]`.

    When instantiating the :code:`If` class, the parameter :code:`name` will be the name
    of the callable.

    See Also:
        For additional information about conditions and examples of its usage, consult
        :ref:`conditional-flows`.

    Example:
        The below example send a different email for admin and non admin users::

            @condition
            def is_admin(user: User) -> bool:
                return "admin" in user.roles

            send_email = (
                is_admin.Then(fetch_admin_data >> send_admin_email)
                .Else(send_member_email)
            )

    Args:
        func: A callable that check somenting about the incoming data and returns a
            boolean.
    """
    condition = If(func, func.__name__)
    return condition
