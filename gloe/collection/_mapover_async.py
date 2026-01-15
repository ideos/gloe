from typing import Awaitable, Callable, Generic, Iterable, TypeVar

from gloe import AsyncTransformer
from gloe._node_utils import _coerce_transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class MapOverAsync(Generic[_T, _U], AsyncTransformer[_T, list[_U]]):
    def __init__(
        self,
        iterable: Iterable[_S],
        mapping_transformer: AsyncTransformer[tuple[_T, _S], _U]
        | Callable[[_T, _S], Awaitable[_U]]
        | Callable[[_T, _S], _U],
    ):
        super().__init__()
        self.iterable = iterable
        self.mapping_transformer = _coerce_transformer(mapping_transformer)
        self.plotting_settings.has_children = True
        self._children = [self.mapping_transformer]

    async def transform_async(self, data: _T) -> list[_U]:
        lopping_result = []
        for item in self.iterable:
            if isinstance(self.mapping_transformer, AsyncTransformer):
                result = await self.mapping_transformer((data, item))
            else:
                result = self.mapping_transformer((data, item))
            lopping_result.append(result)
        return lopping_result
