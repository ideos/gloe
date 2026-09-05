"""Small callable factories; business functions need no wrapper to compose."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from functools import wraps
from inspect import Parameter, Signature
from typing import Any, ParamSpec, TypeVar, TypeVarTuple, Unpack, cast

from ._core import _concurrent, _invoke, _signature

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
S = TypeVar("S")
Ts = TypeVarTuple("Ts")


def _describe(
    function: Callable[..., Any], label: str, children: tuple[object, ...]
) -> None:
    setattr(function, "__gloe_label__", label)
    setattr(function, "__gloe_children__", children)


def transformer(function: Callable[P, R]) -> Callable[P, Callable[P, R]]:
    """Bind keyword-only configuration, keeping positional inputs for execution."""
    original = _signature(function)
    if any(
        p.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)
        for p in original.parameters.values()
    ):
        raise TypeError("Configured transformers require explicit parameters")
    config = Signature(
        [p for p in original.parameters.values() if p.kind == Parameter.KEYWORD_ONLY]
    )
    inputs = Signature(
        [p for p in original.parameters.values() if p.kind != Parameter.KEYWORD_ONLY]
    )

    @wraps(function)
    def configure(**configuration: Any) -> Callable[..., Any]:
        bound = config.bind(**configuration)
        bound.apply_defaults()

        @wraps(function)
        def invoke(*args: Any, **kwargs: Any) -> Any:
            inputs.bind(*args, **kwargs)
            return function(*args, **kwargs, **bound.arguments)

        setattr(
            invoke,
            "__signature__",
            inputs.replace(return_annotation=original.return_annotation),
        )
        _describe(invoke, getattr(function, "__name__", type(function).__name__), ())
        return invoke

    setattr(configure, "__signature__", config)
    return cast(Callable[P, Callable[P, R]], configure)


def map(using: Callable[[T], R]) -> Callable[[Iterable[T]], Awaitable[list[R]]]:
    """Map an iterable sequentially, awaiting callback results when necessary."""
    if not callable(using):
        raise TypeError("map using must be callable")

    async def apply(values: Iterable[T]) -> list[R]:
        return [await _invoke(using, value) for value in values]

    _describe(apply, "map", (using,))
    return apply


def filter(using: Callable[[T], object]) -> Callable[[Iterable[T]], Awaitable[list[T]]]:
    """Keep matching values in order. Predicates must resolve to bool."""
    if not callable(using):
        raise TypeError("filter using must be callable")

    async def apply(values: Iterable[T]) -> list[T]:
        output = []
        for value in values:
            if await _predicate(using, value):
                output.append(value)
        return output

    _describe(apply, "filter", (using,))
    return apply


async def _predicate(using: Callable[[T], object], value: T) -> bool:
    result = await _invoke(using, value)
    if not isinstance(result, bool):
        raise TypeError("Predicate must return bool")
    return result


def condition(
    using: Callable[[T], object], *, then: Callable[[T], R], otherwise: Callable[[T], S]
) -> Callable[[T], Awaitable[R | S]]:
    """Invoke exactly one branch with the original input."""
    if not all(callable(fn) for fn in (using, then, otherwise)):
        raise TypeError("Condition predicate and branches must be callable")

    async def apply(value: T) -> R | S:
        selected = then if await _predicate(using, value) else otherwise
        return cast(R | S, await _invoke(selected, value))

    _describe(apply, "condition", (using, then, otherwise))
    return apply


def parallel(using: Iterable[Callable[[T], R]]) -> Callable[[T], Awaitable[list[R]]]:
    """Run a configured collection of branches concurrently with shared input."""
    functions = _branches(using)

    async def apply(value: T) -> list[R]:
        return await _concurrent(functions, value)

    _describe(apply, "parallel", functions)
    return apply


def sequential(using: Iterable[Callable[[T], R]]) -> Callable[[T], Awaitable[list[R]]]:
    """Run configured branches in order, each receiving the same input."""
    functions = _branches(using)

    async def apply(value: T) -> list[R]:
        return [await _invoke(function, value) for function in functions]

    _describe(apply, "sequential", functions)
    return apply


def _branches(using: Iterable[Callable[[T], R]]) -> tuple[Callable[[T], R], ...]:
    functions = tuple(using)
    if not all(callable(fn) for fn in functions):
        raise TypeError("Every branch must be callable")
    return functions


def unpack(function: Callable[[Unpack[Ts]], R]) -> Callable[[tuple[Unpack[Ts]]], R]:
    """Explicitly spread a tuple into a callable's positional arguments."""

    @wraps(function)
    def apply(values: tuple[Unpack[Ts]]) -> R:
        return function(*values)

    # Discard a copied factory signature before describing the unary adapter.
    apply.__dict__.pop("__signature__", None)
    setattr(apply, "__signature__", _signature(apply, follow_wrapped=False))
    _describe(apply, "unpack", (function,))
    return apply
