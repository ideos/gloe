"""Configuration factories and root-call signatures stay explicit."""

from __future__ import annotations

from functools import partial

from gloe import Transformer, input, transformer


@transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


@transformer
def render(value: int, *, prefix: str = "v") -> str:
    return prefix + str(value)


@transformer
def repeat[T](value: T, *, count: int) -> list[T]:
    return [value] * count


add()  # reject: missing_required_configuration
add(amount="2")  # reject: configuration_type
add(2)  # reject: positional_configuration
add(value=1, amount=2)  # reject: data_passed_to_factory
render(prefix=1)  # reject: optional_configuration_type
repeat(count="2")  # reject: generic_configuration_type


input[str]() >> add(amount=2)  # reject: configured_input
add(amount=2)(1, amount=3)  # reject: configuration_at_execution
input[int]() >> add  # reject: unconfigured_factory
input[int]() >> render  # reject: unconfigured_optional_factory
input[int]() >> repeat  # reject: unconfigured_generic_factory


Transformer(add)
Transformer(add).sync(1)  # reject: transformer_factory_call
Transformer(lambda value: value).sync(1)  # reject: untyped_lambda_stage


def configured(value: int, *, prefix: str) -> str:
    return prefix + str(value)


partial(configured, prefix=2)  # reject: partial_configuration_type
input[str]() >> partial(configured, prefix="v")  # reject: partial_input_type


root = Transformer(configured)
root.sync(1)  # reject: missing_root_configuration
root.sync(1, prefix=2)  # reject: root_configuration_type
root.sync("1", prefix="v")  # reject: root_input_type


@transformer  # reject: variadic_factory
def variadic(*values: int) -> int:
    return sum(values)


def constant() -> int:
    return 1


input[int]() >> constant  # reject: zero_input_stage
