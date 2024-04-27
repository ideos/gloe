from typing import TypeVar, Union
from typing_extensions import TypeAlias

from gloe.base_transformer import BaseTransformer
from gloe.async_transformer import AsyncTransformer

_I = TypeVar("_I")
_O = TypeVar("_O", covariant=True)

AT: TypeAlias = AsyncTransformer
BT: TypeAlias = BaseTransformer[_I, _O]

O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")


AsyncNext2 = Union[
    tuple[AT[_O, O1], BT[_O, O2]],
    tuple[BT[_O, O1], AT[_O, O2]],
]

AsyncNext3 = Union[
    tuple[AT[_O, O1], BT[_O, O2], BT[_O, O3]],
    tuple[BT[_O, O1], AT[_O, O2], BT[_O, O3]],
    tuple[BT[_O, O1], BT[_O, O2], AT[_O, O3]],
]

AsyncNext4 = Union[
    tuple[AT[_O, O1], BT[_O, O2], BT[_O, O3], BT[_O, O4]],
    tuple[BT[_O, O1], AT[_O, O2], BT[_O, O3], BT[_O, O4]],
    tuple[BT[_O, O1], BT[_O, O2], AT[_O, O3], BT[_O, O4]],
    tuple[BT[_O, O1], BT[_O, O2], BT[_O, O3], AT[_O, O4]],
]

AsyncNext5 = Union[
    tuple[AT[_O, O1], BT[_O, O2], BT[_O, O3], BT[_O, O4], BT[_O, O5]],
    tuple[BT[_O, O1], AT[_O, O2], BT[_O, O3], BT[_O, O4], BT[_O, O5]],
    tuple[BT[_O, O1], BT[_O, O2], AT[_O, O3], BT[_O, O4], BT[_O, O5]],
    tuple[BT[_O, O1], BT[_O, O2], BT[_O, O3], AT[_O, O4], BT[_O, O5]],
    tuple[BT[_O, O1], BT[_O, O2], BT[_O, O3], BT[_O, O4], AT[_O, O5]],
]

AsyncNext6 = Union[
    tuple[AT[_O, O1], BT[_O, O2], BT[_O, O3], BT[_O, O4], BT[_O, O5], BT[_O, O6]],
    tuple[BT[_O, O1], AT[_O, O2], BT[_O, O3], BT[_O, O4], BT[_O, O5], BT[_O, O6]],
    tuple[BT[_O, O1], BT[_O, O2], AT[_O, O3], BT[_O, O4], BT[_O, O5], BT[_O, O6]],
    tuple[BT[_O, O1], BT[_O, O2], BT[_O, O3], AT[_O, O4], BT[_O, O5], BT[_O, O6]],
    tuple[BT[_O, O1], BT[_O, O2], BT[_O, O3], BT[_O, O4], AT[_O, O5], BT[_O, O6]],
    tuple[BT[_O, O1], BT[_O, O2], BT[_O, O3], BT[_O, O4], BT[_O, O5], AT[_O, O6]],
]

AsyncNext7 = Union[
    tuple[
        AT[_O, O1],
        BT[_O, O2],
        BT[_O, O3],
        BT[_O, O4],
        BT[_O, O5],
        BT[_O, O6],
        BT[_O, O7],
    ],
    tuple[
        BT[_O, O1],
        AT[_O, O2],
        BT[_O, O3],
        BT[_O, O4],
        BT[_O, O5],
        BT[_O, O6],
        BT[_O, O7],
    ],
    tuple[
        BT[_O, O1],
        BT[_O, O2],
        AT[_O, O3],
        BT[_O, O4],
        BT[_O, O5],
        BT[_O, O6],
        BT[_O, O7],
    ],
    tuple[
        BT[_O, O1],
        BT[_O, O2],
        BT[_O, O3],
        AT[_O, O4],
        BT[_O, O5],
        BT[_O, O6],
        BT[_O, O7],
    ],
    tuple[
        BT[_O, O1],
        BT[_O, O2],
        BT[_O, O3],
        BT[_O, O4],
        AT[_O, O5],
        BT[_O, O6],
        BT[_O, O7],
    ],
    tuple[
        BT[_O, O1],
        BT[_O, O2],
        BT[_O, O3],
        BT[_O, O4],
        BT[_O, O5],
        AT[_O, O6],
        BT[_O, O7],
    ],
    tuple[
        BT[_O, O1],
        BT[_O, O2],
        BT[_O, O3],
        BT[_O, O4],
        BT[_O, O5],
        BT[_O, O6],
        AT[_O, O7],
    ],
]
