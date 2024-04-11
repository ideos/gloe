from typing import Generic, Iterable, TypeVar

from networkx import DiGraph

from ..transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class MapOver(Generic[_T, _U], Transformer[_T, list[_U]]):
    def __init__(
        self,
        iterable: list[_S],
        mapping_transformer: Transformer[tuple[_T, _S], _U],
    ):
        super().__init__()
        self.iterable = iterable
        self.mapping_transformer = mapping_transformer
        self._invisible = True
        self._children = [mapping_transformer]

    def transform(self, data: _T) -> list[_U]:
        lopping_result = []
        for item in self.iterable:
            lopping_result.append(self.mapping_transformer((data, item)))
        return lopping_result

    def _add_child_node(
        self,
        child: "Transformer",
        child_net: DiGraph,
        parent_id: str,
        next_node: "Transformer",
    ):
        child._dag(
            child_net,
            next_node,
            {"parent_id": parent_id, "bounding_box": True, "box_label": "mapping"},
        )
