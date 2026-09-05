"""Signature-preserving, invocation-local validation decorators."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar, cast

from ._core import _signature

P = ParamSpec("P")
R = TypeVar("R")
Incoming = TypeVar("Incoming")
Outcome = TypeVar("Outcome")
C = TypeVar("C")


def _validators(value: object) -> tuple[Callable[..., object], ...]:
    values = (value,) if callable(value) else value
    if not isinstance(values, (tuple, list)) or not all(callable(fn) for fn in values):
        raise TypeError("Validators must be callable or a tuple/list of callables")
    if any(
        inspect.iscoroutinefunction(fn)
        or inspect.iscoroutinefunction(getattr(fn, "__call__", None))
        for fn in values
    ):
        raise TypeError("Ensurer validators must be synchronous")
    return tuple(values)


def _check(validator: Callable[..., object], *values: object) -> None:
    result = validator(*values)
    if result is not None:
        if inspect.iscoroutine(result):
            result.close()
        raise TypeError("Ensurer validators must return None or raise")


class _Ensurer(Generic[Incoming, Outcome, C]):
    def __init__(self, incoming: object, outcome: object, changes: object) -> None:
        self.incoming = _validators(incoming)
        self.outcome = _validators(outcome)
        self.changes = _validators(changes)

    def __call__(self, function: Callable[P, R]) -> Callable[P, R]:
        signature = _signature(function)
        inputs = [
            p
            for p in signature.parameters.values()
            if p.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
        if len(inputs) != 1 or any(
            p.kind == inspect.Parameter.VAR_POSITIONAL
            for p in signature.parameters.values()
        ):
            raise TypeError(
                "Ensurers require one positional data input; use a tuple adapter"
            )

        def before(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            value = bound.arguments[inputs[0].name]
            for validator in self.incoming:
                _check(validator, value)
            return value

        def after(value: Any, result: Any) -> None:
            for validator in self.outcome:
                _check(validator, result)
            for validator in self.changes:
                _check(validator, value, result)

        if inspect.iscoroutinefunction(function):

            @wraps(function)
            async def asynchronous(*args: P.args, **kwargs: P.kwargs) -> Any:
                value = before(args, kwargs)
                result = await function(*args, **kwargs)
                after(value, result)
                return result

            return cast(Callable[P, R], asynchronous)

        @wraps(function)
        def synchronous(*args: P.args, **kwargs: P.kwargs) -> R:
            value = before(args, kwargs)
            result = function(*args, **kwargs)
            if inspect.isawaitable(result):

                async def finish() -> Any:
                    output = await result
                    after(value, output)
                    return output

                return cast(R, finish())
            after(value, result)
            return result

        return synchronous


def ensure(
    *, incoming: object = (), outcome: object = (), changes: object = ()
) -> _Ensurer[object, object, object]:
    """Validate a unary stage without replacing its signature or copying its input."""
    return _Ensurer(incoming, outcome, changes)
