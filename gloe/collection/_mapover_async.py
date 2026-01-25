from inspect import Parameter, Signature
from typing import Generic, Iterable, TypeVar, overload, cast, get_args, get_origin
from typing_extensions import TypeVarTuple, Unpack

from gloe import AsyncTransformer

Args = TypeVarTuple("Args")
_Head = TypeVar("_Head")
_Tail = TypeVarTuple("_Tail")
_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class MapOverAsync(Generic[Unpack[Args], _U], AsyncTransformer[Unpack[Args], list[_U]]):
    @overload
    def __init__(
        self: "MapOverAsync[_T, _U]",
        iterable: Iterable[_S],
        mapping_transformer: AsyncTransformer[tuple[_T, _S], _U],
    ) -> None:
        pass

    @overload
    def __init__(
        self: "MapOverAsync[_Head, Unpack[_Tail], _U]",
        iterable: Iterable[_S],
        mapping_transformer: AsyncTransformer[_Head, Unpack[_Tail], _S, _U],
    ) -> None:
        pass

    def __init__(
        self,
        iterable: Iterable[_S],
        mapping_transformer: AsyncTransformer[tuple[_T, _S], _U]
        | AsyncTransformer[_Head, Unpack[_Tail], _S, _U],
    ):
        super().__init__()
        self._validate_mapping_transformer(mapping_transformer)
        self.iterable = iterable
        self.mapping_transformer = cast(
            AsyncTransformer[tuple[object, ...], _U], mapping_transformer
        )
        self.plotting_settings.has_children = True
        self._children = [mapping_transformer]

    def signature(self) -> Signature:
        mapping_signature = self.mapping_transformer.signature()
        params = list(mapping_signature.parameters.values())
        return_annotation = self._signature(
            AsyncTransformer, "transform_async"
        ).return_annotation

        if len(params) == 0:
            return Signature(parameters=[], return_annotation=return_annotation)

        if len(params) == 1:
            annotation = params[0].annotation
            origin = get_origin(annotation)
            args = get_args(annotation)
            if origin is tuple and len(args) > 0:
                annotation = args[0]
            param = params[0].replace(
                annotation=annotation,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
            )
            return Signature(parameters=[param], return_annotation=return_annotation)

        return Signature(parameters=params[:-1], return_annotation=return_annotation)

    def _validate_mapping_transformer(
        self,
        mapping_transformer: AsyncTransformer[tuple[_T, _S], _U]
        | AsyncTransformer[_Head, Unpack[_Tail], _S, _U],
    ) -> None:
        mapping_signature = mapping_transformer.signature()
        params = list(mapping_signature.parameters.values())
        if len(params) == 0:
            raise TypeError(
                "MapOverAsync mapping transformer must accept extra arguments plus the item."
            )
        if len(params) == 1:
            annotation = params[0].annotation
            origin = get_origin(annotation)
            args = get_args(annotation)
            if origin is not tuple:
                raise TypeError(
                    "MapOverAsync mapping transformer must accept a tuple of (extra, item). "
                    "Use MapAsync for single-argument mapping."
                )
            if len(args) == 1 and args[0] is not ...:
                raise TypeError(
                    "MapOverAsync mapping transformer tuple must include the extra argument "
                    "and the item."
                )

    async def transform_async(self, *data: Unpack[Args]) -> list[_U]:
        lopping_result = []
        for item in self.iterable:
            result = await self.mapping_transformer((*data, item))
            lopping_result.append(result)
        return lopping_result
