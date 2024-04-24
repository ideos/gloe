import sys
from typing import Any, TypeVar, Generic, TypeAlias, overload

from typing_extensions import TypeVarTuple, Unpack

from gloe.functional import transformer
from gloe.transformers import Transformer

_Tup = TypeVarTuple("_Tup")
_El = TypeVar("_El")


class pick_1st(Transformer[tuple[_El, Unpack[_Tup]], _El]):
    def transform(self, data: tuple[_El, Unpack[_Tup]]) -> _El:
        return data[0]


class pick_2nd(Transformer[tuple[Any, _El, Unpack[_Tup]], _El]):
    def transform(self, data: tuple[Any, _El, Unpack[_Tup]]) -> _El:
        return data[1]


class pick_3rd(Transformer[tuple[Any, Any, _El, Unpack[_Tup]], _El]):
    def transform(self, data: tuple[Any, Any, _El, Unpack[_Tup]]) -> _El:
        return data[2]


class pick_4th(Transformer[tuple[Any, Any, Any, _El, Unpack[_Tup]], _El]):
    def transform(self, data: tuple[Any, Any, Any, _El, Unpack[_Tup]]) -> _El:
        return data[3]


class pick_5th(Transformer[tuple[Any, Any, Any, Any, _El, Unpack[_Tup]], _El]):
    def transform(self, data: tuple[Any, Any, Any, Any, _El, Unpack[_Tup]]) -> _El:
        return data[4]


class pick_6th(Transformer[tuple[Any, Any, Any, Any, Any, _El, Unpack[_Tup]], _El]):
    def transform(self, data: tuple[Any, Any, Any, Any, Any, _El, Unpack[_Tup]]) -> _El:
        return data[5]


class pick_last(Transformer[tuple[Unpack[_Tup], _El], _El]):
    def transform(self, data: tuple[Unpack[_Tup], _El]) -> _El:
        return data[-1]
