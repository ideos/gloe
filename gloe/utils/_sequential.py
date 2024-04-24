from typing import TypeVar, overload, TypeAlias
from gloe.transformers import Transformer

_In = TypeVar("_In")

O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")


Trf: TypeAlias = Transformer


@overload
def sequential(
    trf1: Trf[_In, O1], trf2: Trf[_In, O2]
) -> Transformer[_In, tuple[O1, O2]]:
    pass


@overload
def sequential(
    trf1: Trf[_In, O1], trf2: Trf[_In, O2], trf3: Trf[_In, O3]
) -> Transformer[_In, tuple[O1, O2, O3]]:
    pass


@overload
def sequential(
    trf1: Trf[_In, O1], trf2: Trf[_In, O2], trf3: Trf[_In, O3], trf4: Trf[_In, O4]
) -> Transformer[_In, tuple[O1, O2, O3, O4]]:
    pass


@overload
def sequential(
    trf1: Trf[_In, O1],
    trf2: Trf[_In, O2],
    trf3: Trf[_In, O3],
    trf4: Trf[_In, O4],
    trf5: Trf[_In, O5],
) -> Transformer[_In, tuple[O1, O2, O3, O4, O5]]:
    pass


@overload
def sequential(
    trf1: Trf[_In, O1],
    trf2: Trf[_In, O2],
    trf3: Trf[_In, O3],
    trf4: Trf[_In, O4],
    trf5: Trf[_In, O5],
    trf6: Trf[_In, O6],
) -> Transformer[_In, tuple[O1, O2, O3, O4, O5, O6]]:
    pass


@overload
def sequential(
    trf1: Trf[_In, O1],
    trf2: Trf[_In, O2],
    trf3: Trf[_In, O3],
    trf4: Trf[_In, O4],
    trf5: Trf[_In, O5],
    trf6: Trf[_In, O6],
    trf7: Trf[_In, O7],
) -> Transformer[_In, tuple[O1, O2, O3, O4, O5, O6, O7]]:
    pass


def sequential(*args):
    class Sequential(Transformer):
        def __init__(self):
            super().__init__()
            self._plotting_settings.has_children = True

        def transform(self, data) -> list:
            output = []
            for trf in args:
                output.append(trf(data))
            return output

    return Sequential()
