from collections.abc import Awaitable as AwaitableABC
from inspect import isawaitable
from typing import (
    Awaitable,
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
    overload,
    Sequence,
    get_origin,
    cast,
    Any,
)

from gloe.conditional._conditioner import Conditioner, AsyncConditioner
from gloe.conditional._implication import _Implication, _AsyncImplication
from gloe.exceptions import UnsupportedTransformerArgException
from gloe.transformers import Transformer
from gloe.utils import forget

In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


def _returns_awaitable(transformer: Transformer) -> bool:
    origin = get_origin(transformer.output_type)
    return origin in (Awaitable, AwaitableABC)


def _as_async_transformer(
    transformer: Transformer[In, ThenOut],
) -> Transformer[In, Awaitable[ThenOut]]:
    if _returns_awaitable(transformer):
        return cast(Transformer[In, Awaitable[ThenOut]], transformer)

    def transform(_: Any, data: In) -> Awaitable[ThenOut]:
        result = transformer(data)
        if isawaitable(result):
            return cast(Awaitable[ThenOut], result)

        async def _wrap_sync() -> ThenOut:
            return cast(ThenOut, result)

        return _wrap_sync()

    wrapped = transformer.copy(cast(Callable[[Any, Any], Any], transform))
    return cast(Transformer[In, Awaitable[ThenOut]], wrapped)


def _to_async_implications(
    implications: Sequence[_Implication[In, ThenOut]],
) -> Sequence[_AsyncImplication[In, ThenOut]]:
    return [
        _AsyncImplication(imp.condition, _as_async_transformer(imp.then_transformer))
        for imp in implications
    ]


class _BaseIfThen(Generic[In, ThenOut, PrevThenOut]):
    def __init__(
        self,
        implication: _Implication[In, ThenOut],
        name: str,
        prev_implications: Sequence[_Implication[In, PrevThenOut]] = [],
    ):
        super().__init__()
        self._implication = implication
        self._prev_implications = prev_implications
        self._name = name
        self._implications: Sequence[
            _Implication[In, Union[ThenOut, PrevThenOut]]
        ] = list(self._prev_implications) + [self._implication]


class _BaseIfThenAsync(Generic[In, ThenOut, PrevThenOut]):
    def __init__(
        self,
        implication: _AsyncImplication[In, ThenOut],
        name: str,
        prev_implications: Sequence[_AsyncImplication[In, PrevThenOut]] = [],
    ):
        super().__init__()
        self._implication = implication
        self._prev_implications = prev_implications
        self._name = name
        self._implications: Sequence[
            _AsyncImplication[In, Union[ThenOut, PrevThenOut]]
        ] = list(self._prev_implications) + [self._implication]


class _IfThenSync(_BaseIfThen[In, ThenOut, PrevThenOut]):
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
        self, else_transformer: Transformer[In, Awaitable[ElseOut]]
    ) -> Transformer[In, Awaitable[Union[ThenOut, PrevThenOut, ElseOut]]]:
        pass

    @overload
    def Else(
        self, else_transformer: Transformer[In, ElseOut]
    ) -> Transformer[In, Union[ThenOut, PrevThenOut, ElseOut]]:
        pass

    def Else(self, else_transformer: Transformer[In, ElseOut]):
        if not isinstance(else_transformer, Transformer):
            raise UnsupportedTransformerArgException(else_transformer)

        if _returns_awaitable(else_transformer):
            async_implications = _to_async_implications(self._implications)
            async_else = _as_async_transformer(else_transformer)
            new_transformer: Transformer = AsyncConditioner(
                async_implications, async_else
            )
        else:
            new_transformer = Conditioner(self._implications, else_transformer)

        new_transformer.__class__.__name__ = self._name
        new_transformer._label = self._name
        return new_transformer

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
    ) -> "_ElseIfSync[In, Union[ThenOut, PrevThenOut]]":
        else_if: "_ElseIfSync[In, Union[ThenOut, PrevThenOut]]" = _ElseIfSync(
            condition, self._implications, self._name
        )
        else_if.__class__.__name__ = self.__class__.__name__
        return else_if


