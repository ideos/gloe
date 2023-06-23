import inspect
import warnings
from abc import abstractmethod
from types import FunctionType
from typing import Any, \
    Callable, \
    Generic, \
    ParamSpec, \
    Sequence, \
    TypeVar, \
    Union, cast, \
    overload

from .transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
P1 = ParamSpec("P1")


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


@overload
def output_ensurer(func: Callable[[_T, _S], Any]) -> TransformerEnsurer[_T, _S]:
    pass


@overload
def output_ensurer(func: Callable[[_S], Any]) -> TransformerEnsurer[Any, _S]:
    pass


def output_ensurer(func: Callable):
    class LambdaEnsurer(TransformerEnsurer):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data):
            pass

        def validate_output(self, data, output):
            if len(inspect.signature(func).parameters) == 1:
                func(output)
            else:
                func(data, output)

    return LambdaEnsurer()


@overload
def ensure(
    income: Sequence[Callable[[_T], Any]]
) -> Callable[[Transformer[_T, _S]], Transformer[_T, _S]]:
    pass


@overload
def ensure(
    outcome: Sequence[Union[Callable[[_S], Any], Callable[[Any, _S], Any]]]
) -> Callable[[Transformer[_T, _S]], Transformer[_T, _S]]:
    pass


@overload
def ensure(
    income: Sequence[Callable[[_T], Any]],
    outcome: Sequence[Union[Callable[[_S], Any], Callable[[_T, _S], Any]]]
) -> Callable[[Transformer[_T, _S]], Transformer[_T, _S]]:
    pass


def ensure(*args, **kwargs):
    if 'income' in kwargs:
        input_ensurers = kwargs['income']
    else:
        input_ensurers = []

    if 'outcome' in kwargs:
        output_ensurers = kwargs['outcome']
    else:
        output_ensurers = []

    input_ensurers_instances = [
        input_ensurer(ensurer) for ensurer in input_ensurers
    ]

    output_ensurers_instances = [
        output_ensurer(ensurer) for ensurer in output_ensurers
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


@overload
def ensured_init(
    income: Sequence[Callable[[_T], Any]]
) -> Callable[[Callable[P1, Transformer[_T, _S]]], Callable[P1, Transformer[_T, _S]]]:
    pass


@overload
def ensured_init(
    outcome: Sequence[Union[Callable[[_S], Any], Callable[[Any, _S], Any]]]
) -> Callable[[Callable[P1, Transformer[_T, _S]]], Callable[P1, Transformer[_T, _S]]]:
    pass


@overload
def ensured_init(
    income: Sequence[Callable[[_T], Any]],
    outcome: Sequence[Union[Callable[[_S], Any], Callable[[_T, _S], Any]]]
) -> Callable[[Callable[P1, Transformer[_T, _S]]], Callable[P1, Transformer[_T, _S]]]:
    pass


def ensured_init(*args, **kwargs):
    if 'income' in kwargs:
        input_ensurers = kwargs['income']
    else:
        input_ensurers = []

    if 'outcome' in kwargs:
        output_ensurers = kwargs['outcome']
    else:
        output_ensurers = []

    input_ensurers_instances = [
        input_ensurer(ensurer) for ensurer in input_ensurers
    ]

    output_ensurers_instances = [
        output_ensurer(ensurer) for ensurer in output_ensurers
    ]

    def decorator(transformer_init: Callable[P1, Transformer]) -> Callable[P1, Transformer]:
        def ensured_transformer_init(*args, **kwargs):
            transformer = transformer_init(*args, **kwargs)

            def transform(self, data):
                for ensurer in input_ensurers_instances:
                    ensurer.validate_input(data)
                output = transformer.transform(data)
                for ensurer in output_ensurers_instances:
                    ensurer.validate_output(data, output)
                return output

            transformer_cp = transformer.copy(transform)

            return transformer_cp

        return ensured_transformer_init

    return decorator
