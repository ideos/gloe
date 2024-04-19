from contextvars import ContextVar
from typing import Generic, TypeVar

from gloe.transformers import Transformer

T = TypeVar("T")
B = TypeVar("B")


class EmptyBridgeOnDrop(Exception):
    def __init__(self, bridge_name: str):
        super().__init__(
            f"The bridge {bridge_name} has tried to be dropped but its value was not"
            "initialized"
        )


class _pick(Generic[T], Transformer[T, T]):
    def __init__(self, variable: ContextVar[T]):
        super().__init__()
        self.plotting_settings.invisible = True
        self.variable = variable

    def transform(self, data: T) -> T:
        self.variable.set(data)
        return data


class _drop(Generic[B, T], Transformer[B, tuple[B, T]]):
    def __init__(self, variable: ContextVar[T]):
        super().__init__()
        self.plotting_settings.invisible = True
        self._variable = variable

    def transform(self, data: B) -> tuple[B, T]:
        current_value: T
        try:
            current_value = self._variable.get()
        except LookupError:
            raise EmptyBridgeOnDrop(self._variable.name)
        return data, current_value


class bridge(Generic[T]):
    def __init__(self, name: str):
        self._variable: ContextVar[T] = ContextVar(name)

    def pick(self) -> Transformer[T, T]:
        return _pick(self._variable)

    def drop(self) -> Transformer[B, tuple[B, T]]:
        drop: _drop[B, T] = _drop(self._variable)
        return drop
