from typing import Generic, Iterable, TypeVar

from gloe import AsyncTransformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class MapOverAsync(Generic[_T, _U], AsyncTransformer[_T, Iterable[_U]]):
    def __init__(
        self,
        iterable: Iterable[_S],
        mapping_transformer: AsyncTransformer[tuple[_T, _S], _U],
    ):
        super().__init__()
        self.iterable = iterable
        self.mapping_transformer = mapping_transformer
        self.plotting_settings.has_children = True
        self._children = [mapping_transformer]

    async def transform_async(self, data: _T) -> Iterable[_U]:
        lopping_result = []
        for item in self.iterable:
            result = await self.mapping_transformer((data, item))
            lopping_result.append(result)
        return lopping_result
