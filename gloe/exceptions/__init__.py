from typing import Any

__all__ = ["UnsupportedTransformerArgException"]


class UnsupportedTransformerArgException(Exception):
    def __init__(self, arg: Any):
        super().__init__(f"Unsupported transformer argument: {arg}")


class UnsupportedEnsurerArgException(Exception):
    def __init__(self, arg: Any):
        super().__init__(f"Unsupported ensurer argument: {arg}")
