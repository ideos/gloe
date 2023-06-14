import inspect
import warnings
from inspect import Signature
from types import FunctionType
from typing import Any, Callable, Concatenate, ParamSpec, Tuple, TypeVar, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from .transformers import Transformer

A = TypeVar("A")
S = TypeVar("S")
U = TypeVar("U")
P = TypeVar("P")
P1 = TypeVar("P1")
P2 = TypeVar("P2")
P3 = TypeVar("P3")
P4 = TypeVar("P4")
P5 = TypeVar("P5")
P6 = TypeVar("P6")
P7 = TypeVar("P7")


@overload
def transformer(func: Callable[[P1, A], S]) -> Callable[[P1], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[P1, P2, A], S]) -> Callable[[P1, P2], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[P1, P2, P3, A], S]) -> Callable[[P1, P2, P3], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[P1, P2, P3, P4, A], S]) -> Callable[[P1, P2, P3, P4], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[P1, P2, P3, P4, P5, A], S]) -> Callable[[P1, P2, P3, P4, P5], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[P1, P2, P3, P4, P5, P6, A], S]) -> Callable[[P1, P2, P3, P4, P5, P6], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[P1, P2, P3, P4, P5, P6, P7, A], S]) -> Callable[[P1, P2, P3, P4, P5, P6, P7], Transformer[A, S]]:
    pass


@overload
def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    pass


def transformer(func: Callable):
    func_signature = inspect.signature(func)

    if len(func_signature.parameters) == 1:
        class LambdaTransformer(Transformer):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return func_signature

            def transform(self, data):
                return func(data)

        lambda_transformer = LambdaTransformer()
        lambda_transformer.__class__.__name__ = func.__name__
        return lambda_transformer

    def exec_func(*args, **kwargs) -> Transformer[A, S]:
        class LambdaTransformer(Transformer[A, S]):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return func_signature

            def transform(self, data: A) -> S:
                return func(data, *args)

        lambda_transformer = LambdaTransformer()
        lambda_transformer.__class__.__name__ = func.__name__
        return lambda_transformer

    return exec_func
