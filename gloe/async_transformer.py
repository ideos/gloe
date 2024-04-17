import copy
import types
import uuid
from abc import abstractmethod
from inspect import Signature
from typing import TypeVar, overload, cast, Callable, Generic

from typing_extensions import Self

from gloe._plotting_utils import PlottingSettings, NodeType
from gloe._transformer_utils import catch_transformer_exception
from gloe.base_transformer import (
    BaseTransformer,
    PreviousTransformer,
)

__all__ = ["AsyncTransformer"]

_In = TypeVar("_In", contravariant=True)
_Out = TypeVar("_Out", covariant=True)
_NextOut = TypeVar("_NextOut")

_Out2 = TypeVar("_Out2")
_Out3 = TypeVar("_Out3")
_Out4 = TypeVar("_Out4")
_Out5 = TypeVar("_Out5")
_Out6 = TypeVar("_Out6")
_Out7 = TypeVar("_Out7")


class AsyncTransformer(Generic[_In, _Out], BaseTransformer[_In, _Out]):
    def __init__(self):
        super().__init__()

        self._plotting_settings = PlottingSettings(
            node_type=NodeType.Transformer, is_async=True
        )
        self.__class__.__annotations__ = self.transform_async.__annotations__

    @abstractmethod
    async def transform_async(self, data: _In) -> _Out:
        """
        Method to perform the transformation asynchronously.

        Args:
            data: the incoming data passed to the transformer during the pipeline
                execution.

        Return:
            The outcome data, it means, the resulf of the transformation.
        """

    def signature(self) -> Signature:
        return self._signature(AsyncTransformer, "transform_async")

    def __repr__(self):
        return (
            f"{self.input_annotation}"
            f" -> ({type(self).__name__})"
            f" -> {self.output_annotation}"
        )

    async def __call__(self, data: _In) -> _Out:
        transform_exception = None

        transformed: _Out | None = None
        try:
            transformed = await self.transform_async(data)
        except Exception as exception:
            transform_exception = catch_transformer_exception(exception, self)

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return cast(_Out, transformed)

        raise NotImplementedError  # pragma: no cover

    def copy(
        self,
        transform: Callable[[Self, _In], _Out] | None = None,
        regenerate_instance_id: bool = False,
    ) -> Self:
        copied = copy.copy(self)

        func_type = types.MethodType
        if transform is not None:
            setattr(copied, "transform_async", func_type(transform, copied))

        if regenerate_instance_id:
            copied.instance_id = uuid.uuid4()

        if self.previous is not None:
            if type(self.previous) is tuple:
                new_previous: list[BaseTransformer] = [
                    previous_transformer.copy() for previous_transformer in self.previous
                ]
                copied._previous = cast(PreviousTransformer, tuple(new_previous))
            elif isinstance(self.previous, BaseTransformer):
                copied._previous = self.previous.copy()

        copied._children = [
            child.copy(regenerate_instance_id=True) for child in self.children
        ]

        return copied

    @overload
    def __rshift__(
        self, next_node: BaseTransformer[_Out, _NextOut]
    ) -> "AsyncTransformer[_In, _NextOut]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[BaseTransformer[_Out, _NextOut], BaseTransformer[_Out, _Out2]],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _Out2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _Out2],
            BaseTransformer[_Out, _Out3],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _Out2],
            BaseTransformer[_Out, _Out3],
            BaseTransformer[_Out, _Out4],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _Out2],
            BaseTransformer[_Out, _Out3],
            BaseTransformer[_Out, _Out4],
            BaseTransformer[_Out, _Out5],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _Out2],
            BaseTransformer[_Out, _Out3],
            BaseTransformer[_Out, _Out4],
            BaseTransformer[_Out, _Out5],
            BaseTransformer[_Out, _Out6],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _Out2],
            BaseTransformer[_Out, _Out3],
            BaseTransformer[_Out, _Out4],
            BaseTransformer[_Out, _Out5],
            BaseTransformer[_Out, _Out6],
            BaseTransformer[_Out, _Out7],
        ],
    ) -> (
        "AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6, _Out7]]"
    ):
        pass

    def __rshift__(self, next_node):  # pragma: no cover
        pass
