import inspect
import warnings
from abc import abstractmethod
from types import FunctionType
from typing import Any, \
    Callable, \
    Generic, \
    ParamSpec, \
    Sequence, \
    TypeVar, \
    cast, \
    overload

from .transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")
_P1 = ParamSpec("_P1")


class TransformerEnsurer(Generic[_T, _S]):

    @abstractmethod
    def validate_input(self, data: _T):
        pass

    @abstractmethod
    def validate_output(self, data: _T, output: _S):
        pass

    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:

        def transform(this: Transformer, data: _T) -> _S:
            self.validate_input(data)
            output = transformer.transform(data)
            self.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp


def input_ensurer(func: Callable[[_T], Any]) -> TransformerEnsurer[_T, Any]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformer Ensurer. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaEnsurer(TransformerEnsurer[_T, _S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: _T):
            func(data)

        def validate_output(self, data: _T, output: _S):
            pass

    return LambdaEnsurer()


@overload
def output_ensurer(func: Callable[[_T, _S], Any]) -> TransformerEnsurer[_T, _S]:
    pass


@overload
def output_ensurer(func: Callable[[_S], Any]) -> TransformerEnsurer[Any, _S]:
    pass


def output_ensurer(func: Callable):
    class LambdaEnsurer(TransformerEnsurer):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data):
            pass

        def validate_output(self, data, output):
            if len(inspect.signature(func).parameters) == 1:
                func(output)
            else:
                func(data, output)

    return LambdaEnsurer()


class _ensure_incoming(Generic[_T]):
    def __init__(self, incoming: Sequence[Callable[[_T], Any]]):
        self.input_ensurers_instances = [
            input_ensurer(ensurer) for ensurer in incoming
        ]

    @overload
    def __call__(self, transformer: Transformer[_T, _U]) -> Transformer[_T, _U]:
        pass

    @overload
    def __call__(
        self, transformer_init: Callable[_P1, Transformer[_T, _U]]
    ) -> Callable[_P1, Transformer[_T, _U]]:
        pass

    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        else:
            transformer_init = arg

            def ensured_transformer_init(*args, **kwargs):
                transformer = transformer_init(*args, **kwargs)
                return self._generate_new_transformer(transformer)

            return ensured_transformer_init

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(data)
            output = transformer.transform(data)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp


class _ensure_outcome(Generic[_S]):
    def __init__(self, incoming: Sequence[Callable[[_S], Any]]):
        self.output_ensurers_instances = [
            output_ensurer(ensurer) for ensurer in incoming
        ]

    @overload
    def __call__(self, transformer: Transformer[_U, _S]) -> Transformer[_U, _S]:
        pass

    @overload
    def __call__(
        self, transformer_init: Callable[_P1, Transformer[_U, _S]]
    ) -> Callable[_P1, Transformer[_U, _S]]:
        pass

    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        else:
            transformer_init = arg

            def ensured_transformer_init(*args, **kwargs):
                transformer = transformer_init(*args, **kwargs)
                return self._generate_new_transformer(transformer)

            return ensured_transformer_init

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            output = transformer.transform(data)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)

        return transformer_cp


class _ensure_changes(Generic[_T, _S]):
    def __init__(self, changes: Sequence[Callable[[_T, _S], Any]]):
        self.changes_ensurers_instances = [
            output_ensurer(ensurer) for ensurer in changes
        ]

    @overload
    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        pass

    @overload
    def __call__(
        self, transformer_init: Callable[_P1, Transformer[_T, _S]]
    ) -> Callable[_P1, Transformer[_T, _S]]:
        pass

    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        else:
            transformer_init = arg

            def ensured_transformer_init(*args, **kwargs):
                transformer = transformer_init(*args, **kwargs)
                return self._generate_new_transformer(transformer)

            return ensured_transformer_init

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            output = transformer.transform(data)
            for ensurer in self.changes_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)

        return transformer_cp


class _ensure_both(Generic[_T, _S]):

    def __init__(
        self,
        incoming: Sequence[Callable[[_T], Any]],
        outcome: Sequence[Callable[[_S], Any]],
        changes: Sequence[Callable[[_T, _S], Any]]
    ):
        incoming_seq = incoming if type(incoming) == list else [incoming]
        self.input_ensurers_instances = [
            input_ensurer(ensurer) for ensurer in incoming_seq
        ]

        outcome_seq = outcome if type(outcome) == list else [outcome]
        self.output_ensurers_instances = [
            output_ensurer(ensurer) for ensurer in outcome_seq
        ]

        changes_seq = changes if type(changes) == list else [changes]
        self.output_ensurers_instances = self.output_ensurers_instances + [
            output_ensurer(ensurer) for ensurer in changes_seq
        ]

    @overload
    def __call__(self, transformer: Transformer[_T, _S]) -> Transformer[_T, _S]:
        pass

    @overload
    def __call__(
        self, transformer_init: Callable[_P1, Transformer[_T, _S]]
    ) -> Callable[_P1, Transformer[_T, _S]]:
        pass

    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        else:
            transformer_init = arg

            def ensured_transformer_init(*args, **kwargs):
                transformer = transformer_init(*args, **kwargs)
                return self._generate_new_transformer(transformer)

            return ensured_transformer_init

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        def transform(_, data):
            for ensurer in self.input_ensurers_instances:
                ensurer.validate_input(data)
            output = transformer.transform(data)
            for ensurer in self.output_ensurers_instances:
                ensurer.validate_output(data, output)
            return output

        transformer_cp = transformer.copy(transform)
        return transformer_cp


@overload
def ensure(incoming: Sequence[Callable[[_T], Any]]) -> _ensure_incoming[_T]:
    pass


@overload
def ensure(outcome: Sequence[Callable[[_S], Any]]) -> _ensure_outcome[_S]:
    pass


@overload
def ensure(changes: Sequence[Callable[[_T, _S], Any]]) -> _ensure_changes[_T, _S]:
    pass


@overload
def ensure(
    incoming: Sequence[Callable[[_T], Any]],
    outcome: Sequence[Callable[[_S], Any]]
) -> _ensure_both[_T, _S]:
    pass


@overload
def ensure(
    incoming: Sequence[Callable[[_T], Any]],
    changes: Sequence[Callable[[_T, _S], Any]]
) -> _ensure_both[_T, _S]:
    pass


@overload
def ensure(
    outcome: Sequence[Callable[[_T], Any]],
    changes: Sequence[Callable[[_T, _S], Any]]
) -> _ensure_both[_T, _S]:
    pass


@overload
def ensure(
    incoming: Sequence[Callable[[_T], Any]],
    outcome: Sequence[Callable[[_S], Any]],
    changes: Sequence[Callable[[_T, _S], Any]]
) -> _ensure_both[_T, _S]:
    pass


def ensure(*args, **kwargs):
    if len(kwargs.keys()) == 1 and 'incoming' in kwargs:
        return _ensure_incoming(kwargs['incoming'])

    if len(kwargs.keys()) == 1 and 'outcome' in kwargs:
        return _ensure_outcome(kwargs['outcome'])

    if len(kwargs.keys()) == 1 and 'changes' in kwargs:
        return _ensure_changes(kwargs['changes'])

    if len(kwargs.keys()) > 1:
        incoming = []
        if 'incoming' in kwargs:
            incoming = kwargs['incoming']

        outcome = []
        if 'outcome' in kwargs:
            outcome = kwargs['outcome']

        changes = []
        if 'changes' in kwargs:
            changes = kwargs['changes']

        return _ensure_both(incoming, outcome, changes)
