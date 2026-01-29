from inspect import isawaitable
from typing import Any
from gloe.base_transformer import BaseTransformer, Flow

__all__ = ["_execute_async_flow"]


async def _execute_async_flow(flow: Flow, arg: Any) -> Any:
    result = arg
    for op in flow:
        if isinstance(op, BaseTransformer):
            if hasattr(op, "_safe_transform"):
                result = op._safe_transform(result)
                if isawaitable(result):
                    result = await result
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
    return result
