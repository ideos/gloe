from typing import overload, TypeVar, Callable, cast, Awaitable

from typing_extensions import Protocol, TypeAlias as Ta, Unpack

from gloe.transformers import Transformer

_I = TypeVar("_I")
Tr: Ta = Transformer

O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")

T2: Ta = tuple[Tr[_I, O1], Tr[_I, O2]]
T3: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3]]
T4: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4]]
T5: Ta = tuple[Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4], Tr[_I, O5]]
T6: Ta = tuple[
    Tr[_I, O1], Tr[_I, O2], Tr[_I, O3], Tr[_I, O4], Tr[_I, O5], Tr[_I, O6]
]
T7: Ta = tuple[
    Tr[_I, O1],
    Tr[_I, O2],
    Tr[_I, O3],
    Tr[_I, O4],
    Tr[_I, O5],
    Tr[_I, O6],
    Tr[_I, O7],
]


class _GatewayFactory(Protocol):
    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, *args: Unpack[tuple[Tr[_I, Awaitable[O1]], Tr[_I, O2]]]
    ) -> Transformer[_I, Awaitable[tuple[O1, O2]]]:
        pass

    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, *args: Unpack[tuple[Tr[_I, O1], Tr[_I, Awaitable[O2]]]]
    ) -> Transformer[_I, Awaitable[tuple[O1, O2]]]:
        pass

    @overload
    def __call__(  # type: ignore[overload-overlap, overload-cannot-match]
        self,
        *args: Unpack[tuple[Tr[_I, Awaitable[O1]], Tr[_I, Awaitable[O2]]]],
    ) -> Transformer[_I, Awaitable[tuple[O1, O2]]]:
        pass

    @overload
    def __call__(  # type: ignore[overload-overlap]
        self, *args: Unpack[T2[_I, O1, O2]]
    ) -> Transformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T3[_I, O1, O2, O3]]
    ) -> Transformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T4[_I, O1, O2, O3, O4]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T5[_I, O1, O2, O3, O4, O5]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T6[_I, O1, O2, O3, O4, O5, O6]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self, *args: Unpack[T7[_I, O1, O2, O3, O4, O5, O6, O7]]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    def __call__(self, *args):  # pragma: no cover
        pass


def _gateway_factory(func: Callable) -> _GatewayFactory:
    return cast(_GatewayFactory, func)
