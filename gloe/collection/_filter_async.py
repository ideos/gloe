from typing import Generic, TypeVar, Iterable, Awaitable

from typing_extensions import deprecated

from gloe.collection._filter import Filter
from gloe.transformers import Transformer

_T = TypeVar("_T")


@deprecated("Use Filter with async callables instead.")
class FilterAsync(Generic[_T], Filter[_T, Awaitable[list[_T]]]):
    """
    Async transformer used to filter values in an iterable using other async
    transformers instead of functions.
    """

    def __init__(self, filter_transformer: Transformer[_T, Awaitable[bool]]):
        super().__init__(filter_transformer)
