from typing import Literal, Protocol, TypeVar

_In = TypeVar("_In", contravariant=True)
_Out = TypeVar("_Out", covariant=True)


class SyncTransformer(Protocol[_In, _Out]):
    @property
    def is_async(self) -> Literal[False]:
        ...

    def transform(self, data: _In) -> _Out:
        ...
