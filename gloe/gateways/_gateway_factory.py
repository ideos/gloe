from typing import overload, TypeVar, Callable, cast

from typing_extensions import Protocol, TypeAlias as Ta, Unpack

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.transformers import Transformer


_I = TypeVar("_I")
_O = TypeVar("_O", covariant=True)

AT: Ta = AsyncTransformer
BT: Ta = BaseTransformer[_I, _O]

O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")


Tr: Ta = Transformer

T2: Ta = tuple[Tr[_I, O1], Tr[_I, O2]]
T2A1: Ta = tuple[AT[_I, O1], BT[_I, O2]]
T2A2: Ta = tuple[BT[_I, O1], AT[_I, O2]]

T3: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3]]
T3A1: Ta = tuple[AT[_I, O1], BT[_I, O2], BT[_I, O3]]
T3A2: Ta = tuple[BT[_I, O1], AT[_I, O2], BT[_I, O3]]
T3A3: Ta = tuple[BT[_I, O1], BT[_I, O2], AT[_I, O3]]

T4: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4]]
T4A1: Ta = tuple[AT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4]]
T4A2: Ta = tuple[BT[_I, O1], AT[_I, O2], BT[_I, O3], BT[_I, O4]]
T4A3: Ta = tuple[BT[_I, O1], BT[_I, O2], AT[_I, O3], BT[_I, O4]]
T4A4: Ta = tuple[BT[_I, O1], BT[_I, O2], BT[_I, O3], AT[_I, O4]]

T5: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4], Tr[_I, O5]]
T5A1: Ta = tuple[AT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5]]
T5A2: Ta = tuple[BT[_I, O1], AT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5]]
T5A3: Ta = tuple[BT[_I, O1], BT[_I, O2], AT[_I, O3], BT[_I, O4], BT[_I, O5]]
T5A4: Ta = tuple[BT[_I, O1], BT[_I, O2], BT[_I, O3], AT[_I, O4], BT[_I, O5]]
T5A5: Ta = tuple[BT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], AT[_I, O5]]

T6: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4], Tr[_I, O5], Tr[_I, O6]]
T6A1: Ta = tuple[AT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6]]
T6A2: Ta = tuple[BT[_I, O1], AT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6]]
T6A3: Ta = tuple[BT[_I, O1], BT[_I, O2], AT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6]]
T6A4: Ta = tuple[BT[_I, O1], BT[_I, O2], BT[_I, O3], AT[_I, O4], BT[_I, O5], BT[_I, O6]]
T6A5: Ta = tuple[BT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], AT[_I, O5], BT[_I, O6]]
T6A6: Ta = tuple[BT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], AT[_I, O6]]

T7: Ta = tuple[
    Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4], Tr[_I, O5], Tr[_I, O6], Tr[_I, O7]
]
T7A1: Ta = tuple[
    AT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6], BT[_I, O7]
]
T7A2: Ta = tuple[
    BT[_I, O1], AT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6], BT[_I, O7]
]
T7A3: Ta = tuple[
    BT[_I, O1], BT[_I, O2], AT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6], BT[_I, O7]
]
T7A4: Ta = tuple[
    BT[_I, O1], BT[_I, O2], BT[_I, O3], AT[_I, O4], BT[_I, O5], BT[_I, O6], BT[_I, O7]
]
T7A5: Ta = tuple[
    BT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], AT[_I, O5], BT[_I, O6], BT[_I, O7]
]
T7A6: Ta = tuple[
    BT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], AT[_I, O6], BT[_I, O7]
]
T7A7: Ta = tuple[
    BT[_I, O1], BT[_I, O2], BT[_I, O3], BT[_I, O4], BT[_I, O5], BT[_I, O6], AT[_I, O7]
]


class _GatewayFactory(Protocol):
    @overload
    def __call__(self, *args: Unpack[T2[_I, O1, O2]]) -> Transformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T2A1[_I, O1, O2]]
    ) -> AsyncTransformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T2A2[_I, O1, O2]]
    ) -> AsyncTransformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T3[_I, O1, O2, O3]]
    ) -> Transformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T3A1[_I, O1, O2, O3]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T3A2[_I, O1, O2, O3]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T3A3[_I, O1, O2, O3]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T4[_I, O1, O2, O3, O4]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T4A1[_I, O1, O2, O3, O4]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T4A2[_I, O1, O2, O3, O4]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T4A3[_I, O1, O2, O3, O4]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T4A4[_I, O1, O2, O3, O4]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5[_I, O1, O2, O3, O4, O5]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5A1[_I, O1, O2, O3, O4, O5]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5A2[_I, O1, O2, O3, O4, O5]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5A3[_I, O1, O2, O3, O4, O5]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5A4[_I, O1, O2, O3, O4, O5]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5A5[_I, O1, O2, O3, O4, O5]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6[_I, O1, O2, O3, O4, O5, O6]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6A1[_I, O1, O2, O3, O4, O5, O6]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6A2[_I, O1, O2, O3, O4, O5, O6]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6A3[_I, O1, O2, O3, O4, O5, O6]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6A4[_I, O1, O2, O3, O4, O5, O6]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6A5[_I, O1, O2, O3, O4, O5, O6]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6A6[_I, O1, O2, O3, O4, O5, O6]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A1[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A2[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A3[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A4[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A5[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A6[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7A7[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    def __call__(self, *args):  # pragma: no cover
        pass


def _gateway_factory(func: Callable) -> _GatewayFactory:
    return cast(_GatewayFactory, func)
