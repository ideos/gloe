from typing import TypeVar, TypeAlias, Any, Union

from gloe._supports_composition import SupportsComposition
from gloe.base_transformer import BaseTransformer
from gloe.async_transformer import AsyncTransformer

I = TypeVar("I")
O = TypeVar("O", covariant=True)

SC: TypeAlias = SupportsComposition
AT: TypeAlias = AsyncTransformer
BT: TypeAlias = BaseTransformer[I, O]
ASC = SupportsComposition[I, AT[I, O]]
BSC = SupportsComposition[I, BT[I, O]]

O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")


AsyncNext2 = Union[
    tuple[ASC[O, O1], BSC[O, O2]],
    tuple[BSC[O, O1], ASC[O, O2]],
]

AsyncNext3 = Union[
    tuple[ASC[O, O1], BSC[O, O2], BSC[O, O3]],
    tuple[BSC[O, O1], ASC[O, O2], BSC[O, O3]],
    tuple[BSC[O, O1], BSC[O, O2], ASC[O, O3]],
]

AsyncNext4 = Union[
    tuple[ASC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4]],
    tuple[BSC[O, O1], ASC[O, O2], BSC[O, O3], BSC[O, O4]],
    tuple[BSC[O, O1], BSC[O, O2], ASC[O, O3], BSC[O, O4]],
    tuple[BSC[O, O1], BSC[O, O2], BSC[O, O3], ASC[O, O4]],
]

AsyncNext5 = Union[
    tuple[ASC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5]],
    tuple[BSC[O, O1], ASC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5]],
    tuple[BSC[O, O1], BSC[O, O2], ASC[O, O3], BSC[O, O4], BSC[O, O5]],
    tuple[BSC[O, O1], BSC[O, O2], BSC[O, O3], ASC[O, O4], BSC[O, O5]],
    tuple[BSC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], ASC[O, O5]],
]

AsyncNext6 = Union[
    tuple[ASC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6]],
    tuple[BSC[O, O1], ASC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6]],
    tuple[BSC[O, O1], BSC[O, O2], ASC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6]],
    tuple[BSC[O, O1], BSC[O, O2], BSC[O, O3], ASC[O, O4], BSC[O, O5], BSC[O, O6]],
    tuple[BSC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], ASC[O, O5], BSC[O, O6]],
    tuple[BSC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], ASC[O, O6]],
]

AsyncNext7 = Union[
    tuple[
        ASC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6], BSC[O, O7]
    ],
    tuple[
        BSC[O, O1], ASC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6], BSC[O, O7]
    ],
    tuple[
        BSC[O, O1], BSC[O, O2], ASC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6], BSC[O, O7]
    ],
    tuple[
        BSC[O, O1], BSC[O, O2], BSC[O, O3], ASC[O, O4], BSC[O, O5], BSC[O, O6], BSC[O, O7]
    ],
    tuple[
        BSC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], ASC[O, O5], BSC[O, O6], BSC[O, O7]
    ],
    tuple[
        BSC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], ASC[O, O6], BSC[O, O7]
    ],
    tuple[
        BSC[O, O1], BSC[O, O2], BSC[O, O3], BSC[O, O4], BSC[O, O5], BSC[O, O6], ASC[O, O7]
    ],
]
