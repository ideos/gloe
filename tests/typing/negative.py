"""Invalid expressions that must fail at their source line."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from gloe import input


def increment(value: int) -> int:
    return value + 1


def text_only(value: str) -> str:
    return value.upper()


input[int]() >> text_only  # reject: incompatible_stage


input[int]() >> (increment, text_only)  # reject: incompatible_branch


def unknown_output(value: int) -> Any:
    return value


input[int]() >> unknown_output  # reject: any_output


def erased_output(value: int) -> Callable[..., int]:
    def needs_two(item: int, label: str) -> int:
        return item

    return needs_two


input[int]() >> erased_output(1)  # reject: erased_output


input[Any]()  # reject: any_input
