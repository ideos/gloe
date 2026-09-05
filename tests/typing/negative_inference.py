"""Ambiguous anchors and branches require an explicit input type."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, overload

from gloe import input


def increment(value: int) -> int:
    return value + 1


def text(value: str) -> str:
    return value.upper()


input() >> input()  # reject: identity_only
input() >> (increment, text)  # reject: incompatible_branch_inputs
input() >> (increment, input())


def generic[T](value: T) -> T:
    return value


input() >> generic  # reject: generic_first_stage


@overload
def convert(value: int) -> str: ...


@overload
def convert(value: str) -> int: ...


def convert(value: int | str) -> int | str:
    return str(value) if isinstance(value, int) else len(value)


input() >> convert  # reject: overloaded_first_stage


def erased(value: Any) -> int:
    return 0


input() >> erased  # reject: any_first_stage


def zero() -> int:
    return 0


input() >> zero  # reject: zero_argument_inference


def two(first: int, second: str) -> int:
    return first


input() >> two  # reject: multiple_argument_inference


def erased_callable(value: int) -> Callable[..., int]:
    def needs_two(first: int, second: str) -> int:
        return first

    return needs_two


input() >> erased_callable  # reject: erased_callable_inference
