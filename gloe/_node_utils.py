import inspect
from typing import Any, Callable, Union

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.exceptions import UnsupportedTransformerArgException
from gloe.functional import async_transformer, transformer
from gloe.transformers import Transformer


def _coerce_transformer(
    node: Union[BaseTransformer, Callable[..., Any]]
) -> Transformer[Any, Any] | AsyncTransformer[Any, Any]:
    if isinstance(node, BaseTransformer):
        if isinstance(node, AsyncTransformer):
            return node
        if isinstance(node, Transformer):
            return node
        raise UnsupportedTransformerArgException(node)
    if callable(node):
        if inspect.iscoroutinefunction(node):
            return async_transformer(node)
        return transformer(node)
    raise UnsupportedTransformerArgException(node)


def _coerce_sync_transformer(
    node: Union[BaseTransformer, Callable[..., Any]]
) -> Transformer:
    transformer_node = _coerce_transformer(node)
    if isinstance(transformer_node, AsyncTransformer):
        raise UnsupportedTransformerArgException(node)
    if not isinstance(transformer_node, Transformer):
        raise UnsupportedTransformerArgException(node)
    return transformer_node
