import asyncio
from typing import Any
import multiprocessing
from typing_extensions import cast

import gloe
from gloe._generic_types import *
from gloe.async_transformer import AsyncTransformer, _execute_async_flow
from gloe.gateways._base_gateway import _base_gateway
from gloe.gateways._gateway_factory import _GatewayFactory
from gloe.transformers import Transformer, _execute_flow, _I, _O
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Executor

_In = TypeVar("_In")


Trf: TypeAlias = Transformer
BTrf: TypeAlias = BaseTransformer
ATrf: TypeAlias = AsyncTransformer


class _Parallel(_base_gateway[_In], Transformer[_In, tuple[Any, ...]]):
    def _transform_single(self, flow, data):
        return _execute_flow(flow, data)

    def transform_using_executor(
        self, executor_class: type[Executor], data: _In
    ) -> tuple[Any, ...]:
        with executor_class() as executor:
            flows = [transformer._flow for transformer in self._children]
            results = list(
                executor.map(
                    self._transform_single, flows, [data] * len(self._children)
                )
            )

        return tuple(results)

    async def _async_transform(self, data: _In) -> tuple[Any, ...]:
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, _execute_flow, transformer._flow, data)
            for transformer in self._children
        ]
        results = await asyncio.gather(*tasks)
        return tuple(results)

    def transform_using_asyncio(self, data: _In) -> tuple[Any, ...]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self._async_transform(data))
        loop.close()
        return results

    def transform(self, data: _In) -> tuple[Any, ...]:
        if gloe.parallelism_handler == "threads":
            return self.transform_using_executor(ThreadPoolExecutor, data)
        elif gloe.parallelism_handler == "multiprocessing":
            return self.transform_using_executor(ProcessPoolExecutor, data)
        elif gloe.parallelism_handler == "asyncio":
            return self.transform_using_asyncio(data)
        else:
            results = []
            for transformer in self._children:
                result = _execute_flow(transformer._flow, data)
                results.append(result)
            return tuple(results)


class _ParallelAsync(_base_gateway[_In], AsyncTransformer[_In, tuple[Any, ...]]):
    async def transform_async(self, data: _In) -> tuple[Any, ...]:
        results = []
        for transformer in self._children:
            if asyncio.iscoroutinefunction(transformer.__call__):
                result = await _execute_async_flow(transformer._flow, data)
            else:
                result = _execute_flow(transformer._flow, data)
            results.append(result)
        return tuple(results)


def _parallel(*transformers):
    if any(isinstance(t, AsyncTransformer) for t in transformers):
        return _ParallelAsync(*transformers)
    return _Parallel(*transformers)


parallel: _GatewayFactory = cast(_GatewayFactory, _parallel)
