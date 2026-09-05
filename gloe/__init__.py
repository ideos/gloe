"""Typed, inspectable pipelines built from ordinary Python functions."""

from ._core import Transformer as Transformer, input as input
from ._functions import (
    transformer as transformer,
    map as map,
    filter as filter,
    condition as condition,
    parallel as parallel,
    sequential as sequential,
    unpack as unpack,
)
from ._validation import ensure as ensure

__version__ = "0.8.0"
__all__ = [
    "Transformer",
    "input",
    "transformer",
    "map",
    "filter",
    "condition",
    "parallel",
    "sequential",
    "unpack",
    "ensure",
]
