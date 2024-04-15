import traceback

from gloe.base_transformer import BaseTransformer, TransformerException


def catch_transformer_exception(
    exception: Exception, raiser_transformer: BaseTransformer
) -> TransformerException:
    transformer_name = raiser_transformer.__class__.__name__
    if type(exception.__cause__) == TransformerException:
        transform_exception = exception.__cause__
    else:
        tb = traceback.extract_tb(exception.__traceback__)

        # TODO: Make this filter condition stronger
        transformer_frames = [
            frame
            for frame in tb
            if frame.name == transformer_name or frame.name == "transform"
        ]

        if len(transformer_frames) == 1:
            transformer_frame = transformer_frames[0]
            exception_message = (
                f"\n  "
                f'File "{transformer_frame.filename}", line {transformer_frame.lineno}, '
                f'in transformer "{transformer_name}"\n  '
                f"  >> {transformer_frame.line}"
            )
        else:
            exception_message = f'An error occurred in transformer "{transformer_name}"'

        transform_exception = TransformerException(
            internal_exception=exception,
            raiser_transformer=raiser_transformer,
            message=exception_message,
        )
    return transform_exception
