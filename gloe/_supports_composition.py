from typing import Protocol, TypeVar

from gloe.base_transformer import BaseTransformer

T = TypeVar("T", covariant=True, bound=BaseTransformer)
S = TypeVar("S", contravariant=True)


class SupportsComposition(Protocol[S, T]):
    def __compose__(self, prev: S) -> T:
        pass
