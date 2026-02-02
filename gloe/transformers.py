from abc import ABC, abstractmethod
from inspect import Signature

from typing import TYPE_CHECKING, TypeVar, overload, cast, Optional, Any, Literal

from typing_extensions import TypeAlias

from gloe._transformer_utils import catch_transformer_exception
from gloe.base_transformer import BaseTransformer, Flow
from gloe._transformer_types import SyncTransformer

if TYPE_CHECKING:
    from gloe.async_transformer import AsyncTransformer
    from gloe._generic_types import (
        AsyncNext2,
        AsyncNext3,
        AsyncNext4,
        AsyncNext5,
        AsyncNext6,
        AsyncNext7,
    )

__all__ = ["Transformer"]

_I = TypeVar("_I", contravariant=True)
_O = TypeVar("_O", covariant=True)

Tr: TypeAlias = "Transformer"

Item = TypeVar("Item")
O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")
To = TypeVar("To", bound=BaseTransformer)




def _execute_flow(flow: Flow, arg: Any) -> Any:
    from gloe.async_transformer import AsyncTransformer

    result = arg
    for op in flow:
        if isinstance(op, AsyncTransformer):
            raise NotImplementedError()
        if isinstance(op, Transformer):
            result = op._safe_transform(result)
        else:
            raise NotImplementedError()
    return result


class Transformer(BaseTransformer[_I, _O], ABC):
    """
    A Transformer is the generic block with the responsibility to take an input of type
    `T` and transform it to an output of type `S`.

    See Also:
        Read more about this feature in the page :ref:`creating-a-transformer`.

    Example:
        Typical usage example::

            class Stringifier(Transformer[dict, str]):
                ...

    """

    def __init__(self):
        super().__init__()
        self.__class__.__annotations__ = self.transform.__annotations__

    @property
    def is_async(self) -> Literal[False]:
        return False

    @abstractmethod
    def transform(self, data: _I) -> _O:
        """
        Main method to be implemented and responsible to perform the transformer logic
        """

    def signature(self) -> Signature:
        return self._signature(Transformer)

    def __repr__(self):
        if len(self) == 1:
            return (
                f"{self.input_annotation}"
                f" -> ({type(self).__name__})"
                f" -> {self.output_annotation}"
            )

        return (
            f"{self.input_annotation}"
            f" -> ({len(self)} transformers omitted)"
            f" -> {self.output_annotation}"
        )

    def _safe_transform(self, data: _I) -> _O:
        transform_exception = None

        transformed: Optional[_O] = None
        try:
            transformed = self.transform(data)
        except Exception as exception:
            transform_exception = catch_transformer_exception(exception, self)

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return cast(_O, transformed)

        raise NotImplementedError()  # pragma: no cover

    @overload
    def __call__(self: "Transformer[None, _O]") -> _O:
        pass

    @overload
    def __call__(self: "Transformer[_I, _O]", data: _I, /) -> _O:
        pass

    def __call__(self, *data: Any) -> _O:
        if len(data) == 0:
            return _execute_flow(self._flow, None)
        if len(data) == 1:
            return _execute_flow(self._flow, data[0])
        return _execute_flow(self._flow, data)

    @overload
    def __rshift__(
        self, next_node: "AsyncTransformer[_O, O1]"
    ) -> "AsyncTransformer[_I, O1]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncNext2[_O, O1, O2]"
    ) -> "AsyncTransformer[_I, tuple[O1, O2]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncNext3[_O, O1, O2, O3]"
    ) -> "AsyncTransformer[_I, tuple[O1, O2, O3]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncNext4[_O, O1, O2, O3, O4]"
    ) -> "AsyncTransformer[_I, tuple[O1, O2, O3, O4]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncNext5[_O, O1, O2, O3, O4, O5]"
    ) -> "AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncNext6[_O, O1, O2, O3, O4, O5, O6]"
    ) -> "AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncNext7[_O, O1, O2, O3, O4, O5, O6, O7]"
    ) -> "AsyncTransformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "SyncTransformer[_O, O1]"
    ) -> "Transformer[_I, O1]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["SyncTransformer[_O, O1]", "SyncTransformer[_O, O2]"],
    ) -> "Transformer[_I, tuple[O1, O2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "SyncTransformer[_O, O1]",
            "SyncTransformer[_O, O2]",
            "SyncTransformer[_O, O3]",
        ],
    ) -> "Transformer[_I, tuple[O1, O2, O3]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "SyncTransformer[_O, O1]",
            "SyncTransformer[_O, O2]",
            "SyncTransformer[_O, O3]",
            "SyncTransformer[_O, O4]",
        ],
    ) -> "Transformer[_I, tuple[O1, O2, O3, O4]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "SyncTransformer[_O, O1]",
            "SyncTransformer[_O, O2]",
            "SyncTransformer[_O, O3]",
            "SyncTransformer[_O, O4]",
            "SyncTransformer[_O, O5]",
        ],
    ) -> "Transformer[_I, tuple[O1, O2, O3, O4, O5]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "SyncTransformer[_O, O1]",
            "SyncTransformer[_O, O2]",
            "SyncTransformer[_O, O3]",
            "SyncTransformer[_O, O4]",
            "SyncTransformer[_O, O5]",
            "SyncTransformer[_O, O6]",
        ],
    ) -> "Transformer[_I, tuple[O1, O2, O3, O4, O5, O6]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "SyncTransformer[_O, O1]",
            "SyncTransformer[_O, O2]",
            "SyncTransformer[_O, O3]",
            "SyncTransformer[_O, O4]",
            "SyncTransformer[_O, O5]",
            "SyncTransformer[_O, O6]",
            "SyncTransformer[_O, O7]",
        ],
    ) -> "Transformer[_I, tuple[O1, O2, O3, O4, O5, O6, O7]]":
        pass

    def __rshift__(self, next_node):  # pragma: no cover
        pass
