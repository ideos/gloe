import asyncio
from inspect import isawaitable
from typing import Any, TypeVar, Awaitable, cast

from gloe.base_transformer import BaseTransformer
from gloe.gateways._base_gateway import _base_gateway
from gloe.gateways._gateway_factory import _gateway_factory
from gloe.transformers import Transformer, _execute_flow

_In = TypeVar("_In")
_Out = TypeVar("_Out")


class _Parallel(_base_gateway[_In], Transformer[_In, _Out]):
    def transform(self, data: _In) -> _Out:
        results: list[Any] = [None] * len(self._children)
        awaitables: list[tuple[int, Any]] = []

        for index, transformer in enumerate(self._children):
            result = _execute_flow(transformer._flow, data)
            if isawaitable(result):
                awaitables.append((index, result))
            else:
                results[index] = result

        if len(awaitables) == 0:
            return cast(_Out, tuple(results))

        async def _await_results() -> tuple[Any, ...]:
            awaited = await asyncio.gather(*[result for _, result in awaitables])
            for (index, _), value in zip(awaitables, awaited):
                results[index] = value
            return tuple(results)

        return cast(_Out, _await_results())


@_gateway_factory
def parallel(*transformers: BaseTransformer) -> Transformer:
    """
    Currently, the parallelism of transformers is supported only by executing
    awaitables concurrently.

    Args:
        *transformers (Sequence[Transformer]): the list of transformers that will
            receive the same input.

    Returns:
        Transformer: a transformer that will execute all the transformers in parallel
            and return a tuple with the results. If any child returns an awaitable, the
            returned transformer yields an awaitable tuple.
    """
    return _Parallel(*transformers)
