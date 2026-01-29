from typing import Generic, Iterable, TypeVar, Awaitable

from typing_extensions import deprecated

from gloe.collection._mapover import MapOver
from gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


@deprecated("Use MapOver with async callables instead.")
class MapOverAsync(Generic[_T, _U], MapOver[_T, Awaitable[list[_U]]]):
    def __init__(
        self,
        iterable: Iterable[_S],
        mapping_transformer: Transformer[tuple[_T, _S], Awaitable[_U]],
    ):
        super().__init__(iterable, mapping_transformer)
