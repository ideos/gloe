import asyncio
from typing import TypeVar, Any

from typing_extensions import cast

from gloe.async_transformer import AsyncTransformer, _execute_async_flow
from gloe.gateways._base_gateway import _base_gateway
from gloe.gateways._gateway_factory import _GatewayFactory
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
            if asyncio.iscoroutinefunction(transformer.__call__):
                result = await _execute_async_flow(transformer._flow, data)
            else:
                result = _execute_flow(transformer._flow, data)
            results.append(result)
        return tuple(results)


def _sequential(*transformers):
    if any(isinstance(t, AsyncTransformer) for t in transformers):
        return _SequentialAsync(*transformers)
    return _Sequential(*transformers)


sequential: _GatewayFactory = cast(_GatewayFactory, _sequential)
