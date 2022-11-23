from typing import Any, \
    Iterable, \
    Tuple

from transformer import Transformer, TransformerHandler, transformer


class Stringifier(Transformer[int, str]):
    """
    Given a number, return its string representation.
    """

    def transform(self, data: int) -> str:
        return str(data)


class Repeater(Transformer[str, Iterable[str]]):
    def __init__(self, count: int = 5):
        super().__init__()
        self.count = count

    def transform(self, data: str) -> Iterable[str]:
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
    Repeater(3) >> (
        Joiner(" * ") >> Repeater(4) >> Joiner(' / '),
        Joiner(" + ") >> Repeater(2) >> Joiner(' | ') >> Wrapper("{ ", " }") >> Wrapper("{ ", " }"),
        Joiner(" - ") >> Repeater(3) >> Joiner(' = ') >> Wrapper("[ ", " ]")
    ) >>
    TupleJoiner(" [|] ") >> (
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]") >> Wrapper("[ ", " ]"),
        Wrapper("[ ", " ]") >> Wrapper("[ ", " ]")
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


graph = (
    to_string >>
    graph_piece
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
