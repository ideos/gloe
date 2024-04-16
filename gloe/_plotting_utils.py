from dataclasses import dataclass
from enum import Enum
from typing import Optional


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
