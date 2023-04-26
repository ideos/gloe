from types import GenericAlias
from typing import ForwardRef, _GenericAlias


def _format_tuple(tuple_annotation: tuple) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(_format_return_annotation(annotation))
    return f"({', '.join(formatted)})"


def _format_union(tuple_annotation: tuple) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(_format_return_annotation(annotation))
    return f"({' | '.join(formatted)})"


def _format_generic_alias(return_annotation: GenericAlias) -> str:
    alias_name = return_annotation.__name__
    formatted: list[str] = []
    for annotation in return_annotation.__args__:
        formatted.append(_format_return_annotation(annotation))
    return f"{alias_name}[{', '.join(formatted)}]"


def _format_return_annotation(return_annotation) -> str:
    if type(return_annotation) == str:
        return return_annotation
    if type(return_annotation) == tuple:
        return _format_tuple(return_annotation)
    if return_annotation.__name__ in {'tuple', 'Tuple'}:
        return _format_tuple(return_annotation.__args__)
    if return_annotation.__name__ in {'Union'}:
        return _format_union(return_annotation.__args__)
    if type(return_annotation) == GenericAlias or type(return_annotation) == _GenericAlias:
        return _format_generic_alias(return_annotation)

    return str(return_annotation.__name__)

ForwardRef