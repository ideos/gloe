"""Runnable examples for the public Gloe 0.8 documentation.

From the repository root with Python 3.12+, run:
    python -m docs.source.examples.pipelines
The assertions keep the examples tied to concrete input and output values
while the surrounding Markdown explains the API contract.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import gloe


@gloe.transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


arithmetic = gloe.input[int]() >> add(amount=2) >> str


async def add_exclamation(value: str) -> str:
    await asyncio.sleep(0)
    return f"{value}!"


mixed_async = arithmetic >> add_exclamation


def is_positive(value: int) -> bool:
    return value > 0


async def double(value: int) -> int:
    await asyncio.sleep(0)
    return value * 2


collection = gloe.input[list[int]]() >> gloe.filter(is_positive) >> gloe.map(double)


def prefix(value: int) -> int:
    return value + 1


def work(value: int) -> int:
    return value * 2


def finish(original: int, computed: int) -> tuple[int, int]:
    return original, computed


retained_data = (
    gloe.input[int]() >> prefix >> (gloe.input(), work) >> gloe.unpack(finish)
)


branch_events: list[str] = []


def left(value: int) -> int:
    branch_events.append("left")
    return value * 2


def right(value: int) -> int:
    branch_events.append("right")
    return value - 1


shared_prefix = gloe.input[int]() >> prefix >> (left, right)
pipe2 = gloe.input[int]() >> prefix >> left
pipe3 = gloe.input[int]() >> prefix >> right
repeated_sequence = pipe2 >> pipe3


def is_priority(value: int) -> bool:
    return value > 0


def choose_priority(value: int) -> str:
    return f"priority:{value}"


def choose_standard(value: int) -> str:
    return f"standard:{value}"


conditional = gloe.input[int]() >> gloe.condition(
    is_priority,
    then=choose_priority,
    otherwise=choose_standard,
)


async def plus_one(value: int) -> int:
    await asyncio.sleep(0)
    return value + 1


def plus_two(value: int) -> int:
    return value + 2


dynamic_parallel = gloe.input[int]() >> gloe.parallel((plus_one, plus_two))
dynamic_sequential = gloe.input[int]() >> gloe.sequential((plus_one, plus_two))


def multiply(value: int, factor: int) -> int:
    return value * factor


@gloe.transformer
def map_over(
    value: int,
    *,
    items: tuple[int, ...],
    combine: Callable[[int, int], int],
) -> list[int]:
    return [combine(value, item) for item in items]


map_over_pipeline = gloe.input[int]() >> map_over(items=(2, 3, 4), combine=multiply)


def reduce_values(values: list[int], reducer: Callable[[int, int], int]) -> int:
    result = 0
    for value in values:
        result = reducer(result, value)
    return result


def sum_values(values: list[int]) -> int:
    return reduce_values(values, lambda total, value: total + value)


reduce_pipeline = gloe.input[list[int]]() >> sum_values


def nonnegative(value: int) -> None:
    if value < 0:
        raise ValueError("value must be nonnegative")


def increased(before: int, after: int) -> None:
    if after <= before:
        raise ValueError("value did not increase")


@gloe.ensure(incoming=nonnegative, changes=increased)
def checked_increment(value: int) -> int:
    return value + 1


validated = gloe.input[int]() >> checked_increment


async def main() -> None:
    assert await arithmetic(3) == "5"
    assert await mixed_async(3) == "5!"
    assert await collection([-2, 0, 2, 3]) == [4, 6]
    assert await retained_data(2) == (3, 6)

    branch_events.clear()
    assert await shared_prefix(3) == (8, 3)
    assert branch_events == ["left", "right"]

    branch_events.clear()
    assert await repeated_sequence(3) == 8
    assert branch_events == ["left", "right"]

    assert await conditional(2) == "priority:2"
    assert await conditional(-2) == "standard:-2"
    assert await dynamic_parallel(3) == [4, 5]
    assert await dynamic_sequential(3) == [4, 5]
    assert await map_over_pipeline(5) == [10, 15, 20]
    assert await reduce_pipeline([1, 2, 3, 4]) == 10
    assert await validated(2) == 3

    try:
        await validated(-1)
    except ValueError as error:
        assert str(error) == "value must be nonnegative"
    else:
        raise AssertionError("incoming validation did not reject -1")


if __name__ == "__main__":
    asyncio.run(main())
    assert arithmetic.sync(4) == "6"
