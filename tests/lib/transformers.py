import asyncio
import math

from tests.lib.exceptions import LnOfNegativeNumber
from gloe import transformer, partial_transformer, async_transformer


@transformer
def square_root(num: float) -> float:
    return math.sqrt(num)


@transformer
def plus1(num: float) -> float:
    """
    Sum 1 to the number
    """
    return num + 1


@async_transformer
async def async_plus1(num: float) -> float:
    await asyncio.sleep(0.00001)
    return num + 1


@async_transformer
async def async_minus1(num: float) -> float:
    await asyncio.sleep(0.00001)
    return num - 1


@transformer
def square(num: float) -> float:
    return num * num


@transformer
def minus1(num: float) -> float:
    return num - 1


@transformer
def times2(num: float) -> float:
    return num * 2


@transformer
def divide_by_2(num: float) -> float:
    return num / 2


@transformer
def sum_tuple2(num: tuple[float, float]) -> float:
    return num[0] + num[1]


@async_transformer
async def async_sum_tuple2(num: tuple[float, float]) -> float:
    await asyncio.sleep(0.01)
    return num[0] + num[1]


@transformer
def mul_tuple2(num: tuple[float, float]) -> float:
    return num[0] * num[1]


@transformer
def sum_tuple3(num: tuple[float, float, float]) -> float:
    num1, num2, num3 = num
    return num1 + num2 + num3


@transformer
def to_string(num: float) -> str:
    return str(num)


@transformer
def tuple_concatenate(strs: tuple[str, float]) -> str:
    return strs[0] + str(strs[1])


@transformer
def duplicate(string: str) -> str:
    return string + string


@transformer
def natural_logarithm(num: float) -> float:
    if num < 0:
        raise LnOfNegativeNumber(num)
    else:
        return math.log(num, math.e)


@async_transformer
async def async_natural_logarithm(num: float) -> float:
    await asyncio.sleep(0.00001)
    if num < 0:
        raise LnOfNegativeNumber(num)
    else:
        return math.log(num, math.e)


@partial_transformer
def logarithm(arg: float, base: float) -> float:
    return math.log(arg) / math.log(base)


@partial_transformer
def format_currency(number: float, thousands_separator: str) -> str:
    return f"{number}:{thousands_separator}.2f"


@transformer
def check_is_even(number: float) -> bool:
    return number % 2 == 0


@partial_transformer
def repeat(content: str, n_times: int, linebreak: bool) -> str:
    repeated = content * n_times
    if linebreak:
        repeated += "\n"
    return repeated


@partial_transformer
def repeat_list(content: float, n_times: int) -> list[float]:
    return [content] * n_times


@transformer
def identity(num: float) -> float:
    return num
