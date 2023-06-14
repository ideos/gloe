import inspect
import warnings
from abc import abstractmethod
from types import FunctionType
from typing import Any, Callable, Generic, Sequence, TypeVar, cast, overload
from .transformers import Transformer


_T = TypeVar("_T")
_S = TypeVar("_S")


class TransformerEnsurer(Generic[_T, _S]):

    @abstractmethod
    def validate_input(self, data: _T):
        pass

    @abstractmethod
    def validate_output(self, data: _T, output: _S):
        pass

    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:

        def transform(this: Transformer, data: _T) -> _S:
            self.validate_input(data)
            output = transformer.transform(data)
            self.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp


def input_ensurer(func: Callable[[_T], Any]) -> TransformerEnsurer[_T, Any]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformer Ensurer. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaEnsurer(TransformerEnsurer[_T, _S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: _T):
            func(data)

        def validate_output(self, data: _T, output: _S):
            pass

    return LambdaEnsurer()


def output_ensurer(func: Callable[[_T, _S], Any]) -> TransformerEnsurer[_T, _S]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformer Ensurer. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaEnsurer(TransformerEnsurer[_T, _S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: _T):
            pass

        def validate_output(self, data: _T, output: _S):
            func(data, output)

    return LambdaEnsurer()


@overload
def ensure_with(
    output_ensurers: Sequence[Callable[[_S], Any]] = []
) -> Callable[[Transformer[Any, _S]], Transformer[Any, _S]]:
    pass


@overload
def ensure_with(
    output_ensurers: Sequence[Callable[[_T, _S], Any]] = []
) -> Callable[[Transformer[_T, _S]], Transformer[_T, _S]]:
    pass


@overload
def ensure_with(
    input_ensurers: Sequence[Callable[[_T], Any]] = []
) -> Callable[[Transformer[_T, Any]], Transformer[_T, Any]]:
    pass


@overload
def ensure_with(
    input_ensurers: Sequence[Callable[[_T], Any]] = [],
    output_ensurers: Sequence[Callable[[_T, _S], Any]] = []
) -> Callable[[Transformer[_T, _S]], Transformer[_T, _S]]:
    pass


@overload
def ensure_with(
    input_ensurers: Sequence[Callable[[_T], Any]] = [],
    output_ensurers: Sequence[Callable[[_S], Any]] = []
) -> Callable[[Transformer[_T, _S]], Transformer[_T, _S]]:
    pass


def ensure_with(*args, **kwargs) -> Callable[[Transformer], Transformer]:
    if 'input_ensurers' in kwargs:
        input_ensurers = kwargs['input_ensurers']
    else:
        input_ensurers = []

    if 'output_ensurers' in kwargs:
        output_ensurers = kwargs['output_ensurers']
    else:
        output_ensurers = []

    input_ensurers_instances = [
        input_ensurer(ensurer) for ensurer in input_ensurers
    ]
    output_ensurers_instances = [
        output_ensurer(lambda _, x: ensurer(x))
        if len(inspect.signature(ensurer).parameters) == 1
        else output_ensurer(ensurer)
        for ensurer in output_ensurers
    ]

    def decorator(transformer: Transformer) -> Transformer:
        def transform(self, data):
            for ensurer in input_ensurers_instances:
                ensurer.validate_input(data)
            output = transformer.transform(data)
            for ensurer in output_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)

        return transformer_cp

    return decorator
