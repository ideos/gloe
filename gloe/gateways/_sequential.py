from typing import TypeVar, Any, Union

from gloe.base_transformer import BaseTransformer
from gloe.async_transformer import AsyncTransformer, _execute_async_flow
from gloe.gateways._base_gateway import _base_gateway
from gloe.gateways._gateway_factory import _gateway_factory
from gloe.transformers import Transformer, _execute_flow

_In = TypeVar("_In")
_Out = TypeVar("_Out")


class _Sequential(_base_gateway[_In], Transformer[_In, tuple[Any, ...]]):
    def transform(self, data: _In) -> tuple[Any, ...]:
        results = []
        for transformer in self._children:
            result = _execute_flow(transformer._flow, data)
            results.append(result)
        return tuple(results)


class _SequentialAsync(_base_gateway[_In], AsyncTransformer[_In, tuple[Any, ...]]):
    async def transform_async(self, data: _In) -> tuple[Any, ...]:
        results = []
        for transformer in self._children:
            if isinstance(transformer, AsyncTransformer):
                result = await _execute_async_flow(transformer._flow, data)
            else:
                result = _execute_flow(transformer._flow, data)
            results.append(result)
        return tuple(results)


@_gateway_factory
def sequential(*transformers: BaseTransformer) -> Union[Transformer, AsyncTransformer]:
    """
    Execute the transformers one after the other, even the async transformers.

    Args:
        *transformers (Sequence[Transformer | AsyncTransformer]): the list of
            transformers what will receive the same input.

    Returns:
        Union[Transformer, AsyncTransformer]: a transformer that will execute all the
            transformers in parallel and return a tuple with the results. If at least
            one of the transformers passed is an AsyncTransformer, the returned
            transformer is also an AsyncTransformer. Otherwise, the returned transformer
            is sync.
    """
    if any(isinstance(t, AsyncTransformer) for t in transformers):
        return _SequentialAsync(*transformers)
    return _Sequential(*transformers)
