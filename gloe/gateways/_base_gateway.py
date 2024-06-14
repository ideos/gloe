import uuid
from inspect import Signature, Parameter
from types import GenericAlias
from typing import Any, TypeVar

from typing_extensions import Generic

from gloe._gloe_graph import GloeGraph
from gloe._plotting_utils import dot_props, NodeType
from gloe._transformer_utils import _diverging_signatures
from gloe.base_transformer import BaseTransformer, GloeNode

_In = TypeVar("_In")


class _base_gateway(Generic[_In], BaseTransformer[_In, Any]):
    def __init__(self, *transformers: BaseTransformer[_In, Any]):
        super().__init__()
        self._children = list(transformers)
        self._plotting_settings.is_gateway = True

        input_annotations = [t.input_annotation for t in transformers]
        all_same_input = len(set(input_annotations)) == 1
        annotation = (
            input_annotations[0]
            if all_same_input
            else GenericAlias(tuple, tuple(t.input_annotation for t in transformers))
        )
        self._prev_signature = Signature(
            parameters=[
                Parameter(
                    "data",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=annotation,
                )
            ]
        )
        self._receiving_signatures = _diverging_signatures(
            self._prev_signature, *transformers
        )

    def signature(self) -> Signature:
        receiving_signature_returns = [
            r.return_annotation for r in self._receiving_signatures
        ]
        new_signature = self._prev_signature.replace(
            return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns))
        )
        return new_signature

    def _dag(self, net: GloeGraph, root_node: GloeNode) -> GloeNode:
        in_converge_id = str(uuid.uuid4())
        in_converge = GloeNode(
            id=in_converge_id,
            input_annotation=self.input_annotation,
            output_annotation="",
        )
        net.add_node(
            in_converge_id,
            _label="gateway_begin",
            **dot_props(NodeType.ParallelGatewayBegin),
        )

        net.add_edge(
            root_node.id,
            in_converge_id,
            label=root_node.output_annotation,
            ltail=root_node.ltail,
        )

        last_nodes = []
        for child_node in self.children:
            last_node = child_node._dag(net, in_converge)
            last_nodes.append(last_node)

        out_converge_id = str(uuid.uuid4())
        out_converge = GloeNode(
            id=out_converge_id,
            input_annotation=self.input_annotation,
            output_annotation="",
        )
        net.add_node(
            out_converge_id,
            _label="gateway_end",
            **dot_props(NodeType.ParallelGatewayEnd),
        )

        for last_node in last_nodes:
            net.add_edge(
                last_node.id,
                out_converge_id,
                label=last_node.output_annotation,
                ltail=last_node.ltail,
            )
        return out_converge
