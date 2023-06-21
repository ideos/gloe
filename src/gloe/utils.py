from typing import Any, TypeVar

from .functional import transformer


@transformer
def forget(data: Any) -> None:
    return None


_In = TypeVar("_In")


@transformer
def forward(data: _In) -> _In:
    return data
