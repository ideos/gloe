from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R", bound='SequentialPass', covariant=True)


class SequentialPass(Generic[R], ABC):
    @abstractmethod
    def __rshift__(self, next_step: Any) -> R:
        pass

    # @abstractmethod
    # def forward(self, *args: Any) -> Any:
    #     pass

