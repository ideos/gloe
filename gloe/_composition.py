from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from gloe.base_transformer import BaseTransformer


class CompositionMixin:
    """
    Mixin that provides the `__rshift__` composition method to the transformers.
    """

    def __rshift__(self, next_node: Union[tuple, "BaseTransformer"]):
        from gloe._composition_utils import _compose_nodes

        return _compose_nodes(self, next_node)
