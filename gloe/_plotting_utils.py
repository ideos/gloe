from dataclasses import dataclass
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
class PlottingSettings:
    node_type: NodeType
    has_children: bool = False
    invisible: bool = False
    is_async: bool = False
    parent_id: Optional[str] = None


def export_dot_props(settings: PlottingSettings, instance_id: UUID) -> dict[str, Any]:
    node_props: dict[str, Any] = {"shape": "box"}

    match settings.node_type:
        case NodeType.Condition:
            node_props = {"shape": "diamond", "style": "filled", "port": "n"}
        case NodeType.Convergent:
            node_props = {
                "shape": "diamond",
                "width": 0.5,
                "height": 0.5,
            }
        case _:
            pass

    if settings.has_children:
        node_props = node_props | {
            "parent_id": instance_id,
            "bounding_box": True,
            "box_label": "mapping",
        }

    return node_props
