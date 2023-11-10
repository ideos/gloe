from tests.lib.exceptions import NumberIsEven, \
    NumberIsOdd, \
    NumberLessThanOrEquals10, \
    NumbersNotEqual


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

