from abc import ABC, abstractmethod
from inspect import Signature, isawaitable

from typing import (
    TypeVar,
    overload,
    cast,
    Optional,
    Any,
    get_args,
    get_origin,
    Iterable,
    Awaitable,
    Protocol,
)

from typing_extensions import Generic, TypeAlias, Unpack, TypeVarTuple
from gloe._transformer_utils import catch_transformer_exception
from gloe.base_transformer import BaseTransformer, Flow
from gloe.exceptions import TransformerRequiresMultiArgs

__all__ = ["Transformer"]

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

Args = TypeVarTuple("Args")
NextArgs = TypeVarTuple("NextArgs")
In1 = TypeVar("In1")
Awaited = TypeVar("Awaited")
_InP = TypeVar("_InP", contravariant=True)
_OutP = TypeVar("_OutP", covariant=True)


class _TransformerLike(Protocol[_InP, _OutP]):
    def transform(self, data: _InP) -> _OutP:
        ...


async def _execute_flow_async(flow: Flow, start_index: int, current: Any) -> Any:
    result = current
    if isawaitable(result):
        result = await result
    for op in flow[start_index:]:
        if isinstance(op, BaseTransformer):
            if hasattr(op, "_safe_transform"):
                result = op._safe_transform(result)
                if isawaitable(result):
                    result = await result
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
    return result


def _execute_flow(flow: Flow, arg: Any) -> Any:
    result = arg
    for index, op in enumerate(flow):
        if isinstance(op, BaseTransformer):
            if hasattr(op, "_safe_transform"):
                result = op._safe_transform(result)
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        if isawaitable(result):
            return _execute_flow_async(flow, index + 1, result)
    return result


