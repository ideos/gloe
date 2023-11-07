from typing import Any, Tuple, TypeVar, Generic

from .functional import transformer
from .transformers import Transformer

_In = TypeVar("_In")
_Out = TypeVar("_Out")


@transformer
def forget(data: Any) -> None:
    return None


@transformer
def debug(income: _In) -> _In:
    breakpoint()
    return income




class forward(Generic[_In], Transformer[_In, _In]):
    def __init__(self):
        super().__init__()
        self.invisible = True

    def __repr__(self):
        return str(self.previous)

    def transform(self, data: _In) -> _In:
        return data



def forward_income(
    inner_transformer: Transformer[_In, _Out]
) -> Transformer[_In, Tuple[_Out, _In]]:
    return forward[_In]() >> (inner_transformer, forward())