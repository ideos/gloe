import math
from typing import Tuple

from tests.lib.exceptions import LnOfNegativeNumber
from src.gloe import transformer


@transformer
def square(num: float) -> float:
    return num * num


@transformer
def square_root(num: float) -> float:
    return math.sqrt(num)


@transformer
def sum1(num: float) -> float:
    """
    Sum 1 to the number
    """
    return float(num + 1)


@transformer
def minus1(num: float) -> float:
    return num - 1


@transformer
def sum_tuple2(num: Tuple[float, float]) -> float:
    return num[0] + num[1]


@transformer
def sum_tuple3(num: Tuple[float, float, float]) -> float:
    num1, num2, num3 = num
    return num1 + num2 + num3


@transformer
def to_string(num: float) -> str:
    return str(num)


@transformer
def natural_logarithm(num: float) -> float:
    if num < 0:
        raise LnOfNegativeNumber(num)
    else:
        return math.log(num, math.e)


@transformer
def logarithm(base: float, arg: float) -> float:
    return math.log(arg) / math.log(base)

@transformer
def repeat(n_times: int, linebreak: bool, content: str) -> str:
    repeated = content * n_times
    if linebreak:
        repeated += '\n'
    return repeated