class _IfThenAsync(_BaseIfThenAsync[In, ThenOut, PrevThenOut]):
    def __init__(
        self,
        implication: _AsyncImplication[In, ThenOut],
        name: str,
        prev_implications: Sequence[_AsyncImplication[In, PrevThenOut]] = [],
    ):
        super().__init__(implication, name, prev_implications)
        self._implication = implication
        self._prev_implications = prev_implications
        self._implications: Sequence[
            _AsyncImplication[In, Union[ThenOut, PrevThenOut]]
        ] = list(self._prev_implications) + [self._implication]

    @overload
    def Else(
        self, else_transformer: Transformer[In, Awaitable[ElseOut]]
    ) -> Transformer[In, Awaitable[Union[ThenOut, PrevThenOut, ElseOut]]]:
        pass

    @overload
    def Else(
        self, else_transformer: Transformer[In, ElseOut]
    ) -> Transformer[In, Awaitable[Union[ThenOut, PrevThenOut, ElseOut]]]:
        pass

    def Else(self, else_transformer: Transformer[In, ElseOut]):
        if not isinstance(else_transformer, Transformer):
            raise UnsupportedTransformerArgException(else_transformer)

        async_else = _as_async_transformer(else_transformer)
        new_transformer: Transformer = AsyncConditioner(self._implications, async_else)
        new_transformer.__class__.__name__ = self._name
        new_transformer._label = self._name
        return new_transformer

    def ElseNone(
        self,
    ) -> Transformer[In, Awaitable[Optional[Union[ThenOut, PrevThenOut]]]]:
        async_forget = _as_async_transformer(forget)
        new_transformer: AsyncConditioner[In, Union[ThenOut, PrevThenOut], None] = (
            AsyncConditioner(self._implications, async_forget)
        )
        new_transformer.__class__.__name__ = self.__class__.__name__
        return new_transformer

    def ElseIf(
        self, condition: Callable[[In], bool]
    ) -> "_ElseIfAsync[In, Union[ThenOut, PrevThenOut]]":
        else_if: "_ElseIfAsync[In, Union[ThenOut, PrevThenOut]]" = _ElseIfAsync(
            condition, self._implications, self._name
        )
        else_if.__class__.__name__ = self.__class__.__name__
        return else_if


class _BaseElseIf(Generic[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: Sequence[_Implication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__()
        self._condition = condition
        self._prev_implications: Sequence[_Implication[In, PrevThenOut]] = (
            prev_implications
        )
        self._name = name


class _BaseElseIfAsync(Generic[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: Sequence[_AsyncImplication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__()
        self._condition = condition
        self._prev_implications: Sequence[_AsyncImplication[In, PrevThenOut]] = (
            prev_implications
        )
        self._name = name


class _ElseIfSync(_BaseElseIf[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: Sequence[_Implication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__(condition, prev_implications, name)
        self._prev_implications = prev_implications

    @overload  # type: ignore[overload-overlap]
    def Then(  # type: ignore[overload-overlap]
        self, next_transformer: Transformer[In, Awaitable[ElseIfOut]]
    ) -> _IfThenAsync[In, ElseIfOut, PrevThenOut]:
        pass

    @overload  # type: ignore[overload-overlap]
    def Then(  # type: ignore[overload-overlap]
        self, next_transformer: Transformer[In, ElseIfOut]
    ) -> _IfThenSync[In, ElseIfOut, PrevThenOut]:
        pass

    def Then(self, next_transformer: Transformer[In, ElseIfOut]):
        if not isinstance(next_transformer, Transformer):
            raise UnsupportedTransformerArgException(next_transformer)

        if _returns_awaitable(next_transformer):
            async_prev = _to_async_implications(self._prev_implications)
            async_transformer = _as_async_transformer(next_transformer)
            async_implication = _AsyncImplication(self._condition, async_transformer)
            return _IfThenAsync(async_implication, self._name, async_prev)

        sync_implication = _Implication(self._condition, next_transformer)
        return _IfThenSync(sync_implication, self._name, self._prev_implications)


class _ElseIfAsync(_BaseElseIfAsync[In, PrevThenOut]):
    def __init__(
        self,
        condition: Callable[[In], bool],
        prev_implications: Sequence[_AsyncImplication[In, PrevThenOut]],
        name: str,
    ):
        super().__init__(condition, prev_implications, name)
        self._prev_implications = prev_implications

    @overload
    def Then(
        self, next_transformer: Transformer[In, Awaitable[ElseIfOut]]
    ) -> _IfThenAsync[In, ElseIfOut, PrevThenOut]:
        pass

    @overload  # type: ignore[overload-overlap]
    def Then(
        self, next_transformer: Transformer[In, ElseIfOut]
    ) -> _IfThenAsync[In, ElseIfOut, PrevThenOut]:
        pass

    def Then(self, next_transformer: Transformer[In, ElseIfOut]):
        if not isinstance(next_transformer, Transformer):
            raise UnsupportedTransformerArgException(next_transformer)

        async_transformer = _as_async_transformer(next_transformer)
        implication = _AsyncImplication(self._condition, async_transformer)
        if_then: _IfThenAsync = _IfThenAsync(
            implication, self._name, self._prev_implications
        )
        return if_then
