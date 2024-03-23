import inspect
import traceback
from abc import ABC, abstractmethod
from inspect import Signature

from typing import (
    TypeVar,
    overload,
    cast,
    Any,
    get_args,
    get_origin,
    Generic,
)

from gloe._utils import _format_return_annotation
from gloe.base_transformer import BaseTransformer, TransformerException
from gloe.async_transformer import AsyncTransformer

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")

_Out2 = TypeVar("_Out2")
_Out3 = TypeVar("_Out3")
_Out4 = TypeVar("_Out4")
_Out5 = TypeVar("_Out5")
_Out6 = TypeVar("_Out6")
_Out7 = TypeVar("_Out7")


class Transformer(BaseTransformer[_In, _Out, "Transformer"], ABC):
    """
    A Transformer is generic block with the responsibility to take an input of type `T`
    and transform it to an output of type `S`.


    Typical usage example:

    class Stringifier(Transformer[dict, str]):
        ...

    """

    def __init__(self):
        super().__init__()
        self.__class__.__annotations__ = self.transform.__annotations__

    @abstractmethod
    def transform(self, data: _In) -> _Out:
        """Main method to be implemented and responsible to perform the transformer logic"""

    def signature(self) -> Signature:
        return self._signature(Transformer)

    def __repr__(self):
        return f"{self.input_annotation} -> ({type(self).__name__}) -> {self.output_annotation}"

    def __call__(self, data: _In) -> _Out:
        transform_exception = None

        transformed: _Out | None = None
        try:
            transformed = self.transform(data)
        except Exception as exception:
            if type(exception.__cause__) == TransformerException:
                transform_exception = exception.__cause__
            else:
                tb = traceback.extract_tb(exception.__traceback__)

                # TODO: Make this filter condition stronger
                transformer_frames = [
                    frame
                    for frame in tb
                    if frame.name == self.__class__.__name__
                    or frame.name == "transform"
                ]

                if len(transformer_frames) == 1:
                    transformer_frame = transformer_frames[0]
                    exception_message = (
                        f"\n  "
                        f'File "{transformer_frame.filename}", line {transformer_frame.lineno}, '
                        f'in transformer "{self.__class__.__name__}"\n  '
                        f"  >> {transformer_frame.line}"
                    )
                else:
                    exception_message = (
                        f'An error occurred in transformer "{self.__class__.__name__}"'
                    )

                transform_exception = TransformerException(
                    internal_exception=exception,
                    raiser_transformer=self,
                    message=exception_message,
                )

        if transform_exception is not None:
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return cast(_Out, transformed)

        raise NotImplementedError

    @overload
    def __rshift__(
        self,
        next_node: tuple["Transformer[_Out, _NextOut]", "Transformer[_Out, _Out2]"],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_Out, _NextOut]",
            "Transformer[_Out, _Out2]",
            "Transformer[_Out, _Out3]",
        ],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2, _Out3]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_Out, _NextOut]",
            "Transformer[_Out, _Out2]",
            "Transformer[_Out, _Out3]",
            "Transformer[_Out, _Out4]",
        ],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_Out, _NextOut]",
            "Transformer[_Out, _Out2]",
            "Transformer[_Out, _Out3]",
            "Transformer[_Out, _Out4]",
            "Transformer[_Out, _Out5]",
        ],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_Out, _NextOut]",
            "Transformer[_Out, _Out2]",
            "Transformer[_Out, _Out3]",
            "Transformer[_Out, _Out4]",
            "Transformer[_Out, _Out5]",
            "Transformer[_Out, _Out6]",
        ],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Transformer[_Out, _NextOut]",
            "Transformer[_Out, _Out2]",
            "Transformer[_Out, _Out3]",
            "Transformer[_Out, _Out4]",
            "Transformer[_Out, _Out5]",
            "Transformer[_Out, _Out6]",
            "Transformer[_Out, _Out7]",
        ],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6, _Out7]]":
        pass

    @overload
    def __rshift__(
        self, next_node: "Transformer[_Out, _NextOut]"
    ) -> "Transformer[_In, _NextOut]":
        pass

    @overload
    def __rshift__(
        self, next_node: "AsyncTransformer[_Out, _NextOut]"
    ) -> "AsyncTransformer[_In, _NextOut]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            AsyncTransformer[_Out, _NextOut],
            "AsyncTransformer[_Out, _Out2] | Transformer[_Out, _Out2]",
        ],
    ) -> AsyncTransformer[_In, tuple[_NextOut, _Out2]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "AsyncTransformer[_Out, _NextOut] | Transformer[_Out, _NextOut]",
            "AsyncTransformer[_Out, _Out2]",
        ],
    ) -> AsyncTransformer[_In, tuple[_NextOut, _Out2]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "AsyncTransformer[_Out, _NextOut]",
            "AsyncTransformer[_Out, _Out2] | Transformer[_Out, _Out2]",
            "AsyncTransformer[_Out, _Out3] | Transformer[_Out, _Out3]",
        ],
    ) -> AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "AsyncTransformer[_Out, _NextOut] | Transformer[_Out, _NextOut]",
            "AsyncTransformer[_Out, _Out2]",
            "AsyncTransformer[_Out, _Out3] | Transformer[_Out, _Out3]",
        ],
    ) -> AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "AsyncTransformer[_Out, _NextOut] | Transformer[_Out, _NextOut]",
            "AsyncTransformer[_Out, _Out2] | Transformer[_Out, _Out2]",
            "AsyncTransformer[_Out, _Out3]",
        ],
    ) -> AsyncTransformer[_In, tuple[_NextOut, _Out2, _Out3]]:
        pass

    def __rshift__(self, next_node):
        pass
