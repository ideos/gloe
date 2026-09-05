"""Malformed annotations must produce diagnostics, never crash the plugin."""

from typing import overload

import gloe


@overload
def malformed(*values: int) -> int: ...


@overload
def malformed(*values: int) -> str: ...  # reject: overlapping_variadic_overload


def malformed(*values: int) -> int | str:
    return 1


gloe.transformer(malformed)  # reject: malformed_factory_signature
