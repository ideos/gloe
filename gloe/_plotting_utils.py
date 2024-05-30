from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from uuid import UUID


class NodeType(Enum):
    Transformer = "Transformer"
    Begin = "Begin"
    End = "End"
    Condition = "Condition"
    Convergent = "Convergent"


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


def export_dot_props(settings: PlottingSettings, instance_id: UUID) -> dict[str, Any]:
    node_props: dict[str, Any] = {"shape": "box"}

    if settings.node_type == NodeType.Condition:
        node_props = {"shape": "diamond", "style": "filled", "port": "n"}
    elif settings.node_type == NodeType.Convergent:
        node_props = {
            "shape": "diamond",
            "width": 0.5,
            "height": 0.5,
        }

    if settings.has_children:
        node_props = node_props | {
            "parent_id": instance_id,
            "bounding_box": True,
            "box_label": "mapping",
        }

    return node_props
