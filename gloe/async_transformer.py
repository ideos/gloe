from abc import abstractmethod
from inspect import Signature
from typing import TypeVar, overload, cast, Callable, Generic, Optional, Any

from typing_extensions import Self

from gloe._plotting_utils import PlottingSettings, NodeType
from gloe._transformer_utils import catch_transformer_exception
from gloe.base_transformer import BaseTransformer, Flow

__all__ = ["AsyncTransformer"]

_In = TypeVar("_In", contravariant=True)
_Out = TypeVar("_Out", covariant=True)
_NextOut = TypeVar("_NextOut")

_O2 = TypeVar("_O2")
_O3 = TypeVar("_O3")
_O4 = TypeVar("_O4")
_O5 = TypeVar("_O5")
_O6 = TypeVar("_O6")
_O7 = TypeVar("_O7")


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

    async def __call__(self, data: _In) -> _Out:
        return await _execute_async_flow(self._flow, data)

    def copy(
        self,
        transform: Optional[Callable[[Self, _In], _Out]] = None,
        regenerate_instance_id: bool = False,
        force: bool = False,
    ) -> Self:
        return self._copy(transform, regenerate_instance_id, "transform_async", force)

    @overload
    def __rshift__(
        self, next_node: BaseTransformer[_Out, _NextOut]
    ) -> "AsyncTransformer[_In, _NextOut]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[BaseTransformer[_Out, _NextOut], BaseTransformer[_Out, _O2]],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            BaseTransformer[_Out, _NextOut],
            BaseTransformer[_Out, _O2],
            BaseTransformer[_Out, _O3],
        ],
    ) -> "AsyncTransformer[_In, tuple[_NextOut, _O2, _O3]]":
        pass

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
        pass

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
        pass

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
        pass

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
        pass

    def __rshift__(self, next_node):  # pragma: no cover
        pass
