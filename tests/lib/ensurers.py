from tests.lib.exceptions import NumberIsOdd, NumberLessThanOrEquals10


def is_even(num: int):
    if num % 2 != 0:
        raise NumberIsOdd()


def is_greater_than_10(num: float):
    if num <= 10:
        raise NumberLessThanOrEquals10()

