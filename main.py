from typing import Any, \
    Generic, Iterable, \
    Tuple, TypeVar

from mapper import Mapper
from transformer import Transformer, TransformerHandler, transformer
from transformer_validator import TransformerValidator


class Stringifier(Transformer[int, str]):
    """
    Given a number, return its string representation.
    """

    def transform(self, data: int) -> str:
        return str(data)


T = TypeVar("T")


class Repeater(Generic[T], Transformer[T, Iterable[T]]):
    def __init__(self, count: int = 5):
        super().__init__()
        self.count = count

    def transform(self, data: T) -> Iterable[T]:
        return [data] * self.count


class Joiner(Transformer[Iterable[str], str]):
    def __init__(self, separator: str = ", "):
        super().__init__()
        self.separator = separator

    def transform(self, data: Iterable[str]) -> str:
        return self.separator.join(data)


class TupleJoiner(Transformer[Tuple[str, str, str], str]):
    def __init__(self, separator: str = ", "):
        super().__init__()
        self.separator = separator

    def transform(self, data: Tuple[str, str, str]) -> str:
        return self.separator.join(data)


class Wrapper(Transformer[str, str]):
    """"""

    def __init__(self, left: str = "( ", right: str = " )"):
        super().__init__()
        self.left = left
        self.right = right

    def transform(self, data: str) -> str:
        return self.left + data + self.right


graph_piece = (
    Repeater[str](3) >> (
        Joiner(" * ") >> Repeater(4) >> Joiner(' / '),
        Joiner(" + ") >> Repeater(2) >> Joiner(' | ') >> Wrapper("{ ", " }") >> Wrapper("{ ", " }"),
        Joiner(" - ") >> Repeater(3) >> Joiner(' = ') >> Wrapper("[ ", " ]")
    ) >>
    TupleJoiner(" [|] ") >> (
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]"),
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]"),
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]")
    ) >>
    TupleJoiner(" [|] ") >> (
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]"),
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]"),
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]"),
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]")
    )
)


@transformer
def to_string(number: int) -> str:
    """

    :param number:
    :return:
    """
    return str(number)


@transformer
def times2(number: int) -> int:
    return number * 2


@transformer
def sum_tuple(numbers: tuple[int, int]) -> int:
    return sum(numbers)


@transformer
def join(numbers: Iterable[int]) -> str:
    return ", ".join([str(number) for number in numbers])


class IsEvenValidator(TransformerValidator[int, int]):
    def validate_input(self, input: int):
        if input % 2 != 0:
            raise Exception(f"{input} is odd")

    def validate_output(self, output: int):
        if output % 2 != 0:
            raise Exception(f"{input} is odd")


graph = (
    IsEvenValidator(times2) >>
    Mapper([1, 2, 3, 4, 5], (
        sum_tuple >> times2 >> IsEvenValidator(times2)
    )) >>
    Repeater(3)
)


class LogHandler(TransformerHandler[Any, Any]):
    def handle(self, input_data: Any, output: Any):
        print(f'Logging output: {output}')


if __name__ == "__main__":
    # print(graph_piece('9'))
    result = graph(9)
    # print(result)
    # str(graph)
    print(graph)
