from gloe._composition_utils import _compose_nodes
from gloe.functional import transformer, partial_transformer, async_transformer
from gloe.conditional import If, ConditionerTransformer, conditioner
from gloe.ensurer import ensure
from gloe.exceptions import UnsupportedTransformerArgException
from gloe.transformers import Transformer
from gloe.base_transformer import TransformerException
from gloe.async_transformer import AsyncTransformer

setattr(Transformer, "__rshift__", _compose_nodes)
setattr(AsyncTransformer, "__rshift__", _compose_nodes)
