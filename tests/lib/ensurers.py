from typing import Any

from tests.lib.exceptions import (
    NumberIsEven,
    NumberIsOdd,
    NumberLessThanOrEquals10,
    NumbersNotEqual,
    HasNotBarKey,
    IsNotInt,
    HasNotFooKey,
    HasFooKey,
)


def is_even(num: int):
    if num % 2 != 0:
        raise NumberIsOdd()


def is_odd(num: int):
    if num % 2 == 0:
        raise NumberIsEven()


def is_greater_than_10(num: float):
    if num <= 10:
        raise NumberLessThanOrEquals10()


def same_value(data: float, output: float):
    if data != output:
        raise NumbersNotEqual()


def same_value_int(incoming: int, outcome: int):
    if incoming != outcome:
        raise NumbersNotEqual()


def has_bar_key(data: dict[str, str]):
    if "bar" not in data.keys():
        raise HasNotBarKey()


def has_foo_key(data: dict[str, str]):
    if "foo" not in data.keys():
        raise HasNotBarKey()


def is_int(data: Any):
    if type(data) is not int:
        raise IsNotInt()


def is_str(data: Any):
    if type(data) is not str:
        raise Exception("data is not string")


def foo_key_removed(incoming: dict[str, str], outcome: dict[str, str]):
    if "foo" not in incoming.keys():
        raise HasNotFooKey()

    if "foo" in outcome.keys():
        raise HasFooKey()
