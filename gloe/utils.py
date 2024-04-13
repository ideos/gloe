import inspect
import sys
from typing import Any, Tuple, TypeVar, Generic

from gloe.functional import transformer
from gloe.transformers import Transformer

__all__ = ["forget", "debug", "forward", "forward_incoming"]

_In = TypeVar("_In")
_Out = TypeVar("_Out")


@transformer
def forget(data: Any) -> None:
    """Transform any input data to `None`"""
    return None


class debug(Generic[_In], Transformer[_In, _In]):
    def __init__(self, custom_debugger: str | None = None):
        super().__init__()
        self._invisible = True
        self._possible_debuggers = ["pdb", "pydevd", "pydevd_runpy"]
        if custom_debugger is not None:
            self._possible_debuggers.append(custom_debugger)

    def _is_under_debug(self):
        if hasattr(sys, "gettrace") and sys.gettrace() is not None:
            trace = sys.gettrace()
            if hasattr(trace, "_args"):
                return True
        return False

    def transform(self, data: _In) -> _In:
        """
        Drops the user into the debugger when the pipeline execution reaches this
        transformer.

        In the debug console, the user will see the output of the previous transformer.
        """
        if self._is_under_debug():
            self._debugging(data)
        return data

    def _debugging(self, current_data: _In):
        breakpoint()


class forward(Generic[_In], Transformer[_In, _In]):
    def __init__(self):
        super().__init__()
        self._invisible = True

    def transform(self, data: _In) -> _In:
        return data


def forward_incoming(
    inner_transformer: Transformer[_In, _Out]
) -> Transformer[_In, Tuple[_Out, _In]]:
    return forward[_In]() >> (inner_transformer, forward())
