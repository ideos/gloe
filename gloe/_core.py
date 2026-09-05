"""Immutable plans and one execution path for synchronous and asynchronous stages."""

from __future__ import annotations

import asyncio
import inspect
import sys
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, ParamSpec, TypeVar, cast
from typing_extensions import TypeVar as DefaultTypeVar

P = ParamSpec("P")
R = TypeVar("R")


class _InferInput:
    """An unresolved input anchor, deliberately distinct from Any."""


T = DefaultTypeVar("T", default=_InferInput)


class _GloeMypyPluginRequired:
    """Configure plugins = ["gloe.mypy_plugin"] to check composition."""


def _signature(
    function: Callable[..., Any], *, follow_wrapped: bool = True
) -> inspect.Signature:
    # Binding needs parameter shapes, never evaluation of user annotations.
    if sys.version_info >= (3, 14):
        from annotationlib import Format

        return inspect.signature(
            function, follow_wrapped=follow_wrapped, annotation_format=Format.STRING
        )
    return inspect.signature(function, follow_wrapped=follow_wrapped)


async def _invoke(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    result = function(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


async def _concurrent(functions: Iterable[Callable[..., Any]], value: Any) -> list[Any]:
    # Keep cleanup local to this invocation, including on parent cancellation.
    tasks = [asyncio.create_task(_invoke(function, value)) for function in functions]
    try:
        return list(await asyncio.gather(*tasks))
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise


@dataclass(frozen=True, init=False, eq=False)
class Transformer(Generic[P, R]):
    """A reusable plan. Calling it is asynchronous; ``sync`` is the blocking entry."""

    _source: Callable[..., Any] | None
    _start: Callable[P, Awaitable[Any]]
    _steps: tuple[object, ...]

    def __init__(self, function: Callable[P, R]) -> None:
        if not callable(function):
            raise TypeError("Transformer requires a callable")

        async def start(*args: P.args, **kwargs: P.kwargs) -> Any:
            return await _invoke(function, *args, **kwargs)

        object.__setattr__(self, "_source", function)
        object.__setattr__(self, "_start", start)
        object.__setattr__(self, "_steps", ())

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        value = await self._start(*args, **kwargs)
        for node in self._steps:
            if isinstance(node, tuple):
                value = tuple(await _concurrent(node, value))
            else:
                value = await _invoke(cast(Callable[..., Any], node), value)
        # Heterogeneous nodes are checked at composition edges by the plugin.
        return cast(R, value)

    def sync(self, *args: P.args, **kwargs: P.kwargs) -> R:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self(*args, **kwargs))
        raise RuntimeError("Use await pipe(...) inside a running event loop")

    def __rshift__(self, node: _GloeMypyPluginRequired) -> Transformer[P, Any]:
        value: object = node
        if type(value) in (Transformer, input):
            value = cast(Transformer[..., Any], value)
            # Flatten sequential plans without deduplicating repeated occurrences.
            steps = (() if value._source is None else (value._source,)) + value._steps
        elif isinstance(value, tuple):
            if not all(callable(branch) for branch in value):
                raise TypeError("Every branch must be callable")
            steps = (value,)
        elif callable(value):
            steps = (value,)
        else:
            raise TypeError("Expected a callable or a tuple of callables")
        following: Transformer[P, Any] = object.__new__(Transformer)
        object.__setattr__(following, "_source", self._source)
        object.__setattr__(following, "_start", self._start)
        object.__setattr__(following, "_steps", self._steps + steps)
        return following

    def graph(self) -> Graph:
        from ._graph import build_graph

        return build_graph(self)

    def to_dot(self, path: str | Path | None = None) -> str:
        return self.graph().to_dot(path)

    def to_image(self, path: str | Path, *, prog: str = "dot") -> None:
        self.graph().to_image(path, prog=prog)


class input(Transformer[[T], T]):
    """Start a unary pipeline; explicit ``input[T]()`` resolves ambiguous types."""

    def __init__(self) -> None:
        async def identity(value: T) -> T:
            return value

        # Identity preserves an awaitable input as data instead of consuming it.
        object.__setattr__(self, "_source", None)
        object.__setattr__(self, "_start", identity)
        object.__setattr__(self, "_steps", ())


from ._graph import Graph  # noqa: E402
