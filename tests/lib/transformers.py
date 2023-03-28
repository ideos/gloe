import math
from typing import Tuple

from transformer import transformer


@transformer
def square(num: float) -> float:
    return num * num


@transformer
def square_root(num: float) -> float:
    return math.sqrt(num)


@transformer
def sum1(num: float) -> float:
    return num + 1


@transformer
def sum_tuple2(num: Tuple[float, float]) -> float:
    return num[0] + num[1]


@transformer
def sum_tuple3(num: Tuple[float, float, float]) -> float:
    num1, num2, num3 = num
    return num1 + num2 + num3
