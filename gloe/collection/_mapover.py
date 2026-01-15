from typing import Callable, Generic, Iterable, TypeVar

from gloe._node_utils import _coerce_sync_transformer
from gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class MapOver(Generic[_T, _U], Transformer[_T, list[_U]]):
    def __init__(
        self,
        iterable: Iterable[_S],
        mapping_transformer: Transformer[tuple[_T, _S], _U]
        | Callable[[_T, _S], _U],
    ):
        super().__init__()
        self.iterable = iterable
        self.mapping_transformer = _coerce_sync_transformer(mapping_transformer)
        self.plotting_settings.has_children = True
        self._children = [self.mapping_transformer]

    def transform(self, data: _T) -> list[_U]:
        lopping_result = []
        for item in self.iterable:
            lopping_result.append(self.mapping_transformer((data, item)))
        return lopping_result
