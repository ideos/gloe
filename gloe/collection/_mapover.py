import asyncio
from inspect import isawaitable
from typing import Generic, Iterable, TypeVar, Awaitable, Any, overload, cast


from gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")
_Out = TypeVar("_Out")


class MapOver(Generic[_T, _Out], Transformer[_T, _Out]):
    @overload
    def __init__(
        self: "MapOver[_T, list[_U]]",
        iterable: Iterable[_S],
        mapping_transformer: Transformer[tuple[_T, _S], _U],
    ):
        ...

    @overload
    def __init__(
        self: "MapOver[_T, Awaitable[list[_U]]]",
        iterable: Iterable[_S],
        mapping_transformer: Transformer[tuple[_T, _S], Awaitable[_U]],
    ):
        ...

    @overload
    def __init__(
        self: "MapOver[_T, list[_U]]",
        iterable: Iterable[_S],
        mapping_transformer: Transformer[_T, _S, _U],
    ):
        ...

    @overload
    def __init__(
        self: "MapOver[_T, Awaitable[list[_U]]]",
        iterable: Iterable[_S],
        mapping_transformer: Transformer[_T, _S, Awaitable[_U]],
    ):
        ...

    def __init__(  # type: ignore[misc]
        self,
        iterable: Iterable[_S],
        mapping_transformer: Transformer[Any, Any],
    ):
        super().__init__()
        self.iterable = iterable
        self.mapping_transformer = mapping_transformer
        self.plotting_settings.has_children = True
        self._children = [mapping_transformer]

    def transform(self, data: _T) -> _Out:
        lopping_result: list[Any] = []
        awaitables: list[tuple[int, Awaitable[Any]]] = []

        for item in self.iterable:
            result = self.mapping_transformer((data, item))
            if isawaitable(result):
                awaitables.append((len(lopping_result), result))
                lopping_result.append(None)
            else:
                lopping_result.append(result)

        if len(awaitables) == 0:
            return cast(_Out, lopping_result)

        async def _await_results() -> list[Any]:
            awaited = await asyncio.gather(*[result for _, result in awaitables])
            for (index, _), value in zip(awaitables, awaited):
                lopping_result[index] = value
            return lopping_result

        return cast(_Out, _await_results())
