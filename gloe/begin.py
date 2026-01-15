from typing import Any, Generic, Protocol, TypeVar, overload

from typing_extensions import TypeVarTuple, Unpack

from gloe.exceptions import TransformerRequiresMultiArgs
from gloe.transformers import MultiArgsTransformer, Transformer

__all__ = ["begin"]

_In = TypeVar("_In")
_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")

Args = TypeVarTuple("Args")


class _BeginSingle(Generic[_In], Transformer[_In, _In]):
    def __init__(self):
        super().__init__()
        self.plotting_settings.invisible = True

    def transform(self, data: _In) -> _In:
        return data


class _BeginMultiArgs(
    Generic[Unpack[Args]], MultiArgsTransformer[Unpack[Args], tuple[Unpack[Args]]]
):
    def __init__(self):
        super().__init__()
        self.plotting_settings.invisible = True

    def transform(self, data: tuple[Unpack[Args]]) -> tuple[Unpack[Args]]:
        if type(data) is tuple:
            if len(data) == 1:
                raise TransformerRequiresMultiArgs()
            return data
        raise NotImplementedError()  # pragma: no cover


class _BeginSingleFactory(Generic[_In]):
    def __call__(self) -> Transformer[_In, _In]:
        return _BeginSingle()


class _BeginMultiFactory(Generic[Unpack[Args]]):
    def __call__(self) -> MultiArgsTransformer[Unpack[Args], tuple[Unpack[Args]]]:
        return _BeginMultiArgs()


class _Begin(Protocol):
    def __call__(self) -> Transformer[Any, Any]:
        pass

    @overload
    def __getitem__(self, item: type[_In]) -> _BeginSingleFactory[_In]:
        pass

    @overload
    def __getitem__(self, item: tuple[type[_A], type[_B]]) -> _BeginMultiFactory[_A, _B]:
        pass

    @overload
    def __getitem__(
        self, item: tuple[type[_A], type[_B], type[_C]]
    ) -> _BeginMultiFactory[_A, _B, _C]:
        pass

    @overload
    def __getitem__(
        self, item: tuple[type[_A], type[_B], type[_C], type[_D]]
    ) -> _BeginMultiFactory[_A, _B, _C, _D]:
        pass

    @overload
    def __getitem__(
        self, item: tuple[type[_A], type[_B], type[_C], type[_D], type[_E]]
    ) -> _BeginMultiFactory[_A, _B, _C, _D, _E]:
        pass

    @overload
    def __getitem__(
        self, item: tuple[type[_A], type[_B], type[_C], type[_D], type[_E], type[_F]]
    ) -> _BeginMultiFactory[_A, _B, _C, _D, _E, _F]:
        pass

    @overload
    def __getitem__(
        self,
        item: tuple[
            type[_A],
            type[_B],
            type[_C],
            type[_D],
            type[_E],
            type[_F],
            type[_G],
        ],
    ) -> _BeginMultiFactory[_A, _B, _C, _D, _E, _F, _G]:
        pass


class _BeginImpl:
    def __call__(self) -> Transformer[Any, Any]:
        return _BeginSingle()

    def __getitem__(self, item: object) -> Any:
        if isinstance(item, tuple):
            if len(item) <= 1:
                return _BeginSingleFactory()
            return _BeginMultiFactory()
        return _BeginSingleFactory()


begin: _Begin = _BeginImpl()
