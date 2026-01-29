from inspect import isawaitable
from typing import TypeVar, Any, Awaitable, cast

from gloe.base_transformer import BaseTransformer
from gloe.gateways._base_gateway import _base_gateway
from gloe.gateways._gateway_factory import _gateway_factory
from gloe.transformers import Transformer, _execute_flow

_In = TypeVar("_In")
_Out = TypeVar("_Out")


class _Sequential(_base_gateway[_In], Transformer[_In, _Out]):
    def transform(self, data: _In) -> _Out:
        results: list[Any] = []
        for index, transformer in enumerate(self._children):
            result = _execute_flow(transformer._flow, data)
            if isawaitable(result):
                remaining = self._children[index + 1 :]

                async def _await_results() -> tuple[Any, ...]:
                    results.append(await result)
                    for next_transformer in remaining:
                        next_result = _execute_flow(next_transformer._flow, data)
                        if isawaitable(next_result):
                            results.append(await next_result)
                        else:
                            results.append(next_result)
                    return tuple(results)

                return cast(_Out, _await_results())
            results.append(result)
        return cast(_Out, tuple(results))


@_gateway_factory
def sequential(*transformers: BaseTransformer) -> Transformer:
    """
    Execute the transformers one after the other, awaiting any async steps.

    Args:
        *transformers (Sequence[Transformer]): the list of transformers that will
            receive the same input.

    Returns:
        Transformer: a transformer that will execute all the transformers in order
            and return a tuple with the results. If any child yields an awaitable,
            the returned transformer yields an awaitable tuple.
    """
    return _Sequential(*transformers)
