from inspect import Signature
from typing import get_args, get_origin


def validate_mapover_signature(
    signature: Signature, name: str, map_name: str
) -> None:
    params = list(signature.parameters.values())
    if len(params) == 0:
        raise TypeError(
            f"{name} mapping transformer must accept extra arguments plus the item."
        )
    if len(params) == 1:
        annotation = params[0].annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is not tuple:
            raise TypeError(
                f"{name} mapping transformer must accept a tuple of (extra, item). "
                f"Use {map_name} for single-argument mapping."
            )
        if len(args) == 1 and args[0] is not ...:
            raise TypeError(
                f"{name} mapping transformer tuple must include the extra argument "
                "and the item."
            )
