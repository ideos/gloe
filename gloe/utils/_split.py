from typing import TypeVar, overload, TypeAlias
from gloe.transformers import Transformer

_In = TypeVar("_In")

I1 = TypeVar("I1")
I2 = TypeVar("I2")
I3 = TypeVar("I3")
I4 = TypeVar("I4")
I5 = TypeVar("I5")
I6 = TypeVar("I6")
I7 = TypeVar("I7")

O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")


Trf: TypeAlias = Transformer


@overload
def split(
    trf1: Trf[I1, O1], trf2: Trf[I2, O2]
) -> Transformer[tuple[I1, I2], tuple[O1, O2]]:
    pass


@overload
def split(
    trf1: Trf[I1, O1], trf2: Trf[I2, O2], trf3: Trf[I3, O3]
) -> Transformer[tuple[I1, I2, I3], tuple[O1, O2, O3]]:
    pass


@overload
def split(
    trf1: Trf[I1, O1], trf2: Trf[I2, O2], trf3: Trf[I3, O3], trf4: Trf[I4, O4]
) -> Transformer[tuple[I1, I2, I3, I4], tuple[O1, O2, O3, O4]]:
    pass


@overload
def split(
    trf1: Trf[I1, O1],
    trf2: Trf[I2, O2],
    trf3: Trf[I3, O3],
    trf4: Trf[I4, O4],
    trf5: Trf[I5, O5],
) -> Transformer[tuple[I1, I2, I3, I4, I5], tuple[O1, O2, O3, O4, O5]]:
    pass


@overload
def split(
    trf1: Trf[I1, O1],
    trf2: Trf[I2, O2],
    trf3: Trf[I3, O3],
    trf4: Trf[I4, O4],
    trf5: Trf[I5, O5],
    trf6: Trf[I6, O6],
) -> Transformer[tuple[I1, I2, I3, I4, I5, I6], tuple[O1, O2, O3, O4, O5, O6]]:
    pass


@overload
def split(
    trf1: Trf[I1, O1],
    trf2: Trf[I2, O2],
    trf3: Trf[I3, O3],
    trf4: Trf[I4, O4],
    trf5: Trf[I5, O5],
    trf6: Trf[I6, O6],
    trf7: Trf[I7, O7],
) -> Transformer[tuple[I1, I2, I3, I4, I5, I6, I7], tuple[O1, O2, O3, O4, O5, O6, O7]]:
    pass


def split(*args):
    class Split(Transformer):
        def __init__(self):
            super().__init__()
            self._plotting_settings.has_children = True

        def transform(self, data_tup) -> tuple:
            output = []
            for trf, data in zip(args, data_tup):
                output.append(trf(data))
            return tuple(output)

    return Split()
