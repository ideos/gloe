import inspect
import warnings
from inspect import Signature
from types import FunctionType
from typing import Any, Callable, Concatenate, ParamSpec, Tuple, TypeVar, cast, overload

from .transformers import Transformer

A = TypeVar("A")
S = TypeVar("S")
P1 = ParamSpec("P1")


def transformer_init(func: Callable[Concatenate[A, P1], S]) -> Callable[P1, Transformer[A, S]]:
    func_signature = inspect.signature(func)

    def init_func(*args: P1.args, **kwargs: P1.kwargs) -> Transformer[A, S]:
        class LambdaTransformer(Transformer[A, S]):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return func_signature

            def transform(self, data: A) -> S:
                return func(data, *args, **kwargs)

        lambda_transformer = LambdaTransformer()
        lambda_transformer.__class__.__name__ = func.__name__
        lambda_transformer.label = func.__name__
        return lambda_transformer

    return init_func


def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    func_signature = inspect.signature(func)

    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformers. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaTransformer(Transformer):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def signature(self) -> Signature:
            return func_signature

        def transform(self, data):
            return func(data)

    lambda_transformer = LambdaTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    lambda_transformer.label = func.__name__
    return lambda_transformer
