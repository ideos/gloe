import types
from inspect import Signature
from typing import TypeVar, Any, Optional, Union

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.gateways._parallel import _Parallel, _ParallelAsync
from gloe.transformers import Transformer
from gloe._typing_utils import _match_types, _specify_types
from gloe.exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")


def is_transformer(node):
    if isinstance(node, list) or isinstance(node, tuple):
        return all(is_transformer(n) for n in node)
    return isinstance(node, Transformer)


def _resolve_serial_connection_signatures(
    transformer2: BaseTransformer, generic_vars: dict, signature2: Signature
) -> Signature:
    first_param = list(signature2.parameters.values())[0]
    new_parameter = first_param.replace(
        annotation=_specify_types(transformer2.input_type, generic_vars)
    )
    new_signature = signature2.replace(
        parameters=[new_parameter],
        return_annotation=_specify_types(transformer2.output_type, generic_vars),
    )
    return new_signature


def _compose_serial(transformer1, _transformer2):
    if len(transformer1) == 1:
        transformer1 = transformer1.copy(regenerate_instance_id=True)

    transformer2 = _transformer2.copy(regenerate_instance_id=True)

    signature1: Signature = transformer1.signature()
    signature2: Signature = transformer2.signature()

    input_generic_vars = _match_types(transformer2.input_type, transformer1.output_type)
    output_generic_vars = _match_types(
        transformer1.output_type, transformer2.input_type
    )
    generic_vars = {**input_generic_vars, **output_generic_vars}

    def transformer1_signature(_) -> Signature:
        return signature1.replace(
            return_annotation=_specify_types(signature1.return_annotation, generic_vars)
        )

    setattr(
        transformer1,
        "signature",
        types.MethodType(transformer1_signature, transformer1),
    )

    new_len = len(transformer1) + len(transformer2)

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return _resolve_serial_connection_signatures(
                transformer2, generic_vars, signature2
            )

        def __len__(self):
            return new_len

    new_transformer: Optional[BaseTransformer] = None
    if is_transformer(transformer1) and is_transformer(transformer2):

        class NewTransformer1(BaseNewTransformer, Transformer[_In, _NextOut]):
            def __init__(self):
                super().__init__()
                self._flow = transformer1._flow + transformer2._flow

            def transform(self, data):
                return None

        new_transformer = NewTransformer1()

    else:

        class NewTransformer2(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            def __init__(self):
                super().__init__()
                self._flow = transformer1._flow + transformer2._flow

            async def transform_async(self, data):
                return None

        new_transformer = NewTransformer2()

    new_transformer.__class__.__name__ = transformer2.__class__.__name__
    new_transformer._label = transformer2.label
    new_transformer._children = transformer2.children
    new_transformer._plotting_settings = transformer2._plotting_settings
    # new_transformer._set_previous(transformer2.previous)
    return new_transformer


def _compose_diverging(
    incident_transformer,
    *receiving_transformers,
):
    if len(incident_transformer) == 1:
        incident_transformer = incident_transformer.copy(regenerate_instance_id=True)

    receiving_transformers = tuple(
        [
            receiving_transformer.copy(regenerate_instance_id=True)
            for receiving_transformer in receiving_transformers
        ]
    )

    class BaseNewTransformer:

        def __len__(self):
            lengths = [len(t) for t in receiving_transformers]
            return sum(lengths) + len(incident_transformer)

    new_transformer: Optional[BaseTransformer] = None

    if is_transformer(incident_transformer) and is_transformer(receiving_transformers):

        class NewTransformer1(BaseNewTransformer, Transformer[_In, tuple[Any, ...]]):
            def __init__(self):
                super().__init__()
                self._flow = incident_transformer._flow + [
                    _Parallel(*receiving_transformers)
                ]

            def transform(self, data):
                return None

        new_transformer = NewTransformer1()

    else:

        class NewTransformer2(
            BaseNewTransformer, AsyncTransformer[_In, tuple[Any, ...]]
        ):
            def __init__(self):
                super().__init__()
                self._flow = incident_transformer._flow + [
                    _ParallelAsync(*receiving_transformers)
                ]

            async def transform_async(self, data):
                return None

        new_transformer = NewTransformer2()

    # new_transformer._previous = cast(Transformer, receiving_transformers)
    new_transformer.__class__.__name__ = "Converge"
    new_transformer._label = ""

    return new_transformer


def _compose_nodes(
    current: BaseTransformer,
    next_node: Union[tuple, BaseTransformer],
):
    if issubclass(type(current), BaseTransformer):
        if issubclass(type(next_node), BaseTransformer):
            return _compose_serial(current, next_node)
        elif type(next_node) is tuple:
            is_all_base_transformers = all(
                issubclass(type(next_transformer), BaseTransformer)
                for next_transformer in next_node
            )
            if is_all_base_transformers:
                return _compose_diverging(current, *next_node)

            unsupported_elem = [
                elem for elem in next_node if not isinstance(elem, BaseTransformer)
            ]
            raise UnsupportedTransformerArgException(unsupported_elem[0])
        else:
            raise UnsupportedTransformerArgException(next_node)
    else:
        raise UnsupportedTransformerArgException(next_node)  # pragma: no cover
