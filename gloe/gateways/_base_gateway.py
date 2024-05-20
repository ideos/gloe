from inspect import Signature
from types import GenericAlias
from typing import Any

from typing_extensions import Generic

from gloe._generic_types import *
from gloe._transformer_utils import _diverging_signatures
from gloe.base_transformer import BaseTransformer

_In = TypeVar("_In")


class _base_gateway(Generic[_In], BaseTransformer[_In, Any]):
    def __init__(
        self, prev_signature: Signature, *transformers: BaseTransformer[_In, Any]
    ):
        super().__init__()
        self._children = list(transformers)
        self._prev_signature = prev_signature
        self._plotting_settings.is_gateway = True
        self._receiving_signatures = _diverging_signatures(
            prev_signature, *transformers
        )

    def signature(self) -> Signature:
        receiving_signature_returns = [
            r.return_annotation for r in self._receiving_signatures
        ]
        new_signature = self._prev_signature.replace(
            return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns))
        )
        return new_signature
