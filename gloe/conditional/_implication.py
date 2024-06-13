import copy
import sys
from dataclasses import dataclass

from typing_extensions import Self

from gloe.base_transformer import BaseTransformer

if sys.version_info >= (3, 10):
    pass
from typing import (
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
class _AsyncImplication(_BaseImplication[In, ThenOut]):
    condition: Callable[[In], bool]
    then_transformer: BaseTransformer[In, ThenOut]
