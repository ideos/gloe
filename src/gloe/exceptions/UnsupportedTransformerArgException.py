from typing import Any


class UnsupportedTransformerArgException(Exception):
    def __init__(self, arg: Any):
        super().__init__(f"Unsupported transformer argument: {arg}")
