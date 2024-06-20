import sys
import uuid
from inspect import Signature
from types import GenericAlias

from gloe.base_transformer import BaseTransformer
from gloe.conditional._implication import _BaseImplication

if sys.version_info >= (3, 10):
    from types import UnionType
from typing import (
    Callable,
    Generic,
    TypeVar,
    Union,
    Sequence,
    Optional,
    cast,
)

from typing_extensions import Self

from gloe._gloe_graph import GloeGraph
from gloe._plotting_utils import PlottingSettings, NodeType, dot_props
from gloe.base_transformer import GloeNode


In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)
ElseOut = TypeVar("ElseOut")
ElseIfOut = TypeVar("ElseIfOut")
PrevThenOut = TypeVar("PrevThenOut")


class BaseConditioner(
    Generic[In, ThenOut, ElseOut], BaseTransformer[In, Union[ThenOut, ElseOut]]
):
    def __init__(
        self,
        implications: Sequence[_BaseImplication[In, ThenOut]],
        else_transformer: BaseTransformer[In, ElseOut],
    ):
        super().__init__()
        self.implications = implications
        self.else_transformer = else_transformer
        self._plotting_settings = PlottingSettings(
            NodeType.Transformer, has_children=True, is_gateway=True
        )
        self._children = [
            *[impl.then_transformer for impl in implications],
            else_transformer,
        ]

    def signature(self) -> Signature:
        else_signature: Signature = self.else_transformer.signature()
        return_signature: list[Signature] = [
            impl.then_transformer.signature().return_annotation
            for impl in self.implications
        ] + [else_signature.return_annotation]

        union_type: type = cast(type, Union)
        if sys.version_info >= (3, 10):
            union_type = UnionType
        new_signature = else_signature.replace(
            return_annotation=GenericAlias(
                union_type,
                tuple(return_signature),
            )
        )
        return new_signature

    def copy(
        self,
        transform: Optional[Callable[[Self, In], Union[ThenOut, ElseOut]]] = None,
        regenerate_instance_id: bool = False,
        force: bool = False,
    ) -> Self:
        copied: Self = super().copy(transform, regenerate_instance_id, force)
        copied.implications = [impl.copy() for impl in copied.implications]
        copied.else_transformer = self.else_transformer.copy(
            regenerate_instance_id=True
        )
        copied._children = [
            *[impl.then_transformer for impl in copied.implications],
            copied.else_transformer,
        ]
        return copied

    def __len__(self):
        then_transformers_len = [
            len(impl.then_transformer) for impl in self.implications
        ]
        return sum(then_transformers_len) + len(self.else_transformer)

    def _dag(
        self,
        net: GloeGraph,
        root_node: GloeNode,
    ) -> GloeNode:
        in_converge_id = str(uuid.uuid4())
        label = self.__class__.__name__
        in_converge = GloeNode(
            id=in_converge_id,
            input_annotation=self.input_annotation,
            output_annotation="",
        )

        net.add_node(
            in_converge_id,
            label=label,
            _label=label,
            **dot_props(NodeType.ConditionBegin),
        )

        net.add_edge(
            root_node.id,
            in_converge_id,
            label=self.input_annotation,
            ltail=root_node.ltail,
        )

        last_nodes = []
        for child_node in self.children:
            last_node = child_node._dag(net, in_converge)
            last_nodes.append(last_node)

        out_converge_id = str(uuid.uuid4())
        net.add_node(
            out_converge_id,
            label="",
            _label=f"{label}_end",
            **dot_props(NodeType.ConditionEnd),
        )
        out_converge = GloeNode(
            id=out_converge_id,
            input_annotation=self.input_annotation,
            output_annotation="",
        )

        for last_node in last_nodes:
            net.add_edge(
                last_node.id,
                out_converge_id,
                label=last_node.output_annotation,
                ltail=last_node.ltail,
            )
        return out_converge
