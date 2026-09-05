"""Composition must fail closed when the checker plugin is absent."""

from gloe import input


def increment(value: int) -> int:
    return value + 1


input[int]() >> increment  # reject: plugin_missing
