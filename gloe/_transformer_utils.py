import traceback
from inspect import Signature

from gloe._typing_utils import _match_types, _specify_types
from gloe.base_transformer import BaseTransformer, TransformerException


def catch_transformer_exception(
    exception: Exception, raiser_transformer: BaseTransformer
) -> TransformerException:
    transformer_name = raiser_transformer.__class__.__name__
    tb = traceback.extract_tb(exception.__traceback__)

    # TODO: Make this filter condition stronger
    transformer_frames = [
        frame
        for frame in tb
        if frame.name == transformer_name
        or frame.name in ["transform", "transform_async"]
    ]

    if len(transformer_frames) >= 1:
        transformer_frame = transformer_frames[-1]
        exception_message = (
            f"\n  "
            f'File "{transformer_frame.filename}", line {transformer_frame.lineno},'
            f' in transformer "{transformer_name}"\n  '
            f"  >> {transformer_frame.line}"
        )

        transform_exception = TransformerException(
            internal_exception=exception,
            raiser_transformer=raiser_transformer,
            message=exception_message,
        )
        return transform_exception

    raise NotImplementedError(
        "This exception was not raised by a transformer"
    )  # pragma: no cover


def _diverging_signatures(
    prev_signature: Signature, *transformers: BaseTransformer
) -> list[Signature]:
    next_signatures: list[Signature] = []

    for receiving_transformer in transformers:
        generic_vars = _match_types(
            receiving_transformer.input_type, prev_signature.return_annotation
        )

        receiving_signature = receiving_transformer.signature()
        return_annotation = receiving_signature.return_annotation

        new_return_annotation = _specify_types(return_annotation, generic_vars)

        new_signature = receiving_signature.replace(
            return_annotation=new_return_annotation
        )
        next_signatures.append(new_signature)

    return next_signatures
