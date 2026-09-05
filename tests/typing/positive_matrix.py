"""Execute and type-check the same boundary and composition contracts."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Generator, Iterable
from functools import partial
from typing import (
    Literal,
    NewType,
    Protocol,
    TypeGuard,
    TypedDict,
    assert_type,
    overload,
)

import gloe


def increment(value: int) -> int:
    return value + 1


async def text(value: int) -> str:
    return str(value)


def constant() -> int:
    return 7


async def async_constant() -> int:
    return 8


def arguments(first: int, /, second: str = "x", *, suffix: str = "!") -> str:
    return f"{first}:{second}{suffix}"


def variadic(first: int, *rest: int, **options: int) -> int:
    return first + sum(rest) + sum(options.values())


@gloe.transformer
async def configured(first: int, /, second: str = "x", *, suffix: str) -> str:
    return arguments(first, second, suffix=suffix)


@gloe.transformer
def convert[T, R](value: T, *, function: Callable[[T], R]) -> R:
    return function(value)


@gloe.transformer
def repeat[T](value: T, *, count: int) -> list[T]:
    return [value] * count


def identity[T](value: T) -> T:
    return value


def constrained[T: (str, bytes)](value: T) -> T:
    return value


class Named(Protocol):
    @property
    def name(self) -> str: ...


class Person:
    name = "Ada"


def name(value: Named) -> str:
    return value.name


UserId = NewType("UserId", int)


class Row(TypedDict):
    id: UserId
    name: str


def row(value: UserId) -> Row:
    return {"id": value, "name": "Ada"}


def row_name(value: Row) -> str:
    return value["name"]


def choose(value: Literal["a", "b"]) -> int:
    return 1 if value == "a" else 2


class AsyncCall:
    async def __call__(self, value: int) -> str:
        return str(value)


class GenericCall:
    def __call__[T](self, value: T) -> list[T]:
        return [value]


class Service:
    async def render(self, value: int, *, suffix: str) -> str:
        return f"{value}{suffix}"


class Ready(Awaitable[int]):
    def __await__(self) -> Generator[None, None, int]:
        yield from ()
        return 9


def deferred(value: int) -> Ready:
    return Ready()


def task(value: int) -> asyncio.Task[str]:
    return asyncio.create_task(text(value))


async def nested(value: int) -> Awaitable[str]:
    return text(value)


def even(value: int) -> bool:
    return value % 2 == 0


async def positive(value: int) -> bool:
    return value > 0


def absent(value: int) -> None:
    return None


def is_text(value: object) -> TypeGuard[str]:
    return isinstance(value, str)


def fallback(value: object) -> str:
    return "?"


def string_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)


type IntFunction = Callable[[int], int]
type JSON = None | bool | int | str | list[JSON] | dict[str, JSON]


@overload
def join(first: int, second: int) -> int: ...


@overload
def join(first: str, second: str) -> str: ...


def join(first: int | str, second: int | str) -> int | str:
    if isinstance(first, int) and isinstance(second, int):
        return first + second
    return str(first) + str(second)


def check(value: object) -> None:
    pass


@overload
def formatted(value: int, *, label: str) -> str: ...


@overload
def formatted(value: str, *, label: str) -> int: ...


@overload
def formatted(value: bytes, *, label: str) -> bytes: ...


def formatted(value: int | str | bytes, *, label: str) -> str | int | bytes:
    if isinstance(value, int):
        return f"{label}:{value}"
    return len(value) if isinstance(value, str) else value


@overload
def mode(value: int, *, kind: Literal["text"]) -> str: ...


@overload
def mode(value: int, *, kind: Literal["raw"]) -> int: ...


def mode(value: int, *, kind: str) -> str | int:
    return str(value) if kind == "text" else value


async def roots() -> None:
    formatted_stage = gloe.transformer(formatted)(label="v")
    assert_type(gloe.input[int]() >> formatted_stage, gloe.Transformer[[int], str])
    assert_type(gloe.input[str]() >> formatted_stage, gloe.Transformer[[str], int])
    assert_type(
        gloe.input[bytes]() >> formatted_stage, gloe.Transformer[[bytes], bytes]
    )
    assert await (gloe.input[int]() >> formatted_stage)(2) == "v:2"
    assert await (gloe.input[str]() >> formatted_stage)("abc") == 3
    assert await (gloe.input[bytes]() >> formatted_stage)(b"abc") == b"abc"
    mode_factory = gloe.transformer(mode)
    assert_type(
        gloe.input[int]() >> mode_factory(kind="text"), gloe.Transformer[[int], str]
    )
    assert_type(
        gloe.input[int]() >> mode_factory(kind="raw"), gloe.Transformer[[int], int]
    )
    assert await (gloe.input[int]() >> mode_factory(kind="text"))(1) == "1"
    assert await (gloe.input[int]() >> mode_factory(kind="raw"))(1) == 1
    zero = gloe.Transformer(constant) >> text
    async_zero = gloe.Transformer(async_constant) >> increment
    assert_type(zero, gloe.Transformer[[], str])
    assert_type(async_zero, gloe.Transformer[[], int])
    assert_type(await zero(), str)
    assert await zero() == "7"
    assert await async_zero() == 9

    multi = gloe.Transformer(arguments) >> str.upper
    assert_type(await multi(1), str)
    assert await multi(1, second="z", suffix="?") == "1:Z?"
    assert await (gloe.Transformer(variadic) >> increment)(1, 2, 3, extra=4) == 11
    assert_type(gloe.input[int]() >> variadic, gloe.Transformer[[int], int])

    bound = configured(suffix="?")
    assert_type(gloe.input[int]() >> bound, gloe.Transformer[[int], str])
    assert await (gloe.input[int]() >> bound)(2) == "2:x?"
    assert await gloe.Transformer(bound)(2, "y") == "2:y?"
    assert (
        await (gloe.input[tuple[int, str]]() >> gloe.unpack(bound))((2, "y")) == "2:y?"
    )

    factory = gloe.transformer(Service().render)(suffix="!")
    partial_stage = partial(Service().render, suffix="?")
    assert_type(gloe.input() >> factory, gloe.Transformer[[int], str])
    assert_type(gloe.input() >> partial_stage, gloe.Transformer[[int], str])
    assert await (gloe.input() >> factory)(2) == "2!"
    assert await (gloe.input() >> partial_stage)(2) == "2?"
    partial_root = gloe.Transformer(partial_stage)
    assert_type(await partial_root(2), str)
    assert await partial_root(2, suffix="!") == "2!"
    partial_map = gloe.input() >> gloe.map(partial_stage)
    assert_type(partial_map, gloe.Transformer[[Iterable[int]], list[str]])
    assert await partial_map([1, 2]) == ["1?", "2?"]
    generic_partial = partial(identity)
    assert_type(gloe.input[int]() >> generic_partial, gloe.Transformer[[int], int])
    assert await (gloe.input[int]() >> generic_partial)(1) == 1


async def topology() -> None:
    wide = gloe.input[int]() >> (
        increment,
        text,
        increment,
        text,
        increment,
        text,
        increment,
        text,
    )
    assert_type(
        wide, gloe.Transformer[[int], tuple[int, str, int, str, int, str, int, str]]
    )
    assert await wide(1) == (2, "1", 2, "1", 2, "1", 2, "1")
    empty = gloe.input[int]() >> ()
    single = gloe.input[int]() >> (text,)
    assert_type(empty, gloe.Transformer[[int], tuple[()]])
    assert_type(single, gloe.Transformer[[int], tuple[str]])
    assert await empty(1) == ()
    assert await single(1) == ("1",)

    prefix = gloe.input() >> increment
    inner = prefix >> (text, gloe.input())
    branch = prefix >> (inner, gloe.input(), text)
    assert_type(branch, gloe.Transformer[[int], tuple[tuple[str, int], int, str]])
    assert await branch(1) == (("3", 3), 2, "2")
    assert_type(prefix >> prefix, gloe.Transformer[[int], int])
    assert await (prefix >> prefix)(1) == 3

    optional = gloe.input() >> gloe.condition(
        even,
        then=text,
        otherwise=gloe.condition(positive, then=increment, otherwise=absent),
    )
    assert_type(optional, gloe.Transformer[[int], str | int | None])
    assert await optional(2) == "2"
    assert await optional(1) == 2
    assert await optional(-1) is None
    broad_predicate = gloe.input[int]() >> gloe.condition(
        bool, then=increment, otherwise=increment
    )
    assert_type(broad_predicate, gloe.Transformer[[int], int])
    assert await broad_predicate(1) == 2
    assert await broad_predicate(0) == 1

    adapter = gloe.unpack(join)
    assert_type(
        gloe.input[tuple[int, int]]() >> adapter,
        gloe.Transformer[[tuple[int, int]], int],
    )
    assert_type(
        gloe.input[tuple[str, str]]() >> adapter,
        gloe.Transformer[[tuple[str, str]], str],
    )
    assert await (gloe.input[tuple[int, int]]() >> adapter)((2, 3)) == 5
    assert await (gloe.input[tuple[str, str]]() >> adapter)(("a", "b")) == "ab"
    assert await (gloe.input[tuple[()]]() >> gloe.unpack(constant))(()) == 7
    defaulted = gloe.unpack(arguments)
    assert await (gloe.input[tuple[int]]() >> defaulted)((1,)) == "1:x!"
    assert await (gloe.input[tuple[int, str]]() >> defaulted)((1, "y")) == "1:y!"


async def values_and_callbacks() -> None:
    def selected(stage: Callable[[int], int] | Callable[[int], str]) -> None:
        assert_type(gloe.input[int]() >> stage, gloe.Transformer[[int], int | str])

    selected(increment)
    recursive = gloe.input[JSON]() >> identity
    assert_type(recursive, gloe.Transformer[[JSON], JSON])
    document: JSON = {"items": [1, None, {"active": True}]}
    assert await recursive(document) is document
    alias: IntFunction = increment
    checked_alias = gloe.ensure(incoming=check)(alias)
    assert_type(gloe.input[int]() >> checked_alias, gloe.Transformer[[int], int])
    assert await (gloe.input[int]() >> checked_alias)(1) == 2
    adapted = convert(function=increment)
    assert_type(gloe.input[int]() >> adapted, gloe.Transformer[[int], int])
    assert await (gloe.input[int]() >> adapted)(2) == 3
    reused = repeat(count=2)
    assert_type(gloe.input[str]() >> reused, gloe.Transformer[[str], list[str]])
    assert await (gloe.input[str]() >> reused)("a") == ["a", "a"]
    assert_type(gloe.input[bytes]() >> constrained, gloe.Transformer[[bytes], bytes])
    assert await (gloe.input[bytes]() >> constrained)(b"a") == b"a"
    assert_type(gloe.input[Person]() >> name, gloe.Transformer[[Person], str])
    assert await (gloe.input[Person]() >> name)(Person()) == "Ada"
    assert_type(
        gloe.input[UserId]() >> row >> row_name, gloe.Transformer[[UserId], str]
    )
    assert await (gloe.input[UserId]() >> row >> row_name)(UserId(1)) == "Ada"
    assert_type(gloe.input() >> choose, gloe.Transformer[[Literal["a", "b"]], int])
    assert await (gloe.input() >> choose)("a") == 1
    assert_type(gloe.input[int]() >> GenericCall(), gloe.Transformer[[int], list[int]])
    assert await (gloe.input[int]() >> GenericCall())(3) == [3]
    # Decorators inspect functions; bind __call__ when adapting an object.
    checked_call = gloe.ensure(incoming=check)(AsyncCall().__call__)
    assert_type(gloe.input[int]() >> checked_call, gloe.Transformer[[int], str])
    assert await (gloe.input[int]() >> checked_call)(3) == "3"
    configured_call = gloe.transformer(AsyncCall().__call__)()
    assert_type(gloe.input[int]() >> configured_call, gloe.Transformer[[int], str])
    assert await (gloe.input[int]() >> configured_call)(3) == "3"
    assert_type(gloe.input() >> AsyncCall(), gloe.Transformer[[int], str])
    assert await (gloe.input() >> AsyncCall())(3) == "3"

    assert_type(gloe.input[int]() >> deferred, gloe.Transformer[[int], int])
    assert_type(gloe.input[int]() >> task, gloe.Transformer[[int], str])
    assert_type(gloe.input[int]() >> nested, gloe.Transformer[[int], Awaitable[str]])
    assert await (gloe.input[int]() >> deferred)(1) == 9
    assert await (gloe.input[int]() >> task)(1) == "1"
    pending = await (gloe.input[int]() >> nested)(1)
    assert_type(pending, Awaitable[str])
    assert await pending == "1"
    pending = text(1)
    data = gloe.input[Awaitable[str]]()
    assert_type(await data(pending), Awaitable[str])
    assert await data(pending) is pending
    assert await pending == "1"

    mapped = gloe.input[Iterable[int]]() >> gloe.map(identity)
    assert_type(mapped, gloe.Transformer[[Iterable[int]], list[int]])
    assert await mapped(iter([1, 2])) == [1, 2]
    filtered = gloe.input[Iterable[object]]() >> gloe.filter(is_text)
    assert_type(filtered, gloe.Transformer[[Iterable[object]], list[str]])
    assert await filtered(iter([1, "a", None])) == ["a"]
    # list is invariant, so this guard's target is not a subtype of the
    # declared item. The conservative contract retains that source item type.
    invariant_guard = gloe.input[list[list[object]]]() >> gloe.filter(string_list)
    assert_type(
        invariant_guard, gloe.Transformer[[list[list[object]]], list[list[object]]]
    )
    assert await invariant_guard([["a"], [1]]) == [["a"]]
    narrowed = gloe.input[object]() >> gloe.condition(
        is_text, then=str.upper, otherwise=fallback
    )
    assert_type(narrowed, gloe.Transformer[[object], str])
    assert await narrowed("a") == "A"
    assert await narrowed(1) == "?"
    async_filtered = gloe.input() >> gloe.filter(positive)
    assert_type(async_filtered, gloe.Transformer[[Iterable[int]], list[int]])
    assert await async_filtered(iter([-1, 1])) == [1]
    # A broad predicate annotation supplies a broad collection item contract.
    # Use a domain-typed predicate (such as positive) to retain int precision.
    broad_filter = gloe.input[list[int]]() >> gloe.filter(bool)
    assert_type(broad_filter, gloe.Transformer[[list[int]], list[object]])
    assert await broad_filter([0, 1]) == [1]

    branches: list[Callable[[int], str | Awaitable[str]]] = [text, str]
    dynamic = gloe.input[int]() >> gloe.parallel(branches)
    serial = gloe.input[int]() >> gloe.sequential(branches)
    assert_type(dynamic, gloe.Transformer[[int], list[str]])
    assert_type(serial, gloe.Transformer[[int], list[str]])
    assert await dynamic(1) == ["1", "1"]
    assert await serial(1) == ["1", "1"]
    empty_branches: list[Callable[[int], str]] = []
    assert await (gloe.input[int]() >> gloe.parallel(empty_branches))(1) == []

    ensured = gloe.ensure(incoming=check, outcome=check)(
        gloe.transformer(Service().render)(suffix="!")
    )
    assert_type(gloe.input[int]() >> ensured, gloe.Transformer[[int], str])
    assert await (gloe.input[int]() >> ensured)(2) == "2!"
