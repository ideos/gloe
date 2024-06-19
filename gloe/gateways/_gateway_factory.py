from typing import overload, TypeVar, Callable, cast

from typing_extensions import Protocol, TypeAlias

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.transformers import Transformer


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


Tr: TypeAlias = Transformer


class _GatewayFactory(Protocol):
    @overload
    def __call__(
        self, t1: Tr[_I, O1], t2: Tr[_I, O2]
    ) -> Transformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, t1: Tr[_I, O1], t2: Tr[_I, O2], t3: Tr[_I, O3]
    ) -> Transformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, t1: Tr[_I, O1], t2: Tr[_I, O2], t3: Tr[_I, O3], t4: Tr[_I, O4]
    ) -> Transformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self,
        t1: Tr[_I, O1],
        t2: Tr[_I, O2],
        t3: Tr[_I, O3],
        t4: Tr[_I, O4],
        t5: Tr[_I, O5],
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self,
        t1: Tr[_I, O1],
        t2: Tr[_I, O2],
        t3: Tr[_I, O3],
        t4: Tr[_I, O4],
        t5: Tr[_I, O5],
        t6: Tr[_I, O6],
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: Tr[_I, O1],
        t2: Tr[_I, O2],
        t3: Tr[_I, O3],
        t4: Tr[_I, O4],
        t5: Tr[_I, O5],
        t6: Tr[_I, O6],
        t7: Tr[_I, O7],
    ) -> Transformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self, t1: AT[_I, O1], t2: BT[_I, O2]
    ) -> AsyncTransformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, t1: BT[_I, O1], t2: AT[_I, O2]
    ) -> AsyncTransformer[_I, tuple[O1, O2]]:
        pass

    @overload
    def __call__(
        self, t1: AT[_I, O1], t2: BT[_I, O2], t3: BT[_I, O3]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, t1: BT[_I, O1], t2: AT[_I, O2], t3: BT[_I, O3]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, t1: BT[_I, O1], t2: BT[_I, O2], t3: AT[_I, O3]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3]]:
        pass

    @overload
    def __call__(
        self, t1: AT[_I, O1], t2: BT[_I, O2], t3: BT[_I, O3], t4: BT[_I, O4]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, t1: BT[_I, O1], t2: AT[_I, O2], t3: BT[_I, O3], t4: BT[_I, O4]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, t1: BT[_I, O1], t2: BT[_I, O2], t3: AT[_I, O3], t4: BT[_I, O4]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self, t1: BT[_I, O1], t2: BT[_I, O2], t3: BT[_I, O3], t4: AT[_I, O4]
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __call__(
        self,
        t1: AT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: AT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: AT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: AT[_I, O4],
        t5: BT[_I, O5],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: AT[_I, O5],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __call__(
        self,
        t1: AT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: AT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: AT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: AT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: AT[_I, O5],
        t6: BT[_I, O6],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: AT[_I, O6],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __call__(
        self,
        t1: AT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
        t7: BT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: AT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
        t7: BT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: AT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
        t7: BT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: AT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
        t7: BT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: AT[_I, O5],
        t6: BT[_I, O6],
        t7: BT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: AT[_I, O6],
        t7: BT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    @overload
    def __call__(
        self,
        t1: BT[_I, O1],
        t2: BT[_I, O2],
        t3: BT[_I, O3],
        t4: BT[_I, O4],
        t5: BT[_I, O5],
        t6: BT[_I, O6],
        t7: AT[_I, O7],
    ) -> AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    def __call__(self, *args):  # pragma: no cover
        pass


def _gateway_factory(func: Callable) -> _GatewayFactory:
    return cast(_GatewayFactory, func)
