import uuid
from inspect import Signature
from types import GenericAlias
from typing import Any

from typing_extensions import Generic

from gloe._generic_types import *
from gloe._plotting_utils import GloeGraph
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

    def _dag(
        self,
        net: GloeGraph,
        root_node: Union[str, "BaseTransformer"],
    ) -> Union[str, "BaseTransformer"]:
        in_converge_id = str(uuid.uuid4())
        net.add_node(in_converge_id, label="", _label="gateway_begin", shape="diamond")

        if isinstance(root_node, str):
            net.add_edge(root_node, in_converge_id, label=self.input_annotation)
        else:
            net.add_edge(
                root_node.node_id,
                in_converge_id,
                label=self.input_annotation,
            )

        last_nodes = []
        for child_node in self.children:
            last_node = child_node._dag(net, in_converge_id)
            last_nodes.append(last_node)

        out_converge_id = str(uuid.uuid4())
        net.add_node(out_converge_id, label="", _label="gateway_end", shape="diamond")

        for last_node in last_nodes:
            if isinstance(last_node, str):
                net.add_edge(last_node, out_converge_id, label=self.output_annotation)
            else:
                net.add_edge(
                    last_node.node_id,
                    out_converge_id,
                    label=last_node.output_annotation,
                )
        return out_converge_id
