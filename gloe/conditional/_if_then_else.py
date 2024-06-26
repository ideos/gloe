from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.exceptions import UnsupportedTransformerArgException
from gloe.conditional._async_conditioner import AsyncConditioner
from gloe.conditional._conditioner import Conditioner
from gloe.conditional._implication import (
    _Implication,
    _AsyncImplication,
    _BaseImplication,
)

from typing import (
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
    overload,
    Sequence,
)

from gloe.transformers import Transformer
from gloe.utils import forget


In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


class _BaseIfThen(Generic[In, ThenOut, PrevThenOut]):
    def __init__(
        self,
        implication: _BaseImplication[In, ThenOut],
        name: str,
        prev_implications: Sequence[_BaseImplication[In, PrevThenOut]] = [],
    ):
        super().__init__()
        self._implication = implication
        self._prev_implications = prev_implications
        self._name = name
        self._implications: Sequence[
            _BaseImplication[In, Union[ThenOut, PrevThenOut]]
        ] = list(self._prev_implications) + [self._implication]


class _IfThen(_BaseIfThen[In, ThenOut, PrevThenOut]):
    def __init__(
        self,
        implication: _Implication[In, ThenOut],
        name: str,
        prev_implications: Sequence[_Implication[In, PrevThenOut]] = [],
    ):
        super().__init__(implication, name, prev_implications)
        self._implication = implication
        self._prev_implications = prev_implications
        self._implications: Sequence[_Implication[In, Union[ThenOut, PrevThenOut]]] = (
            list(self._prev_implications) + [self._implication]
        )

    @overload
    def Else(
        self, else_transformer: Transformer[In, ElseOut]
    ) -> Transformer[In, Union[ThenOut, PrevThenOut, ElseOut]]:
        pass

    @overload
    def Else(
        self, else_transformer: AsyncTransformer[In, ElseOut]
    ) -> AsyncTransformer[In, Union[ThenOut, PrevThenOut, ElseOut]]:
        pass

    def Else(self, else_transformer):
        if isinstance(else_transformer, AsyncTransformer):
            new_atransformer: AsyncConditioner = AsyncConditioner(
                self._implications, else_transformer
            )
            new_atransformer.__class__.__name__ = self._name
            new_atransformer._label = self._name

            return new_atransformer

        elif isinstance(else_transformer, Transformer):
            new_transformer: Conditioner = Conditioner(
                self._implications, else_transformer
            )

            new_transformer.__class__.__name__ = self._name
            new_transformer._label = self._name

            return new_transformer

        raise UnsupportedTransformerArgException(else_transformer)

    def ElseNone(
        self,
    ) -> Transformer[In, Optional[Union[ThenOut, PrevThenOut]]]:
        new_transformer: Conditioner[In, Union[ThenOut, PrevThenOut], None] = (
            Conditioner(self._implications, forget)
        )
        new_transformer.__class__.__name__ = self.__class__.__name__
        return new_transformer

    def ElseIf(
        self, condition: Callable[[In], bool]
    ) -> "_ElseIf[In, Union[ThenOut, PrevThenOut]]":
        else_if: "_ElseIf[In, Union[ThenOut, PrevThenOut]]" = _ElseIf(
            condition, self._implications, self._name
        )
        else_if.__class__.__name__ = self.__class__.__name__
        return else_if


class _AsyncIfThen(_BaseIfThen[In, ThenOut, PrevThenOut]):
    def Else(
        self, else_transformer: BaseTransformer[In, ElseOut]
    ) -> AsyncTransformer[In, Union[ThenOut, PrevThenOut, ElseOut]]:
        new_transformer: AsyncConditioner[In, Union[ThenOut, PrevThenOut], ElseOut] = (
            AsyncConditioner(self._implications, else_transformer)
        )

        new_transformer.__class__.__name__ = self._name
        new_transformer._label = self._name

        return new_transformer

    def ElseNone(
        self,
    ) -> AsyncTransformer[In, Optional[Union[ThenOut, PrevThenOut]]]:
        new_transformer: AsyncConditioner[In, Union[ThenOut, PrevThenOut], None] = (
            AsyncConditioner(self._implications, forget)
        )
        new_transformer.__class__.__name__ = self.__class__.__name__
        return new_transformer

    def ElseIf(
        self, condition: Callable[[In], bool]
    ) -> "_AsyncElseIf[In, Union[ThenOut, PrevThenOut]]":
        else_if: "_AsyncElseIf[In, Union[ThenOut, PrevThenOut]]" = _AsyncElseIf(
            condition, self._implications, self._name
        )
        else_if.__class__.__name__ = self.__class__.__name__
        return else_if


class _BaseElseIf(Generic[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: Sequence[_BaseImplication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__()
        self._condition = condition
        self._prev_implications: Sequence[_BaseImplication[In, PrevThenOut]] = (
            prev_implications
        )
        self._name = name


class _ElseIf(_BaseElseIf[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: Sequence[_Implication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__(condition, prev_implications, name)
        self._prev_implications: Sequence[_Implication[In, PrevThenOut]] = (
            prev_implications
        )

    @overload
    def Then(
        self, next_transformer: AsyncTransformer[In, ElseIfOut]
    ) -> _AsyncIfThen[In, ElseIfOut, PrevThenOut]:
        pass

    @overload
    def Then(
        self, next_transformer: Transformer[In, ElseIfOut]
    ) -> _IfThen[In, ElseIfOut, PrevThenOut]:
        pass

    def Then(self, next_transformer):
        if isinstance(next_transformer, AsyncTransformer):
            async_implication = _AsyncImplication(self._condition, next_transformer)
            async_if_then = _AsyncIfThen(
                async_implication, self._name, self._prev_implications
            )
            return async_if_then

        if isinstance(next_transformer, Transformer):
            implication = _Implication(self._condition, next_transformer)
            if_then = _IfThen(implication, self._name, self._prev_implications)
            return if_then

        raise UnsupportedTransformerArgException(next_transformer)


class _AsyncElseIf(_BaseElseIf[In, PrevThenOut]):
    def Then(
        self, next_transformer: BaseTransformer[In, ElseIfOut]
    ) -> _AsyncIfThen[In, ElseIfOut, PrevThenOut]:
        async_implication = _AsyncImplication(self._condition, next_transformer)
        async_if_then = _AsyncIfThen(
            async_implication, self._name, self._prev_implications
        )
        return async_if_then
