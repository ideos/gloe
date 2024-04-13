import asyncio
import types
from inspect import Signature
from types import GenericAlias
from typing import TypeVar, Any, cast

from gloe.async_transformer import AsyncTransformer
from gloe.base_transformer import BaseTransformer
from gloe.transformers import Transformer
from gloe._typing_utils import _match_types, _specify_types
from gloe.exceptions import UnsupportedTransformerArgException

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_NextOut = TypeVar("_NextOut")


def is_transformer(node):
    if type(node) == list or type(node) == tuple:
        return all(is_transformer(n) for n in node)
    return isinstance(node, Transformer)


def is_async_transformer(node):
    return isinstance(node, AsyncTransformer)


def _resolve_new_merge_transformers(
    new_transformer: BaseTransformer, transformer2: BaseTransformer
):
    new_transformer.__class__.__name__ = transformer2.__class__.__name__
    new_transformer._label = transformer2.label
    new_transformer._children = transformer2.children
    new_transformer._invisible = transformer2.invisible
    new_transformer._graph_node_props = transformer2.graph_node_props
    new_transformer._set_previous(transformer2.previous)
    return new_transformer


def _resolve_serial_connection_signatures(
    transformer2: BaseTransformer, generic_vars: dict, signature2: Signature
) -> Signature:
    first_param = list(signature2.parameters.values())[0]
    new_parameter = first_param.replace(
        annotation=_specify_types(transformer2.input_type, generic_vars)
    )
    new_signature = signature2.replace(
        parameters=[new_parameter],
        return_annotation=_specify_types(signature2.return_annotation, generic_vars),
    )
    return new_signature


