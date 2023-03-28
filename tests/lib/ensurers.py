from tests.lib.exceptions import NumberIsOdd, NumberLessThanOrEquals10
from transformer_ensurer import input_ensurer, output_ensurer


@input_ensurer
def input_is_even(num: int):
    if num % 2 != 0:
        raise NumberIsOdd()


@output_ensurer
def output_is_greater_than_10(num: int):
    if num <= 10:
        raise NumberLessThanOrEquals10()

