from abc import ABC, abstractmethod
from inspect import Signature

from typing import TypeVar, overload, cast, Iterable

from typing_extensions import Generic, Unpack, TypeVarTuple

from gloe.async_transformer import AsyncTransformer
from gloe._transformer_utils import catch_transformer_exception
from gloe.base_transformer import BaseTransformer, Flow, _NO_ARGS
from gloe.exceptions import TransformerRequiresMultiArgs

from gloe._generic_types import (
    AsyncNext2,
    AsyncNext3,
    AsyncNext4,
    AsyncNext5,
    AsyncNext6,
    AsyncNext7,
)

__all__ = ["Transformer"]

_O = TypeVar("_O", covariant=True)

Item = TypeVar("Item")
O1 = TypeVar("O1")
O2 = TypeVar("O2")
O3 = TypeVar("O3")
O4 = TypeVar("O4")
O5 = TypeVar("O5")
O6 = TypeVar("O6")
O7 = TypeVar("O7")
To = TypeVar("To", bound=BaseTransformer)

Args = TypeVarTuple("Args")
NextArgs = TypeVarTuple("NextArgs")


def _execute_flow(flow: Flow, arg: object) -> object:
    result = arg
    for op in flow:
        if isinstance(op, Transformer):
            result = op._safe_transform(result)
        else:
            raise NotImplementedError()
    return result


class Transformer(BaseTransformer[Unpack[Args], _O], Generic[Unpack[Args], _O], ABC):
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

    @abstractmethod
    def transform(self, *data: Unpack[Args]) -> _O:
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

    def _safe_transform(self, data: object) -> _O:
        try:
            args = cast(tuple[Unpack[Args]], self._unpack_call_args(data))
        except TransformerRequiresMultiArgs as exception:
            raise TypeError(self._param_mismatch_message(data)) from exception
        except TypeError as exception:
            if data is _NO_ARGS:
                raise TypeError(self._param_mismatch_message(data)) from exception
            raise
        try:
            transformed = self.transform(*args)
        except Exception as exception:
            raise catch_transformer_exception(exception, self).internal_exception
        return cast(_O, transformed)

    def __call__(self, *data: Unpack[Args]) -> _O:
        packed = self._pack_call_args(data)
        return cast(_O, _execute_flow(self._flow, packed))

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], tuple[Unpack[NextArgs]]]",
        next_node: "Transformer[Unpack[NextArgs], O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], tuple[Unpack[NextArgs]]]",
        next_node: AsyncTransformer[Unpack[NextArgs], O1],
    ) -> AsyncTransformer[Unpack[Args], O1]:
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], list[Item]]",
        next_node: "Transformer[Iterable[Item], O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], list[Item]]",
        next_node: AsyncTransformer[Iterable[Item], O1],
    ) -> AsyncTransformer[Unpack[Args], O1]:
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], _O]",
        next_node: "Transformer[_O, _O]",
    ) -> "Transformer[Unpack[Args], _O]":
        pass

    @overload
    def __rshift__(
        self, next_node: "Transformer[_O, O1]"
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Transformer[_O, O1]", "Transformer[_O, O2]"],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Transformer[_O, O1]", "Transformer[_O, O2]", "Transformer[_O, O3]"],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_O, O1]",
            "Transformer[_O, O2]",
            "Transformer[_O, O3]",
            "Transformer[_O, O4]",
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_O, O1]",
            "Transformer[_O, O2]",
            "Transformer[_O, O3]",
            "Transformer[_O, O4]",
            "Transformer[_O, O5]",
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4, O5]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_O, O1]",
            "Transformer[_O, O2]",
            "Transformer[_O, O3]",
            "Transformer[_O, O4]",
            "Transformer[_O, O5]",
            "Transformer[_O, O6]",
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4, O5, O6]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_O, O1]",
            "Transformer[_O, O2]",
            "Transformer[_O, O3]",
            "Transformer[_O, O4]",
            "Transformer[_O, O5]",
            "Transformer[_O, O6]",
            "Transformer[_O, O7]",
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4, O5, O6, O7]]":
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncTransformer[_O, O1]
    ) -> AsyncTransformer[Unpack[Args], O1]:
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncNext2[_O, O1, O2]
    ) -> AsyncTransformer[Unpack[Args], tuple[O1, O2]]:
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncNext3[_O, O1, O2, O3]
    ) -> AsyncTransformer[Unpack[Args], tuple[O1, O2, O3]]:
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncNext4[_O, O1, O2, O3, O4]
    ) -> AsyncTransformer[Unpack[Args], tuple[O1, O2, O3, O4]]:
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncNext5[_O, O1, O2, O3, O4, O5]
    ) -> AsyncTransformer[Unpack[Args], tuple[O1, O2, O3, O4, O5]]:
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncNext6[_O, O1, O2, O3, O4, O5, O6]
    ) -> AsyncTransformer[Unpack[Args], tuple[O1, O2, O3, O4, O5, O6]]:
        pass

    @overload
    def __rshift__(
        self, next_node: AsyncNext7[_O, O1, O2, O3, O4, O5, O6, O7]
    ) -> AsyncTransformer[Unpack[Args], tuple[O1, O2, O3, O4, O5, O6, O7]]:
        pass

    def __rshift__(self, next_node):  # pragma: no cover
        pass
