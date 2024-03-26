import traceback
from abc import ABC, abstractmethod
from inspect import Signature

from typing import (
    TypeVar,
    overload,
    cast,
    Any,
    TypeAlias,
    Union,
)

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


Trf: TypeAlias = "Transformer"
ATrf: TypeAlias = AsyncTransformer
BTrf: TypeAlias = BaseTransformer[_In, _Out, Any]

AsyncNext2 = Union[
    tuple[ATrf[_Out, _NextOut], BTrf[_Out, _Out2]],
    tuple[BTrf[_Out, _NextOut], ATrf[_Out, _Out2]],
]

AsyncNext3 = Union[
    tuple[ATrf[_Out, _NextOut], BTrf[_Out, _Out2], BTrf[_Out, _Out3]],
    tuple[BTrf[_Out, _NextOut], ATrf[_Out, _Out2], BTrf[_Out, _Out3]],
    tuple[BTrf[_Out, _NextOut], BTrf[_Out, _Out2], ATrf[_Out, _Out3]],
]

AsyncNext4 = Union[
    tuple[
        ATrf[_Out, _NextOut], BTrf[_Out, _Out2], BTrf[_Out, _Out3], BTrf[_Out, _Out4]
    ],
    tuple[
        BTrf[_Out, _NextOut], ATrf[_Out, _Out2], BTrf[_Out, _Out3], BTrf[_Out, _Out4]
    ],
    tuple[
        BTrf[_Out, _NextOut], BTrf[_Out, _Out2], ATrf[_Out, _Out3], BTrf[_Out, _Out4]
    ],
    tuple[
        BTrf[_Out, _NextOut], BTrf[_Out, _Out2], BTrf[_Out, _Out3], ATrf[_Out, _Out4]
    ],
]

AsyncNext5 = Union[
    tuple[
        ATrf[_Out, _NextOut],
        BTrf[_Out, _Out2],
        BTrf[_Out, _Out3],
        BTrf[_Out, _Out4],
        BTrf[_Out, _Out5],
    ],
    tuple[
        BTrf[_Out, _NextOut],
        ATrf[_Out, _Out2],
        BTrf[_Out, _Out3],
        BTrf[_Out, _Out4],
        BTrf[_Out, _Out5],
    ],
    tuple[
        BTrf[_Out, _NextOut],
        BTrf[_Out, _Out2],
        ATrf[_Out, _Out3],
        BTrf[_Out, _Out4],
        BTrf[_Out, _Out5],
    ],
    tuple[
        BTrf[_Out, _NextOut],
        BTrf[_Out, _Out2],
        BTrf[_Out, _Out3],
        ATrf[_Out, _Out4],
        BTrf[_Out, _Out5],
    ],
    tuple[
        BTrf[_Out, _NextOut],
        BTrf[_Out, _Out2],
        BTrf[_Out, _Out3],
        BTrf[_Out, _Out4],
        ATrf[_Out, _Out5],
    ],
]


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
        next_node: tuple["Trf[_Out, _NextOut]", "Trf[_Out, _Out2]"],
    ) -> "Trf[_In, tuple[_NextOut, _Out2]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple["Trf[_Out, _NextOut]", "Trf[_Out, _Out2]", "Trf[_Out, _Out3]"],
    ) -> "Transformer[_In, tuple[_NextOut, _Out2, _Out3]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Trf[_Out, _NextOut]",
            "Trf[_Out, _Out2]",
            "Trf[_Out, _Out3]",
            "Trf[_Out, _Out4]",
        ],
    ) -> "Trf[_In, tuple[_NextOut, _Out2, _Out3, _Out4]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Trf[_Out, _NextOut]",
            "Trf[_Out, _Out2]",
            "Trf[_Out, _Out3]",
            "Trf[_Out, _Out4]",
            "Trf[_Out, _Out5]",
        ],
    ) -> "Trf[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Trf[_Out, _NextOut]",
            "Trf[_Out, _Out2]",
            "Trf[_Out, _Out3]",
            "Trf[_Out, _Out4]",
            "Trf[_Out, _Out5]",
            "Trf[_Out, _Out6]",
        ],
    ) -> "Trf[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6]]":
        pass

    @overload
    def __rshift__(
        self,
        next_node: tuple[
            "Trf[_Out, _NextOut]",
            "Trf[_Out, _Out2]",
            "Trf[_Out, _Out3]",
            "Trf[_Out, _Out4]",
            "Trf[_Out, _Out5]",
            "Trf[_Out, _Out6]",
            "Trf[_Out, _Out7]",
        ],
    ) -> "Trf[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5, _Out6, _Out7]]":
        pass

    @overload
    def __rshift__(self, next_node: "Trf[_Out, _NextOut]") -> "Trf[_In, _NextOut]":
        pass

    @overload
    def __rshift__(self, next_node: ATrf[_Out, _NextOut]) -> ATrf[_In, _NextOut]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: AsyncNext2[_Out, _NextOut, _Out2],
    ) -> ATrf[_In, tuple[_NextOut, _Out2]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: AsyncNext3[_Out, _NextOut, _Out2, _Out3],
    ) -> ATrf[_In, tuple[_NextOut, _Out2, _Out3]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: AsyncNext4[_Out, _NextOut, _Out2, _Out3, _Out4],
    ) -> ATrf[_In, tuple[_NextOut, _Out2, _Out3, _Out4]]:
        pass

    @overload
    def __rshift__(
        self,
        next_node: AsyncNext5[_Out, _NextOut, _Out2, _Out3, _Out4, _Out5],
    ) -> ATrf[_In, tuple[_NextOut, _Out2, _Out3, _Out4, _Out5]]:
        pass

    def __rshift__(self, next_node):
        pass
