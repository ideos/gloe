import copy
from dataclasses import dataclass

from typing_extensions import Self

from gloe.base_transformer import BaseTransformer
from typing import (
    Awaitable,
    Callable,
    Generic,
    TypeVar,
)

from gloe.transformers import Transformer

In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)


class _BaseImplication(Generic[In, ThenOut]):
    condition: Callable[[In], bool]
    then_transformer: BaseTransformer[In, ThenOut]

    def copy(self) -> Self:
        copied = copy.copy(self)
        copied.then_transformer = self.then_transformer.copy(
            regenerate_instance_id=True
        )
        return copied


@dataclass
class _Implication(_BaseImplication[In, ThenOut]):
    condition: Callable[[In], bool]
    then_transformer: Transformer[In, ThenOut]


@dataclass
class _AsyncImplication(_BaseImplication[In, Awaitable[ThenOut]]):
    condition: Callable[[In], bool]
    then_transformer: Transformer[In, Awaitable[ThenOut]]

    def copy(self) -> Self:
        copied = copy.copy(self)
        copied.then_transformer = self.then_transformer.copy(
            regenerate_instance_id=True
        )
        return copied
