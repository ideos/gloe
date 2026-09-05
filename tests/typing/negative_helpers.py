"""Collection, branching, tuple-adapter, and validation guardrails."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, overload

from gloe import (
    condition,
    ensure,
    filter,
    input,
    map,
    parallel,
    sequential,
    unpack,
)


def increment(value: int) -> int:
    return value + 1


def text(value: str) -> str:
    return value.upper()


def invalid_predicate(value: int) -> int:
    return value


def invalid_output(value: int) -> Any:
    return value


input[list[str]]() >> map(increment)  # reject: map_input
input[list[int]]() >> map(invalid_output)  # reject: map_any_output
input[list[int]]() >> filter(invalid_predicate)  # reject: filter_non_bool
input[list[int]]() >> filter(text)  # reject: filter_input


def wrong_branch(value: str) -> int:
    return len(value)


input[int]() >> parallel((increment, wrong_branch))  # reject: parallel_branch
input[int]() >> sequential((increment, wrong_branch))  # reject: sequential_branch


def invalid_condition(value: int) -> int:
    return value


input[int]() >> condition(  # reject: condition_predicate
    using=invalid_condition,
    then=increment,
    otherwise=wrong_branch,
)


def incoming_text(value: str) -> None:
    return None


def outcome_int(value: int) -> None:
    return None


def changes_text(before: str, after: str) -> None:
    return None


@ensure(incoming=incoming_text)  # reject: incoming_type
def validated_incoming(value: int) -> str:
    return str(value)


@ensure(outcome=outcome_int)  # reject: outcome_type
def validated_outcome(value: int) -> str:
    return str(value)


@ensure(changes=changes_text)  # reject: changes_type
def validated_changes(value: int) -> str:
    return str(value)


async def async_validator(value: int) -> None:
    return None


@ensure(incoming=async_validator)  # reject: async_validator
def validated_async(value: int) -> str:
    return str(value)


def two_inputs(first: int, second: str) -> str:
    return str(first) + second


@ensure(incoming=lambda value: None)  # reject: ensure_non_unary
def non_unary(value: int, second: str) -> str:
    return str(value) + second


def keyword_only(value: int, *, suffix: str) -> str:
    return str(value) + suffix


input[tuple[int, str]]() >> unpack(keyword_only)  # reject: unpack_keyword_only


def variadic(*values: int) -> int:
    return sum(values)


input[tuple[int, ...]]() >> unpack(variadic)  # reject: unpack_variadic


async def async_result(value: int) -> str:
    return str(value)


def wrong_validator_output(value: str) -> int:
    return len(value)


@ensure(outcome=wrong_validator_output)  # reject: validator_non_none
def output_checked(value: int) -> str:
    return str(value)


def callback_with_erased_output(value: int) -> Callable[..., int]:
    def needs_two(first: int, second: str) -> int:
        return first

    return needs_two


input[list[int]]() >> map(  # reject: map_erased_output
    using=callback_with_erased_output
)


@overload
def overloaded(value: int) -> str: ...


@overload
def overloaded(value: str) -> int: ...


def overloaded(value: int | str) -> str | int:
    return str(value) if isinstance(value, int) else len(value)


def check_text(value: str) -> None:
    pass


# The first overload passes, but the second output cannot use this validator.
ensure(outcome=check_text)(overloaded)  # reject:
