import math
from transformer import transformer


@transformer
def square(num: float) -> float:
    return num * num


@transformer
def square_root(num: float) -> float:
    return math.sqrt(num)


@transformer
def sum_tuple2(num: (float, float)) -> float:
    return num[0] + num[1]


@transformer
def sum_tuple3(num: (float, float, float)) -> float:
    return num[0] + num[1]
