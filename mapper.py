from typing import Generic, Iterable, TypeVar

from transformer import Transformer

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


class Mapper(Generic[T, U], Transformer[T, Iterable[U]]):
    def __init__(self, iterable: Iterable[S], lopping_transformer: Transformer[tuple[T, S], U]):
        super().__init__()
        self.iterable = iterable
        self.lopping_transformer = lopping_transformer

    def transform(self, data: T) -> Iterable[U]:
        lopping_result = []
        for item in self.iterable:
            lopping_result.append(self.lopping_transformer((data, item)))
        return lopping_result
