from gloe._composition_utils import _compose_nodes
from gloe.functional import (
    transformer,
    partial_transformer,
    partial_async_transformer,
    async_transformer,
)
from gloe.conditional import If, condition
from gloe.ensurer import ensure
from gloe.exceptions import UnsupportedTransformerArgException
from gloe.transformers import Transformer
from gloe.base_transformer import BaseTransformer, PreviousTransformer
from gloe.base_transformer import TransformerException
from gloe.async_transformer import AsyncTransformer

__version__ = "0.6.0-rc0"

__all__ = [
    "transformer",
    "partial_transformer",
    "partial_async_transformer",
    "async_transformer",
    "If",
    "condition",
    "ensure",
    "UnsupportedTransformerArgException",
    "BaseTransformer",
    "PreviousTransformer",
    "Transformer",
    "TransformerException",
    "AsyncTransformer",
]

setattr(Transformer, "__rshift__", _compose_nodes)
setattr(AsyncTransformer, "__rshift__", _compose_nodes)
