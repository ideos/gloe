from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class NodeType(Enum):
    Transformer = "Transformer"
    Begin = "Begin"
    End = "End"
    ConditionBegin = "ConditionBegin"
    ConditionEnd = "ConditionEnd"
    ParallelGatewayBegin = "ParallelGatewayBegin"
    ParallelGatewayEnd = "ParallelGatewayEnd"


@dataclass
class GatewaySettings:
    extra_labels: list[str] = field(default_factory=list)


@dataclass
class PlottingSettings:
    node_type: NodeType
    has_children: bool = False
    invisible: bool = False
    is_async: bool = False
    is_gateway: bool = False
    gateway_settings: Optional[GatewaySettings] = None
    parent_id: Optional[str] = None


def dot_props(node_type: NodeType) -> dict[str, Any]:
    node_props: dict[str, Any] = {"shape": "box"}

    if node_type == NodeType.ConditionBegin:
        node_props = {"shape": "diamond", "style": "filled", "port": "n"}
    elif node_type == NodeType.ConditionEnd:
        node_props = {
            "shape": "diamond",
            "style": "filled",
            "port": "n",
            "width": 0.4,
            "height": 0.4,
        }
    elif node_type == NodeType.ParallelGatewayBegin:
        node_props = {"shape": "diamond", "width": 0.4, "height": 0.4, "label": ""}
    elif node_type == NodeType.ParallelGatewayEnd:
        node_props = {"shape": "diamond", "width": 0.4, "height": 0.4, "label": ""}
    elif node_type == NodeType.Begin:
        node_props = {"shape": "circle", "width": 0.3, "height": 0.3, "label": ""}
    elif node_type == NodeType.End:
        node_props = {"shape": "doublecircle", "width": 0.2, "height": 0.2, "label": ""}

    return node_props
