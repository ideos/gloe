from typing import Any, Tuple, TypeVar

from .functional import transformer
from .transformers import forward, Transformer

_In = TypeVar("_In")
_Out = TypeVar("_Out")


@transformer
def forget(data: Any) -> None:
    return None


@transformer
def debug(income: _In) -> _In:
    breakpoint()
    return income


def forward_income(
    inner_transformer: Transformer[_In, _Out]
) -> Transformer[_In, Tuple[_Out, _In]]:
    return forward[_In]() >> (inner_transformer, forward())
