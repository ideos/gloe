from typing import Generic, TypeVar, Iterable, Awaitable

from typing_extensions import deprecated

from gloe.collection._map import Map
from gloe.transformers import Transformer

_T = TypeVar("_T", contravariant=True)
_U = TypeVar("_U", covariant=True)


@deprecated("Use Map with async callables instead.")
class MapAsync(Generic[_T, _U], Map[_T, Awaitable[list[_U]]]):
    """
    Async transformer used to map values in an iterable using other async
    transformers instead of functions.
    """

    def __init__(self, mapping_transformer: Transformer[_T, Awaitable[_U]]):
        super().__init__(mapping_transformer)
