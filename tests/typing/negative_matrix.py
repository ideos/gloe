"""Invalid cross-feature programs, paired with positive_matrix.py."""

from collections.abc import Awaitable, Callable
from functools import partial
from typing import Any, Literal, TypedDict, overload

import gloe
from tests.typing.positive_matrix import (
    Person,
    Row,
    UserId,
    arguments,
    async_constant,
    choose,
    configured,
    constant,
    convert,
    deferred,
    even,
    formatted,
    identity,
    increment,
    join,
    name,
    mode,
    nested,
    row_name,
    text,
    variadic,
)


def unknown_input(value: Any) -> int:
    return 1


gloe.Transformer(unknown_input)  # reject: erased_root_input


def untyped_result(value: int) -> Any:
    return value


def union_unknown(value: int) -> str | list[Any]:
    return str(value)


gloe.Transformer(untyped_result)  # reject: erased_root_output
gloe.input[int]() >> union_unknown  # reject: union_unknown_output


class UnknownField(TypedDict):
    value: Any


gloe.input[UnknownField]()  # reject: erased_record_input
gloe.input[type[Any]]()  # reject: erased_class_input

type RecursiveUnknown = list[RecursiveUnknown] | dict[str, Any]
type GenericTree[T] = T | list[GenericTree[T]]
gloe.input[RecursiveUnknown]()  # reject: recursive_unknown_alias
gloe.input[GenericTree[Any]]()  # reject: recursive_unknown_argument

gloe.transformer(formatted)()  # reject: overload_missing_configuration
gloe.transformer(formatted)(label=1)  # reject: overload_configuration_type
gloe.input[float]() >> gloe.transformer(formatted)(  # reject: overload_data_type
    label="v"
)
gloe.transformer(mode)(kind="other")  # reject: overload_configuration_literal

root = gloe.Transformer(arguments)
root.sync()  # reject: missing_root_input
root.sync(first=1)  # reject: positional_only_root
root.sync(1, second=2)  # reject: optional_root_input_type
root.sync(1, suffix=2)  # reject: root_keyword_type
root.sync(1, "a", "!")  # reject: root_keyword_passed_positionally
gloe.Transformer(constant).sync(1)  # reject: extra_zero_root_argument
gloe.Transformer(variadic).sync(1, "a")  # reject: variadic_root_argument
gloe.Transformer(variadic).sync(1, extra="a")  # reject: variadic_root_keyword

_ = configured(suffix="!")(1, suffix="?")  # reject: configuration_rebound
_ = configured(suffix="!")(first=1)  # reject: configured_positional_only
_ = configured(suffix="!")(1, second=2)  # reject: configured_optional_input
configured(unknown=True)  # reject: unknown_configuration
convert(function=increment)("a")  # reject: config_generic_specialization

gloe.input[str]() >> gloe.Transformer(async_constant)  # reject: zero_root_as_stage
gloe.input[int]() >> (increment, text, name)  # reject: last_branch_input
gloe.input[int]() >> ((increment, text), text)  # reject: raw_nested_branch_tuple
gloe.input[int]() >> [increment, text]  # reject: list_is_not_fanout
gloe.input[int]() >> 1  # reject: non_callable_stage
gloe.input[int]() >> None  # reject: none_stage
gloe.input[int]() >> gloe.input[str]()  # reject: incompatible_explicit_identity
gloe.input[Awaitable[int]]() >> increment  # reject: awaitable_input_is_data
gloe.input[int]() >> deferred >> text >> increment  # reject: custom_awaitable_result
gloe.input[int]() >> nested >> str.upper  # reject: nested_awaitable_is_data


def optional(value: int) -> int | None:
    return value if value else None


gloe.input[int]() >> optional >> increment  # reject: optional_requires_handling
gloe.input[Literal["c"]]() >> choose  # reject: literal_input
gloe.input[int]() >> row_name  # reject: record_input
gloe.input[Person]() >> row_name  # reject: nominal_record_mismatch


def account(value: UserId) -> Row:
    return {"id": value, "name": "Ada"}


gloe.input[int]() >> account  # reject: nominal_unit_input

gloe.input[tuple[int]]() >> gloe.unpack(join)  # reject: unpack_missing_argument
gloe.input[tuple[int, str]]() >> gloe.unpack(join)  # reject: unpack_overload_mismatch
gloe.input[tuple[int, int, int]]() >> gloe.unpack(join)  # reject: unpack_extra_argument
gloe.input[tuple[str]]() >> gloe.unpack(arguments)  # reject: unpack_default_type
gloe.input[tuple[int, ...]]() >> gloe.unpack(arguments)  # reject: unpack_unknown_length
gloe.unpack(1)  # reject: unpack_non_callable


def keyword(value: int, *, required: str) -> str:
    return required


