import asyncio
from inspect import Signature
from types import GenericAlias
from typing import TypeVar, Any, Generic

from gloe.async_transformer import AsyncTransformer

from gloe._transformer_utils import _diverging_signatures
from gloe.transformers import Transformer
from gloe.base_transformer import BaseTransformer

_In = TypeVar("_In")
_Out = TypeVar("_Out")


class _base_parallel(Generic[_In]):
    def __init__(
        self, prev_signature: Signature, *transformers: BaseTransformer[_In, Any]
    ):
        super().__init__()
        self._children = list(transformers)
        self._prev_signature = prev_signature
        self._receiving_signatures = _diverging_signatures(
            prev_signature, *transformers
        )

    def signature(self) -> Signature:
        receiving_signature_returns = [
            r.return_annotation for r in self._receiving_signatures
        ]
        new_signature = self._prev_signature.replace(
            return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns))
        )
        return new_signature


class parallel(_base_parallel[_In], Transformer[_In, tuple[Any, ...]]):
    def transform(self, data: _In) -> tuple[Any, ...]:
        results = []
        for transformer in self._children:
            results.append(transformer(data))
        return tuple(results)


class parallel_async(_base_parallel[_In], AsyncTransformer[_In, tuple[Any, ...]]):
    async def transform_async(self, data: _In) -> tuple[Any, ...]:
        results = []
        for transformer in self._children:
            if asyncio.iscoroutinefunction(transformer.__call__):
                result = await transformer(data)
            else:
                result = transformer(data)
            results.append(result)
        return tuple(results)
