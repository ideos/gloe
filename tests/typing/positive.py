"""Positive checker contracts for the public Gloe typing surface."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import partial
from typing import ParamSpec, TypeVar, assert_type, cast, overload

from typing_extensions import TypeIs

from gloe import (
    Transformer,
    condition,
    filter,
    input,
    map,
    parallel,
    sequential,
    transformer,
    unpack,
    ensure,
)

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")


def increment(value: int) -> int:
    return value + 1


def double(value: int) -> int:
    return value * 2


async def stringify(value: int) -> str:
    return str(value)


def maybe_async(value: int) -> int | Awaitable[int]:
    return value if value % 2 else stringify_number(value)


async def stringify_number(value: int) -> int:
    return value


def pair(value: int) -> tuple[int, str]:
    return value, str(value)


def combine(number: int, text: str) -> str:
    return f"{number}:{text}"


def optional_combine(number: int, text: str = "") -> str:
    return f"{number}:{text}"


def configured(value: int, *, prefix: str, repeat: int = 1) -> str:
    return prefix + str(value) * repeat


def same(value: T) -> T:
    return value


@overload
def convert(value: int) -> str: ...


@overload
def convert(value: str) -> int: ...


def convert(value: int | str) -> str | int:
    return str(value) if isinstance(value, int) else len(value)


class ToText:
    def __call__(self, value: int) -> str:
        return str(value)


def preserve(function: Callable[P, R]) -> Callable[P, R]:
    return function


plain = input[int]() >> increment >> stringify
assert_type(plain, Transformer[[int], str])

inferred = input() >> increment >> stringify
assert_type(inferred, Transformer[[int], str])

branched = input[int]() >> (increment, stringify)
assert_type(branched, Transformer[[int], tuple[int, str]])

wide = input[int]() >> (increment, stringify, double, stringify)
assert_type(wide, Transformer[[int], tuple[int, str, int, str]])

optional = input[int]() >> maybe_async >> double
assert_type(optional, Transformer[[int], int])

unpacked = input[int]() >> pair >> unpack(combine)
assert_type(unpacked, Transformer[[int], str])

optional_unpacked = input[int]() >> pair >> unpack(optional_combine)
assert_type(optional_unpacked, Transformer[[int], str])

multi_input = Transformer(combine) >> str.upper
assert_type(multi_input.sync(1, "x"), str)

curried = input[int]() >> partial(configured, prefix="v")
assert_type(curried, Transformer[[int], str])

generic = input[int]() >> same >> increment
assert_type(generic, Transformer[[int], int])

overloaded = input[int]() >> convert
assert_type(overloaded, Transformer[[int], str])

callable_object = input[int]() >> ToText()
assert_type(callable_object, Transformer[[int], str])

param_spec_stage = input[int]() >> preserve(increment)
assert_type(param_spec_stage, Transformer[[int], int])


@transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


@transformer
def repeat(value: T, *, count: int) -> list[T]:
    return [value] * count


@transformer
def no_configuration(value: int) -> int:
    return value


configured_add = add(amount=2)
assert_type(configured_add(1), int)
assert_type(input[int]() >> configured_add, Transformer[[int], int])
assert_type(input[int]() >> repeat(count=2), Transformer[[int], list[int]])
assert_type(no_configuration()(1), int)


def positive(value: int) -> bool:
    return value > 0


async_mapped = input[list[int]]() >> map(stringify)
assert_type(async_mapped, Transformer[[list[int]], list[str]])

filtered = input[list[int]]() >> filter(positive)
assert_type(filtered, Transformer[[list[int]], list[int]])

pipeline_mapped = input[list[int]]() >> map(input[int]() >> increment >> stringify)
assert_type(pipeline_mapped, Transformer[[list[int]], list[str]])


class Animal:
    pass


class Cat(Animal):
    name = "cat"


def is_cat(value: Animal) -> TypeIs[Cat]:
    return isinstance(value, Cat)


narrowed = input[list[Animal]]() >> filter(is_cat)
assert_type(narrowed, Transformer[[list[Animal]], list[Cat]])


@overload
def mixed_predicate(value: Animal) -> TypeIs[Cat]: ...


@overload
def mixed_predicate(value: int) -> bool: ...


def mixed_predicate(value: Animal | int) -> bool:
    return isinstance(value, Cat) if isinstance(value, Animal) else value > 0


mixed_narrowed = input[list[Animal | int]]() >> filter(
    cast(Callable[[Animal | int], bool], mixed_predicate)
)
assert_type(mixed_narrowed, Transformer[[list[Animal | int]], list[Animal | int]])


def as_label(value: int) -> str:
    return str(value)


def as_parity(value: int) -> str:
    return "even" if value % 2 == 0 else "odd"


dynamic_parallel = input[int]() >> parallel((as_label, as_parity))
assert_type(dynamic_parallel, Transformer[[int], list[str]])

dynamic_sequential = input[int]() >> sequential([as_label, as_parity])
assert_type(dynamic_sequential, Transformer[[int], list[str]])


def choose_text(value: int) -> str:
    return str(value)


def choose_number(value: int) -> int:
    return value


conditional = input[int]() >> condition(
    positive,
    then=choose_text,
    otherwise=choose_number,
)
assert_type(conditional, Transformer[[int], str | int])


def incoming_check(value: int) -> None:
    if value < 0:
        raise ValueError(value)


def outcome_check(value: str) -> None:
    if not value:
        raise ValueError(value)


def changed_check(before: int, after: str) -> None:
    if str(before) != after:
        raise ValueError(after)


@ensure(
    incoming=incoming_check,
    outcome=(outcome_check,),
    changes=[changed_check],
)
def checked(value: int) -> str:
    return str(value)


validated = input[int]() >> checked
assert_type(validated, Transformer[[int], str])


class Service:
    def fetch(self, value: int) -> str:
        return str(value)


bound_method = input[int]() >> Service().fetch
assert_type(bound_method, Transformer[[int], str])


def assert_sync(pipe: Transformer[[int], str]) -> str:
    return pipe.sync(1)


class CustomPipeline(Transformer[[int], object]):
    async def __call__(self, value: int) -> str:
        return str(value)


custom_callable = input[int]() >> CustomPipeline(increment)
assert_type(custom_callable, Transformer[[int], str])


def any_value(value: object) -> None:
    pass


validated_overloads = ensure(incoming=any_value, outcome=any_value)(convert)
assert_type(input[int]() >> validated_overloads, Transformer[[int], str])
assert_type(input[str]() >> validated_overloads, Transformer[[str], int])


def half(value: int) -> float:
    return value / 2


original_example = (
    input() >> add(amount=2) >> (double, half) >> sum >> print  # noqa: F633
)
assert_type(original_example, Transformer[[int], None])


def validate_pair(values: tuple[int, str]) -> None:
    pass


validated_join = ensure(incoming=validate_pair)(unpack(combine))
assert_type(input() >> validated_join, Transformer[[tuple[int, str]], str])