gloe.input[int]() >> keyword  # reject: unbound_required_keyword
gloe.unpack(keyword)  # reject: unpack_required_keyword
gloe.unpack(variadic)  # reject: unpack_variadic

gloe.input[str]() >> partial(arguments, 1)  # accepted: remaining input is str
gloe.input[int]() >> partial(arguments, 1)  # reject: partial_remaining_input
gloe.input[int]() >> partial(arguments, first=1)  # reject: partial_positional_keyword


def keyword_variadic(value: int, **options: int) -> int:
    return value


gloe.transformer(keyword_variadic)  # reject: variadic_keyword_factory


def not_boolean(value: int) -> str:
    return str(value)


async def async_not_boolean(value: int) -> int:
    return value


gloe.map(increment)(["a"])  # reject: direct_map_input
gloe.filter(even)(["a"])  # reject: direct_filter_input
gloe.filter(async_not_boolean)  # reject: async_predicate_output
gloe.condition(not_boolean, then=increment, otherwise=increment)  # reject: predicate
gloe.input[int]() >> gloe.condition(  # reject: condition_else_input
    even, then=text, otherwise=name
)
gloe.input[int]() >> gloe.condition(  # reject: condition_then_input
    even, then=name, otherwise=text
)
gloe.condition(even, then=text, otherwise=untyped_result)  # reject: condition_unknown
gloe.parallel((increment, untyped_result))  # reject: parallel_unknown
gloe.sequential((increment, untyped_result))  # reject: sequential_unknown
gloe.parallel((increment, 1))  # reject: non_callable_dynamic_branch

erased_callbacks: list[Callable[..., int]] = [increment]
gloe.parallel(erased_callbacks)  # reject: erased_dynamic_signature
gloe.sequential(erased_callbacks)  # reject: erased_sequential_signature

erased_map: Callable[..., int] = increment
erased_predicate: Callable[..., bool] = even
gloe.map(erased_map)  # reject: erased_map_signature
gloe.filter(erased_predicate)  # reject: erased_predicate_signature
gloe.condition(  # reject: erased_condition_signature
    erased_predicate, then=increment, otherwise=increment
)

erased_partial: partial[int] = partial(increment)
gloe.map(erased_partial)  # reject: erased_partial_map
gloe.Transformer(erased_partial)  # reject: erased_partial_root
gloe.Transformer(partial(identity))  # reject: generic_partial_root


class CallableOperation:
    def __call__(self, value: int) -> int:
        return value


gloe.transformer(CallableOperation())  # reject: callable_object_factory_adapter
gloe.ensure()(CallableOperation())  # reject: callable_object_ensurer_adapter


def non_none(value: int) -> bool:
    return True


def check_text(value: str) -> None:
    pass


class AsyncValidator:
    async def __call__(self, value: int) -> None:
        pass


gloe.ensure(incoming=AsyncValidator())(increment)  # reject: async_object_validator
gloe.ensure(incoming=non_none)(increment)  # reject: non_none_incoming
gloe.ensure(incoming=[check_text])(increment)  # reject: list_validator_input
gloe.ensure(incoming=None)(increment)  # reject: non_callable_validator
gloe.ensure()(constant)  # reject: ensure_zero_input
gloe.ensure()(arguments)  # reject: ensure_multiple_inputs
gloe.ensure()(keyword_variadic)  # reject: ensure_variadic_keywords


@overload
def overloaded(value: int) -> str: ...


@overload
def overloaded(value: str) -> int: ...


def overloaded(value: int | str) -> str | int:
    return str(value) if isinstance(value, int) else len(value)


gloe.ensure(incoming=check_text)(overloaded)  # reject: overload_validator_input
gloe.input() >> identity  # reject: unresolved_generic_anchor
gloe.input() >> ()  # reject: empty_inferred_fanout


async def execution() -> None:
    await root("a")  # reject: awaited_root_type
    await root()  # reject: awaited_missing_input
    await root(1, suffix=2)  # reject: awaited_keyword_type
    await gloe.Transformer(async_constant)(1)  # reject: awaited_zero_root
    pipe = gloe.input() >> increment >> text
    await pipe("1")  # reject: awaited_pipeline_input
    pipe.sync("1")  # reject: blocking_pipeline_input
    answer: int = await pipe(1)  # reject: awaited_output_type
    pending: str = pipe(1)  # reject: missing_await
    print(answer, pending)


def union_callable(stage: Callable[[int], int] | Callable[..., str]) -> None:
    gloe.input[int]() >> stage  # reject: union_erased_callable


def union_partial(stage: Callable[[int], int] | partial[str]) -> None:
    gloe.input[int]() >> stage  # reject: union_erased_partial


gloe.filter(untyped_result)  # reject: unknown_predicate_output
gloe.condition(  # reject: unknown_condition_predicate
    untyped_result, then=increment, otherwise=increment
)
