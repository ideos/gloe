from abc import abstractmethod
from inspect import Signature
from typing import TypeVar, overload, cast, Callable, Optional, Any

from typing_extensions import Self, Unpack, Generic, TypeVarTuple, override

from typing import Type
from gloe._composition import CompositionMixin
from gloe._gloe_transformer import _GloeTransformer
from gloe._plotting_utils import PlottingSettings, NodeType
from gloe._transformer_utils import catch_transformer_exception
from gloe.base_transformer import BaseTransformer, Flow

__all__ = ["AsyncTransformer", "MultiArgsAsyncTransformer"]

_In = TypeVar("_In", contravariant=True)
_Out = TypeVar("_Out", covariant=True)
_NextOut = TypeVar("_NextOut")

_O2 = TypeVar("_O2")
_O3 = TypeVar("_O3")
_O4 = TypeVar("_O4")
_O5 = TypeVar("_O5")
_O6 = TypeVar("_O6")
_O7 = TypeVar("_O7")

Args = TypeVarTuple("Args")


async def _execute_async_flow(flow: Flow, arg: Any) -> Any:
    result = arg
    for op in flow:
        if isinstance(op, BaseTransformer):
            if isinstance(op, AsyncTransformer):
                result = await op._safe_transform(result)
            else:
                if hasattr(op, "_safe_transform"):
                    result = op._safe_transform(result)
                else:
                    raise NotImplementedError()
        else:
            raise NotImplementedError()
    return result


class AsyncTransformer(
    CompositionMixin, _GloeTransformer[_In, _Out], Generic[_In, _Out]
):
    @property
    def _transform_method_name(self) -> str:
        return "transform_async"

    @property
    def _concrete_class(self) -> Type["AsyncTransformer"]:
        return AsyncTransformer

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

    async def _safe_transform(self, data: _In) -> _Out:
        transform_exception = None

        transformed: Optional[_Out] = None
        try:
            transformed = await self.transform_async(data)
        except Exception as exception:
            transform_exception = catch_transformer_exception(exception, self)

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return cast(_Out, transformed)

        raise NotImplementedError  # pragma: no cover

    @overload
    async def __call__(self: "AsyncTransformer[None, _Out]") -> _Out:
        return await _execute_async_flow(self._flow, None)

    @overload
    async def __call__(self, data: _In) -> _Out:
        return await _execute_async_flow(self._flow, data)

    async def __call__(self, data=None):
        return await _execute_async_flow(self._flow, data)

    @overload
    def __rshift__(
        self, next_node: BaseTransformer[_Out, _NextOut]
    ) -> "AsyncTransformer[_In, _NextOut]":
        ...

    @overload
    def __rshift__(
        self,
        next_node: tuple[BaseTransformer[_Out, _NextOut], BaseTransformer[_Out, _O2]],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2]]":
        ...

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _O2],
            BaseTransformer[_Out, _O3],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2, _O3]]":
        ...

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _O2],
            BaseTransformer[_Out, _O3],
            BaseTransformer[_Out, _O4],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2, _O3, _O4]]":
        ...

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _O2],
            BaseTransformer[_Out, _O3],
            BaseTransformer[_Out, _O4],
            BaseTransformer[_Out, _O5],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2, _O3, _O4, _O5]]":
        ...

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _O2],
            BaseTransformer[_Out, _O3],
            BaseTransformer[_Out, _O4],
            BaseTransformer[_Out, _O5],
            BaseTransformer[_Out, _O6],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2, _O3, _O4, _O5, _O6]]":
        ...

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _O2],
            BaseTransformer[_Out, _O3],
            BaseTransformer[_Out, _O4],
            BaseTransformer[_Out, _O5],
            BaseTransformer[_Out, _O6],
            BaseTransformer[_Out, _O7],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2, _O3, _O4, _O5, _O6, _O7]]":
        ...

    def __rshift__(self, next_node):
        return super().__rshift__(next_node)


class MultiArgsAsyncTransformer(
    Generic[Unpack[Args], _Out], AsyncTransformer[tuple[Unpack[Args]], _Out]
):
    @override
    async def __call__(  # type: ignore[override]
        self: "MultiArgsAsyncTransformer[Unpack[Args], _Out]", *data: Unpack[Args]
    ) -> _Out:
        return await _execute_async_flow(self._flow, data)
