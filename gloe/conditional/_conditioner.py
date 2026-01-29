import sys
from types import GenericAlias

from gloe.conditional._base_conditioner import BaseConditioner
from gloe.conditional._implication import _Implication, _AsyncImplication
from collections.abc import Awaitable as AwaitableABC
from inspect import Signature
from typing import (
    Awaitable,
    cast,
    get_args,
    get_origin,
    TypeVar,
    Union,
    Sequence,
    Any,
)

from gloe.transformers import Transformer


In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


class Conditioner(
    BaseConditioner[In, ThenOut, ElseOut, Union[ThenOut, ElseOut]],
    Transformer[In, Union[ThenOut, ElseOut]],
):
    def __init__(
        self,
        implications: Sequence[_Implication[In, ThenOut]],
        else_transformer: Transformer[In, ElseOut],
    ):
        super().__init__(implications, else_transformer)
        self.implications: Sequence[_Implication[In, ThenOut]] = implications
        self.else_transformer: Transformer[In, ElseOut] = else_transformer

    def transform(self, data: In) -> Union[ThenOut, ElseOut]:
        for implication in self.implications:
            if implication.condition(data):
                return cast(Union[ThenOut, ElseOut], implication.then_transformer(data))
        return cast(Union[ThenOut, ElseOut], self.else_transformer(data))


class AsyncConditioner(
    BaseConditioner[
        In,
        Awaitable[ThenOut],
        Awaitable[ElseOut],
        Awaitable[Union[ThenOut, ElseOut]],
    ],
    Transformer[In, Awaitable[Union[ThenOut, ElseOut]]],
):
    def __init__(
        self,
        implications: Sequence[_AsyncImplication[In, ThenOut]],
        else_transformer: Transformer[In, Awaitable[ElseOut]],
    ):
        super().__init__(implications, else_transformer)
        self.implications: Sequence[_AsyncImplication[In, ThenOut]] = implications
        self.else_transformer: Transformer[In, Awaitable[ElseOut]] = else_transformer

    def transform(self, data: In) -> Awaitable[Union[ThenOut, ElseOut]]:
        for implication in self.implications:
            if implication.condition(data):
                return implication.then_transformer(data)
        return self.else_transformer(data)

    def signature(self) -> Signature:
        else_signature = self.else_transformer.signature()
        return_signatures = [
            impl.then_transformer.signature().return_annotation
            for impl in self.implications
        ] + [else_signature.return_annotation]

        def _unwrap_awaitable(annotation: Any) -> Any:
            origin = get_origin(annotation)
            if origin in (Awaitable, AwaitableABC):
                args = get_args(annotation)
                if args:
                    return args[0]
            return annotation

        awaited_signatures = [_unwrap_awaitable(sig) for sig in return_signatures]

        union_type: type = cast(type, Union)
        if sys.version_info >= (3, 10):
            from types import UnionType

            union_type = UnionType

        new_union = GenericAlias(union_type, tuple(awaited_signatures))
        awaitable_type = cast(Any, Awaitable)
        return else_signature.replace(return_annotation=awaitable_type[new_union])
