"""The plugin rejects gradual-typing erasure at pipeline boundaries."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any, TypedDict

from gloe import Transformer, input


def nested_any(value: int) -> list[Any]:
    return [value]


input[int]() >> nested_any  # reject: nested_result_any


def mapping_any(value: int) -> dict[str, Any]:
    return {"value": value}


input[int]() >> mapping_any  # reject: mapping_result_any


class Payload(TypedDict):
    value: Any


def typed_dict_any(value: int) -> Payload:
    return {"value": value}


input[int]() >> typed_dict_any  # reject: typeddict_result_any


def unknown(value: int) -> Any:
    return value


Transformer(unknown)  # reject: transformer_result_any


input[Any]()  # reject: input_any
input[list[Any]]()  # reject: nested_input_any
input[Callable[..., int]]()  # reject: input_erased_callable


def erased(value: int) -> Callable[..., int]:
    def needs_two(first: int, second: str) -> int:
        return first

    return needs_two


input[int]() >> erased  # reject: erased_result_signature


def configure(value: int, *, prefix: str) -> str:
    return prefix + str(value)


erased_partial: partial[str] = partial(configure, prefix="v")
input[int]() >> erased_partial  # reject: erased_partial_signature
