import inspect
from typing import Any, Generic, Iterable, TypeVar, Union

from networkx import DiGraph
import networkx as nx

from .transformer import Transformer

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


class Mapper(Generic[T, U], Transformer[T, Iterable[U]]):
    def __init__(self, iterable: Iterable[S], looping_transformer: Transformer[tuple[T, S], U]):
        super().__init__()
        self.iterable = iterable
        self.looping_transformer = looping_transformer
        self.invisible = True
        self.children = [looping_transformer]

    def transform(self, data: T) -> Iterable[U]:
        lopping_result = []
        for item in self.iterable:
            lopping_result.append(self.looping_transformer((data, item)))
        return lopping_result

    def _add_child_node(
        self,
        child: 'Transformer',
        child_net: DiGraph,
        parent_id: str,
        next_node: 'Transformer'
    ):
        child._dag(
            child_net,
            next_node,
            {
                'parent_id': parent_id,
                'bounding_box': True,
                'box_label': 'mapping'
            }
        )
