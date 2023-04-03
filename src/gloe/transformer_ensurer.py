import inspect
import warnings
from abc import abstractmethod
from types import FunctionType
from typing import Any, Callable, Generic, Sequence, TypeVar, cast

from typing_extensions import Never

from .transformer import Transformer

T = TypeVar("T")
S = TypeVar("S")


class TransformerEnsurer(Generic[T]):

    @abstractmethod
    def validate_input(self, data: T):
        pass

    @abstractmethod
    def validate_output(self, output: S):
        pass

    def __call__(self, transformer: Transformer[T, S]) -> Transformer[T, S]:

        def transform(this: Transformer, data: T) -> S:
            self.validate_input(data)
            output = transformer.transform(data)
            self.validate_output(output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp


def input_ensurer(func: Callable[[T], Any]) -> TransformerEnsurer[T]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformer Ensurer. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaEnsurer(TransformerEnsurer[T]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: T):
            func(data)

        def validate_output(self, output: S):
            pass

    return LambdaEnsurer()


def output_ensurer(func: Callable[[S], Any]) -> TransformerEnsurer[S]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformer Ensurer. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaEnsurer(TransformerEnsurer[S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: T):
            pass

        def validate_output(self, output: S):
            func(output)

    return LambdaEnsurer()


def ensure_with(
    input_ensurers: Sequence[Callable[[T], Never]] = [],
    output_ensurers: Sequence[Callable[[T], Never]] = []
) -> Callable[[Transformer[T, S]], Transformer[T, S]]:
    input_ensurers_instances = [input_ensurer(ensurer) for ensurer in input_ensurers]
    output_ensurers_instances = [output_ensurer(ensurer) for ensurer in output_ensurers]

    def decorator(transformer: Transformer[T, S]) -> Transformer[T, S]:
        def transform(self, data: T) -> S:
            for ensurer in input_ensurers_instances:
                ensurer.validate_input(data)
            output = transformer.transform(data)
            for ensurer in output_ensurers_instances:
                ensurer.validate_output(output)
            return output

        transformer_cp = transformer.copy(transform)

        return transformer_cp

    return decorator
