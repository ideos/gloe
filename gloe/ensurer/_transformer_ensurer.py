import inspect
from abc import abstractmethod, ABC
from types import FunctionType
from typing import Any, Callable, Generic, Sequence, TypeVar, cast, overload

from typing_extensions import ParamSpec

from gloe.exceptions import UnsupportedEnsurerArgException
from gloe.async_transformer import AsyncTransformer
from gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")
_P1 = ParamSpec("_P1")


class TransformerEnsurer(Generic[_T, _S], ABC):
    @abstractmethod
    def validate_input(self, data: _T):
        """Perform a validation on incoming data before execute the transformer code"""

    @abstractmethod
    def validate_output(self, data: _T, output: _S):
        """Perform a validation on outcome data after execute the transformer code"""


def input_ensurer(func: Callable[[_T], Any]) -> TransformerEnsurer[_T, Any]:
    class LambdaEnsurer(TransformerEnsurer[_T, _S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def validate_input(self, data: _T):
            func(data)

        def validate_output(self, data: _T, output: _S):  # pragma: no cover
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

        def validate_input(self, data):  # pragma: no cover
            pass

        def validate_output(self, data, output):
            if len(inspect.signature(func).parameters) == 1:
                func(output)
            else:
                func(data, output)

    return LambdaEnsurer()


class _ensure_base:
    def __init__(self):
        self.input_ensurers_instances = []
        self.output_ensurers_instances = []
        self._input_data = None

    @overload
    def __call__(self, transformer: Transformer[_U, _S]) -> Transformer[_U, _S]:
        pass

    @overload
    def __call__(
        self, transformer: AsyncTransformer[_U, _S]
    ) -> AsyncTransformer[_U, _S]:
        pass

    @overload
    def __call__(
        self, partial_transformer: Callable[_P1, Transformer[_T, _U]]
    ) -> Callable[_P1, Transformer[_T, _U]]:
        pass

    @overload
    def __call__(
        self, partial_transformer: Callable[_P1, AsyncTransformer[_T, _U]]
    ) -> Callable[_P1, AsyncTransformer[_T, _U]]:
        pass

    def __call__(self, arg):
        if isinstance(arg, Transformer):
            return self._generate_new_transformer(arg)
        if isinstance(arg, AsyncTransformer):
            return self._generate_new_async_transformer(arg)
        if callable(arg):
            partial_transformer = arg

            def ensured_partial_transformer(*args, **kwargs):
                transformer = partial_transformer(*args, **kwargs)
                if isinstance(transformer, Transformer):
                    return self._generate_new_transformer(transformer)
                if isinstance(transformer, AsyncTransformer):
                    return self._generate_new_async_transformer(transformer)

                raise UnsupportedEnsurerArgException(transformer)

            return ensured_partial_transformer

        raise UnsupportedEnsurerArgException(arg)

    def _generate_new_transformer(self, transformer: Transformer) -> Transformer:
        _flow = transformer._flow
        first_node = _flow[0]
        last_node = _flow[-1]

        if isinstance(first_node, Transformer) and len(transformer) == 1:

            def transform(_, data):
                for ensurer in self.input_ensurers_instances:
                    ensurer.validate_input(data)
                output = transformer.transform(data)
                for ensurer in self.output_ensurers_instances:
                    ensurer.validate_output(data, output)
                return output

            return transformer.copy(transform)

        if isinstance(first_node, Transformer) and (
            len(self.input_ensurers_instances) > 0
            or len(self.output_ensurers_instances) > 0
        ):

            def transform(_, data):
                for ensurer in self.input_ensurers_instances:
                    ensurer.validate_input(data)
                output = first_node.transform(data)
                self._input_data = data
                return output

            transformer._flow[0] = first_node.copy(transform)

        if (
            isinstance(last_node, Transformer)
            and len(self.output_ensurers_instances) > 0
        ):

            def transform(_, data):
                output = last_node.transform(data)
                for ensurer in self.output_ensurers_instances:
                    ensurer.validate_output(self._input_data, output)
                return output

            transformer._flow[-1] = last_node.copy(transform)

        return transformer

    def _generate_new_async_transformer(
        self, transformer: AsyncTransformer
    ) -> AsyncTransformer:
        _flow = transformer._flow
        first_node = _flow[0]
        last_node = _flow[-1]

        if isinstance(first_node, AsyncTransformer) and len(_flow) == 1:

            async def transform_async(_, data):
                for ensurer in self.input_ensurers_instances:
                    ensurer.validate_input(data)
                output = await transformer.transform_async(data)
                for ensurer in self.output_ensurers_instances:
                    ensurer.validate_output(data, output)
                return output

            return transformer.copy(transform_async)

        if (
            len(self.input_ensurers_instances) > 0
            or len(self.output_ensurers_instances) > 0
        ):
            if isinstance(first_node, AsyncTransformer):

                async def transform_async(_, data):
                    for ensurer in self.input_ensurers_instances:
                        ensurer.validate_input(data)
                    output = await first_node.transform_async(data)
                    self._input_data = data
                    return output

                transformer._flow[0] = first_node.copy(transform_async)
            elif isinstance(first_node, Transformer):

                def transform(_, data):
                    for ensurer in self.input_ensurers_instances:
                        ensurer.validate_input(data)
                    output = first_node.transform(data)
                    self._input_data = data
                    return output

                transformer._flow[0] = first_node.copy(transform)

        if len(self.output_ensurers_instances) > 0:
            if isinstance(last_node, AsyncTransformer):

                async def transform_async(_, data):
                    output = await last_node.transform_async(data)
                    for ensurer in self.output_ensurers_instances:
                        ensurer.validate_output(self._input_data, output)
                    return output

                transformer._flow[-1] = last_node.copy(transform_async)

            elif isinstance(last_node, Transformer):

                def transform(_, data):
                    output = last_node.transform(data)
                    for ensurer in self.output_ensurers_instances:
                        ensurer.validate_output(self._input_data, output)
                    return output

                transformer._flow[-1] = last_node.copy(transform)

        return transformer


class _ensure_incoming(Generic[_T], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[_T], Any]]):
        super().__init__()
        self.input_ensurers_instances = [input_ensurer(ensurer) for ensurer in incoming]


class _ensure_outcome(Generic[_S], _ensure_base):
    def __init__(self, incoming: Sequence[Callable[[_S], Any]]):
        super().__init__()
        self.output_ensurers_instances = [
            output_ensurer(ensurer) for ensurer in incoming
        ]


class _ensure_changes(Generic[_T, _S], _ensure_base):
    def __init__(self, changes: Sequence[Callable[[_T, _S], Any]]):
        super().__init__()
        self.output_ensurers_instances = [
            output_ensurer(ensurer) for ensurer in changes
        ]


class _ensure_both(Generic[_T, _S], _ensure_base):
    def __init__(
        self,
        incoming: Sequence[Callable[[_T], Any]],
        outcome: Sequence[Callable[[_S], Any]],
        changes: Sequence[Callable[[_T, _S], Any]],
    ):
        super().__init__()
        incoming_seq = incoming if isinstance(incoming, list) else [incoming]
        self.input_ensurers_instances = [
            input_ensurer(ensurer) for ensurer in incoming_seq
        ]

        outcome_seq = outcome if isinstance(outcome, list) else [outcome]
        self.output_ensurers_instances = [
            output_ensurer(ensurer) for ensurer in outcome_seq
        ]

        changes_seq = changes if isinstance(changes, list) else [changes]
        self.output_ensurers_instances = self.output_ensurers_instances + [
            output_ensurer(ensurer) for ensurer in changes_seq
        ]