def _nerge_serial(transformer1, _transformer2):
    if transformer1.previous is None:
        transformer1 = transformer1.copy(regenerate_instance_id=True)

    transformer2 = _transformer2.copy(regenerate_instance_id=True)
    transformer2._set_previous(transformer1)

    signature1: Signature = transformer1.signature()
    signature2: Signature = transformer2.signature()

    input_generic_vars = _match_types(
        transformer2.input_type, signature1.return_annotation
    )
    output_generic_vars = _match_types(
        signature1.return_annotation, transformer2.input_type
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

    class BaseNewTransformer:
        def signature(self) -> Signature:
            return _resolve_serial_connection_signatures(
                transformer2, generic_vars, signature2
            )

        def __len__(self):
            return len(transformer1) + len(transformer2)

    new_transformer: BaseTransformer | None = None
    if is_transformer(transformer1) and is_transformer(_transformer2):

        class NewTransformer1(BaseNewTransformer, Transformer[_In, _NextOut]):
            def transform(self, data: _In) -> _NextOut:
                transformer2_call = transformer2.__call__
                transformer1_call = transformer1.__call__
                transformed = transformer2_call(transformer1_call(data))
                return transformed

        new_transformer = NewTransformer1()

    elif is_async_transformer(transformer1) and is_transformer(_transformer2):

        class NewTransformer2(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                transformer1_out = await transformer1(data)
                transformed = transformer2(transformer1_out)
                return transformed

        new_transformer = NewTransformer2()

    elif is_async_transformer(transformer1) and is_async_transformer(transformer2):

        class NewTransformer3(BaseNewTransformer, AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                transformer1_out = await transformer1(data)
                transformed = await transformer2(transformer1_out)
                return transformed

        new_transformer = NewTransformer3()

    elif is_transformer(transformer1) and is_async_transformer(_transformer2):

        class NewTransformer4(AsyncTransformer[_In, _NextOut]):
            async def transform_async(self, data: _In) -> _NextOut:
                transformer1_out = transformer1(data)
                transformed = await transformer2(transformer1_out)
                return transformed

        new_transformer = NewTransformer4()

    else:
        raise UnsupportedTransformerArgException(transformer2)  # pragma: no cover

    return _resolve_new_merge_transformers(new_transformer, transformer2)


def _merge_diverging(
    incident_transformer,
    *receiving_transformers,
):
    if incident_transformer.previous is None:
        incident_transformer = incident_transformer.copy(regenerate_instance_id=True)

    receiving_transformers = tuple(
        [
            receiving_transformer.copy(regenerate_instance_id=True)
            for receiving_transformer in receiving_transformers
        ]
    )

    for receiving_transformer in receiving_transformers:
        receiving_transformer._set_previous(incident_transformer)

    incident_signature: Signature = incident_transformer.signature()
    receiving_signatures: list[Signature] = []

    for receiving_transformer in receiving_transformers:
        generic_vars = _match_types(
            receiving_transformer.input_type, incident_signature.return_annotation
        )

        receiving_signature = receiving_transformer.signature()
        return_annotation = receiving_signature.return_annotation

        new_return_annotation = _specify_types(return_annotation, generic_vars)

        new_signature = receiving_signature.replace(
            return_annotation=new_return_annotation
        )
        receiving_signatures.append(new_signature)

        def _signature(_) -> Signature:
            return new_signature

        if receiving_transformer._previous == incident_transformer:
            setattr(
                receiving_transformer,
                "signature",
                types.MethodType(_signature, receiving_transformer),
            )

    class BaseNewTransformer:
        def signature(self) -> Signature:
            receiving_signature_returns = [
                r.return_annotation for r in receiving_signatures
            ]
            new_signature = incident_signature.replace(
                return_annotation=GenericAlias(tuple, tuple(receiving_signature_returns))
            )
            return new_signature

        def __len__(self):
            lengths = [len(t) for t in receiving_transformers]
            return sum(lengths) + len(incident_transformer)

    new_transformer = None
    if is_transformer(incident_transformer) and is_transformer(receiving_transformers):

        def split_result(data: _In) -> tuple[Any, ...]:
            intermediate_result = incident_transformer(data)

            outputs = []
            for receiving_transformer in receiving_transformers:
                output = receiving_transformer(intermediate_result)
                outputs.append(output)

            return tuple(outputs)

        class NewTransformer1(BaseNewTransformer, Transformer[_In, tuple[Any, ...]]):
            def transform(self, data: _In) -> tuple[Any, ...]:
                return split_result(data)

        new_transformer = NewTransformer1()

    else:

        async def split_result_async(data: _In) -> tuple[Any, ...]:
            if asyncio.iscoroutinefunction(incident_transformer.__call__):
                intermediate_result = await incident_transformer(data)
            else:
                intermediate_result = incident_transformer(data)

            outputs = []
            for receiving_transformer in receiving_transformers:
                if asyncio.iscoroutinefunction(receiving_transformer.__call__):
                    output = await receiving_transformer(intermediate_result)
                else:
                    output = receiving_transformer(intermediate_result)
                outputs.append(output)

            return tuple(outputs)

        class NewTransformer2(BaseNewTransformer, AsyncTransformer[_In, tuple[Any, ...]]):
            async def transform_async(self, data: _In) -> tuple[Any, ...]:
                return await split_result_async(data)

        new_transformer = NewTransformer2()

    new_transformer._previous = cast(Transformer, receiving_transformers)
    new_transformer.__class__.__name__ = "Converge"
    new_transformer._label = ""
    new_transformer._graph_node_props = {
        "shape": "diamond",
        "width": 0.5,
        "height": 0.5,
    }

    return new_transformer


def _compose_nodes(
    current: BaseTransformer,
    next_node: tuple | BaseTransformer,
):
    if issubclass(type(current), BaseTransformer):
        if issubclass(type(next_node), BaseTransformer):
            return _nerge_serial(current, next_node)  # type: ignore
        elif type(next_node) == tuple:
            is_all_base_transformers = all(
                issubclass(type(next_transformer), BaseTransformer)
                for next_transformer in next_node
            )
            if is_all_base_transformers:
                return _merge_diverging(current, *next_node)  # type: ignore

            unsupported_elem = [
                elem for elem in next_node if not isinstance(elem, BaseTransformer)
            ]
            raise UnsupportedTransformerArgException(unsupported_elem[0])
        else:
            raise UnsupportedTransformerArgException(next_node)
    else:
        raise UnsupportedTransformerArgException(next_node)  # pragma: no cover
