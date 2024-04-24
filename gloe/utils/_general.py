import sys
from typing import Any, TypeVar, Generic, Iterable
from gloe.functional import transformer
from gloe.transformers import Transformer

_In = TypeVar("_In")
_Out = TypeVar("_Out")


@transformer
def forget(data: Any) -> None:
    """Transform any input data to `None`"""
    return None


class debug(Generic[_In], Transformer[_In, _In]):
    def __init__(self):
        super().__init__()
        self.plotting_settings.invisible = True

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
        self.plotting_settings.invisible = True

    def transform(self, data: _In) -> _In:
        return data


class bypass(Generic[_In], Transformer[_In, _In]):
    def __init__(self, transformer: Transformer[_In, Any]):
        super().__init__()
        self.transformer = transformer
        self.plotting_settings.invisible = True

    def transform(self, data: _In) -> _In:
        self.transformer(data)
        return data


def forward_incoming(
    inner_transformer: Transformer[_In, _Out]
) -> Transformer[_In, tuple[_Out, _In]]:
    return forward[_In]() >> (inner_transformer, forward())


class flatten(Transformer[Iterable[_In | Iterable[_In]], Iterable[_In]]):
    def transform(self, nested_list: Iterable[_In | Iterable[_In]]) -> Iterable[_In]:
        flat_list = []
        for inner_item in nested_list:
            if isinstance(inner_item, Iterable):
                if isinstance(inner_item, list):
                    flat_list += inner_item
                else:
                    flat_list += list(inner_item)
            else:
                flat_list.append(inner_item)
        return flat_list
