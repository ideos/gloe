from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from transformer import Transformer

T = TypeVar("T")
S = TypeVar("S")


class TransformerValidator(Transformer[T, S]):
    def __init__(self, transformer: Transformer[T, S]):
        super().__init__()
        self.transformer = transformer
        self.__doc__ = self.transformer.__doc__
        self.__annotations__ = self.transformer.__annotations__
        self.__class__.__name__ = self.transformer.__class__.__name__

    def __repr__(self):
        return repr(self.transformer)

    @abstractmethod
    def validate_input(self, input: T):
        pass

    @abstractmethod
    def validate_output(self, output: S):
        pass

    def transform(self, data: T) -> S:
        self.validate_input(data)
        output = self.transformer.transform(data)
        self.validate_output(output)
        return output
