from typing import Generic, Iterable, TypeVar

from networkx import DiGraph

from src.gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class Map(Generic[_T, _U], Transformer[Iterable[_T], Iterable[_U]]):
    def __init__(self, mapping_transformer: Transformer[_T, _U]):
        super().__init__()
        self.mapping_transformer = mapping_transformer
        self.invisible = True
        self.children = [mapping_transformer]

        mapping_transformer.graph_node_props = {
            'parent_id': self.instance_id,
            'bounding_box': True,
            'box_label': 'mapping'
        }

    def transform(self, data: Iterable[_T]) -> Iterable[_U]:
        mapping_result = []
        for item in data:
            mapping_result.append(self.mapping_transformer(item))
        return mapping_result

