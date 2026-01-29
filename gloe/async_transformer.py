from abc import abstractmethod
from inspect import Signature
from typing import TypeVar, Awaitable, get_args, get_origin

from typing_extensions import deprecated

from gloe._async_flow import _execute_async_flow
from gloe.transformers import Transformer

_In = TypeVar("_In")
_Out = TypeVar("_Out")


@deprecated("Use Transformer with async callables instead.")
class AsyncTransformer(Transformer[_In, Awaitable[_Out]]):
    def __init__(self):
        super().__init__()
        self.__class__.__annotations__ = self.transform_async.__annotations__
        orig_bases = getattr(self, "__orig_bases__", [])
        transformer_args = [
            get_args(base)
            for base in orig_bases
            if get_origin(base) == AsyncTransformer
        ]
        if transformer_args and len(transformer_args[0]) > 2:
            self._multi_args = True

    @abstractmethod
    async def transform_async(self, data: _In) -> _Out:
        """
        Main method to be implemented and responsible to perform the transformer logic.
        """

    def transform(self, data: _In) -> Awaitable[_Out]:
        return self.transform_async(data)

    def signature(self) -> Signature:
        return self._signature(AsyncTransformer, "transform_async")


__all__ = ["AsyncTransformer", "_execute_async_flow"]
