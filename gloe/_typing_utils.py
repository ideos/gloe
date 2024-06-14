from types import GenericAlias
from typing import TypeVar, get_origin, _GenericAlias  # type: ignore


def _format_tuple(tuple_annotation: tuple, input_annotation) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(_format_return_annotation(annotation, input_annotation))
    return f"({', '.join(formatted)})"


def _format_union(tuple_annotation: tuple, input_annotation) -> str:
    formatted: list[str] = []
    for annotation in tuple_annotation:
        formatted.append(_format_return_annotation(annotation, input_annotation))
    return f"({' | '.join(formatted)})"


def _format_generic_alias(return_annotation: GenericAlias, input_annotation) -> str:
    alias_name = getattr(return_annotation, "__name__", None)
    if alias_name is None:
        alias_name = getattr(return_annotation, "_name")
    formatted: list[str] = []
    for annotation in return_annotation.__args__:
        formatted.append(_format_return_annotation(annotation, input_annotation))
    return f"{alias_name}[{', '.join(formatted)}]"


def _format_return_annotation(return_annotation, input_annotation=None) -> str:
    if isinstance(return_annotation, str):
        return return_annotation
    if isinstance(return_annotation, tuple):
        return _format_tuple(return_annotation, input_annotation)
    return_name = getattr(return_annotation, "__name__", None)
    if return_name is None:
        return_name = getattr(return_annotation, "_name", None)

    if return_name in {"tuple", "Tuple"}:
        return _format_tuple(return_annotation.__args__, input_annotation)
    if (
        return_name == "Union"
        or return_annotation.__class__.__name__ == "_UnionGenericAlias"
    ):
        return _format_union(return_annotation.__args__, input_annotation)
    if (
        type(return_annotation) is GenericAlias
        or type(return_annotation) is _GenericAlias
    ):  # _GenericAlias must be investigated too
        return _format_generic_alias(return_annotation, input_annotation)

    return str(return_name)


def _match_types(generic, specific):
    if type(generic) is TypeVar:
        return {generic: specific}

    specific_origin = get_origin(specific)
    generic_origin = get_origin(generic)

    if specific_origin is None and generic_origin is None:
        return {}

    if (
        specific_origin is None
        or generic_origin is None
        or not issubclass(specific_origin, generic_origin)
    ):
        return {}

    generic_args = getattr(generic, "__args__", ())
    specific_args = getattr(specific, "__args__", ())

    if len(generic_args) != len(specific_args):
        return {}

    matches = {}
    for generic_arg, specific_arg in zip(generic_args, specific_args):
        matched_types = _match_types(generic_arg, specific_arg)
        matches.update(matched_types)

    return matches


def _specify_types(generic, spec):
    if type(generic) is TypeVar:
        tp = spec.get(generic)
        if tp is None:
            return generic
        return tp

    generic_args = getattr(generic, "__args__", None)

    if generic_args is None:
        return generic

    origin = get_origin(generic)

    args = tuple(_specify_types(arg, spec) for arg in generic_args)

    return GenericAlias(origin, args)