class Transformer(BaseTransformer[Any, _O], Generic[Unpack[Args], _O], ABC):
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
        orig_bases = getattr(self, "__orig_bases__", [])
        transformer_args = [
            get_args(base)
            for base in orig_bases
            if get_origin(base) == Transformer
        ]
        if transformer_args and len(transformer_args[0]) > 2:
            self._multi_args = True

    @abstractmethod
    def transform(self, data: Any) -> _O:
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

    def _safe_transform(self, data: Any) -> _O:
        transform_exception = None

        transformed: Optional[_O] = None
        try:
            transformed = self.transform(data)
        except Exception as exception:
            transform_exception = catch_transformer_exception(exception, self)

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            if isawaitable(transformed):
                return cast(_O, self._await_transform(cast(Awaitable[Any], transformed)))
            return cast(_O, transformed)

        raise NotImplementedError()  # pragma: no cover

    def _await_transform(self, awaitable: Awaitable[Any]) -> Awaitable[Any]:
        async def _await_result() -> Any:
            try:
                return await awaitable
            except Exception as exception:
                transform_exception = catch_transformer_exception(exception, self)
                raise transform_exception.internal_exception

        return _await_result()

    async def transform_async(self, data: Any) -> Any:
        result = self._safe_transform(data)
        if isawaitable(result):
            return await cast(Awaitable[Any], result)
        return result

    @overload
    def __call__(self: "Transformer[None, _O]") -> _O:
        pass

    @overload
    def __call__(
        self: "Transformer[Unpack[Args], _O]", *data: Unpack[Args]
    ) -> _O:
        pass

    def __call__(self, *data):
        if self._multi_args:
            if len(data) == 1 and type(data[0]) is tuple:
                data = data[0]
            elif len(data) == 1:
                raise TransformerRequiresMultiArgs()
            return _execute_flow(self._flow, data)

        if len(data) == 0:
            return _execute_flow(self._flow, None)
        if len(data) == 1:
            return _execute_flow(self._flow, data[0])
        raise TypeError("Transformer expected a single argument")


    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], Awaitable[tuple[Unpack[NextArgs]]]]",
        next_node: "Transformer[Unpack[NextArgs], Awaitable[O1]]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], Awaitable[tuple[Unpack[NextArgs]]]]",
        next_node: "Transformer[Unpack[NextArgs], O1]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], tuple[Unpack[NextArgs]]]",
        next_node: "Transformer[Unpack[NextArgs], O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self: "Transformer[Unpack[Args], Awaitable[Awaited]]",
        next_node: "_TransformerLike[Awaited, Awaitable[O1]]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-cannot-match]
        self: "Transformer[Unpack[Args], Awaitable[Awaited]]",
        next_node: "_TransformerLike[Awaited, O1]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self: "Transformer[Unpack[Args], Awaitable[Awaited]]",
        next_node: "Transformer[Awaited, Awaitable[O1]]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self: "Transformer[Unpack[Args], Awaitable[Awaited]]",
        next_node: "Transformer[Awaited, O1]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], list[Item]]",
        next_node: "_TransformerLike[Iterable[Item], O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self: "Transformer[Unpack[Args], list[Item]]",
        next_node: "Transformer[Iterable[Item], O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-cannot-match]
        self: "Transformer[Unpack[Args], Awaitable[list[Item]]]",
        next_node: "_TransformerLike[Iterable[Item], O1]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self: "Transformer[Unpack[Args], Awaitable[list[Item]]]",
        next_node: "Transformer[Iterable[Item], O1]",
    ) -> "Transformer[Unpack[Args], Awaitable[O1]]":
        pass

    @overload
    def __rshift__(
        self: "Transformer[Unpack[Args], _O]",
        next_node: "_TransformerLike[_O, O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self: "Transformer[Unpack[Args], _O]",
        next_node: "Transformer[_O, O1]",
    ) -> "Transformer[Unpack[Args], O1]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self: "Transformer[Unpack[Args], Awaitable[Awaited]]",
        next_node: tuple["Tr[Awaited, O1]", "Tr[Awaited, O2]"],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple["Tr[_O, Awaitable[O1]]", "Tr[_O, Awaitable[O2]]"],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple["Tr[_O, Awaitable[O1]]", "Tr[_O, O2]"],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple["Tr[_O, O1]", "Tr[_O, Awaitable[O2]]"],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple[
            "Tr[_O, Awaitable[O1]]",
            "Tr[_O, O2]",
            "Tr[_O, O3]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple[
            "Tr[_O, O1]",
            "Tr[_O, Awaitable[O2]]",
            "Tr[_O, O3]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple[
            "Tr[_O, O1]",
            "Tr[_O, O2]",
            "Tr[_O, Awaitable[O3]]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self,
        next_node: tuple[
            "Tr[_O, Awaitable[O1]]",
            "Tr[_O, Awaitable[O2]]",
            "Tr[_O, O3]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self,
        next_node: tuple[
            "Tr[_O, Awaitable[O1]]",
            "Tr[_O, O2]",
            "Tr[_O, Awaitable[O3]]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self,
        next_node: tuple[
            "Tr[_O, O1]",
            "Tr[_O, Awaitable[O2]]",
            "Tr[_O, Awaitable[O3]]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap, overload-cannot-match]
        self,
        next_node: tuple[
            "Tr[_O, Awaitable[O1]]",
            "Tr[_O, Awaitable[O2]]",
            "Tr[_O, Awaitable[O3]]",
        ],
    ) -> "Transformer[Unpack[Args], Awaitable[tuple[O1, O2, O3]]]":
        pass

    @overload
    def __rshift__(  # type: ignore[overload-overlap]
        self,
        next_node: tuple["Tr[_O, O1]", "Tr[_O, O2]"],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[_O, O1]", "Tr[_O, O2]", "Tr[_O, O3]"],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Tr[_O, O1]", "Tr[_O, O2]", "Tr[_O, O3]", "Tr[_O, O4]"],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Tr[_O, O1]", "Tr[_O, O2]", "Tr[_O, O3]", "Tr[_O, O4]", "Tr[_O, O5]"
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4, O5]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Tr[_O, O1]",
            "Tr[_O, O2]",
            "Tr[_O, O3]",
            "Tr[_O, O4]",
            "Tr[_O, O5]",
            "Tr[_O, O6]",
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4, O5, O6]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Tr[_O, O1]",
            "Tr[_O, O2]",
            "Tr[_O, O3]",
            "Tr[_O, O4]",
            "Tr[_O, O5]",
            "Tr[_O, O6]",
            "Tr[_O, O7]",
        ],
    ) -> "Transformer[Unpack[Args], tuple[O1, O2, O3, O4, O5, O6, O7]]":
        pass

    def __rshift__(self, next_node):  # pragma: no cover
        pass
