from typing import Iterable, Optional, TypeVar
from multiprocessing.pool import ThreadPool as Pool

from gloe import Transformer
from gloe.collection._mapover import MapOver
from gloe.collection._map import Map

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class ParallelMap(Map):

    def __init__(
        self, mapping_transformer: Transformer[_T, _U], pool_size: Optional[int] = None
    ):
        super().__init__(mapping_transformer)
        self.pool_size = pool_size

    def transform(self, data: Iterable[_T]) -> Iterable[_U]:

        with Pool(self.pool_size) as p:
            mapping_result = p.map(self.mapping_transformer, data)
        return mapping_result


class ParallelMapOver(MapOver):

    def __init__(
        self,
        iterable: list[_S],
        mapping_transformer: Transformer[tuple[_T, _S], _U],
        pool_size: Optional[int] = None,
    ):
        super().__init__(iterable, mapping_transformer)

        self.pool_size = pool_size

    def transform(self, data: _T) -> Iterable[_U]:

        inputs = [(data, item) for item in self.iterable]

        with Pool(self.pool_size) as p:
            lopping_result = p.map(self.mapping_transformer, inputs)

        return lopping_result
