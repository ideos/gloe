import uuid
import inspect
import warnings
from abc import ABC, abstractmethod
from inspect import Signature
from typing import Any, \
    Callable, \
    Generic, \
    ParamSpec, Tuple, \
    TypeAlias, TypeVar, \
    Union, cast, overload

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")
R1 = TypeVar("R1")
R2 = TypeVar("R2")
R3 = TypeVar("R3")


class TransformerHandler(Generic[T, S], ABC):

    @abstractmethod
    def handle(self, input_data: T, output: S):
        pass


PreviousTransformer: TypeAlias = Union[
    None,
    'Transformer',
    tuple['Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer']
]


class Transformer(Generic[T, S], ABC):

    @staticmethod
    def _merge_serial_transform(
        transformer1: 'Transformer[T, S]', transformer2: 'Transformer[S, U]'
    ) -> 'Transformer[T, U]':
        transformer1 = transformer1.copy()
        transformer2 = transformer2.copy()
        transformer2._set_previous(transformer1)

        custom_transform: Callable[[Any, T], U] = \
            lambda _, data: transformer2(transformer1(data))

        trfm1_signature: Signature = transformer1.__signature__()
        trfm2_signature: Signature = transformer2.__signature__()
        new_signature = trfm2_signature \
            .replace(parameters=list(trfm1_signature.parameters.values()))

        class NewTransformer(Transformer[T, U]):
            def transform(self, data: T) -> U:
                return custom_transform(self, data)

            def __signature__(self) -> Signature:
                return new_signature

        new_transformer = NewTransformer()
        new_transformer.__class__.__name__ = transformer2.__class__.__name__
        new_transformer._set_previous(transformer2.previous)
        return new_transformer

    @staticmethod
    def _merge_diverging_transform(
        incident_transformer: 'Transformer[T, S]',
        *receiving_transformers: 'Transformer[S, Any]'
    ) -> 'Transformer[T, tuple]':
        incident_transformer = incident_transformer.copy()
        receiving_transformers = tuple([
            receiving_transformer.copy() for receiving_transformer in receiving_transformers
        ])
        for receiving_transformer in receiving_transformers:
            receiving_transformer._set_previous(incident_transformer)

        def split_result(data: T) -> Tuple[Any, ...]:
            intermediate_result = incident_transformer(data)
            return tuple([
                receiving_transformer(intermediate_result)
                for receiving_transformer in receiving_transformers
            ])

        tuple_transform: Callable[[Any, T], Tuple[Any, ...]] = \
            lambda _, data: split_result(data)

        incident_signature: Signature = incident_transformer.__signature__()
        receiving_signature_returns: list[str] = [
            str(receiving_transformer.__signature__().return_annotation)
            for receiving_transformer in receiving_transformers
        ]
        new_signature = incident_signature.replace(
            return_annotation=f"""({", ".join(receiving_signature_returns)})"""
        )

        class NewTransformer(Transformer[T, Tuple[Any, ...]]):
            def transform(self, data: T) -> Tuple[Any, ...]:
                return tuple_transform(self, data)

            def __signature__(self) -> Signature:
                return new_signature

        new_transformer = NewTransformer()
        new_transformer.previous = cast(PreviousTransformer, receiving_transformers)
        new_transformer.__class__.__name__ = 'Converge'
        return new_transformer

    def __init__(self):
        self._handlers: list[TransformerHandler[T, S]] = []
        self.previous: PreviousTransformer = None
        self.id = uuid.uuid4()
        self.__class__.__annotations__ = self.transform.__annotations__

    def __hash__(self):
        return self.id.int

    def __eq__(self, other):
        if isinstance(other, Transformer):
            return self.id == other.id
        return NotImplemented

    @abstractmethod
    def transform(self, data: T) -> S:
        pass

    def add_handler(self, handler: TransformerHandler[T, S]):
        if handler not in self._handlers:
            self._handlers = self._handlers + [handler]

        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
                for previous_transformer in previous:
                    previous_transformer.add_handler(handler)
            elif isinstance(previous, Transformer):
                previous.add_handler(handler)

    def copy(self) -> 'Transformer[T, S]':
        copy = type(
            type(self).__name__, (Transformer,), {
                'transform': self.transform,
                '__call__': self.__call__,
                '__signature__': self.__signature__
            }
        )
        copied = copy()
        copied.id = self.id
        copied._handlers = self._handlers
        if self.previous is not None:
            if type(self.previous) == tuple:
                copied.previous = tuple([
                    previous_transformer.copy()
                    for previous_transformer in self.previous
                ])
            elif isinstance(self.previous, Transformer):
                copied.previous = self.previous.copy()

        return copied

    def _set_previous(self, previous: PreviousTransformer):
        if self.previous is None:
            self.previous = previous
        elif type(self.previous) == tuple:
            for previous_transformer in self.previous:
                previous_transformer._set_previous(previous)
        elif isinstance(self.previous, Transformer):
            self.previous._set_previous(previous)

    def ancestors(self) -> set['Transformer']:
        ancestors: set['Transformer'] = set()
        previous = self.previous
        if previous is not None:
            # print(previous, isinstance(previous, Transformer))
            if type(previous) == tuple:
                ancestors = set(previous)
                for previous_transformer in previous:
                    ancestors = ancestors.union(previous_transformer.ancestors())
            elif isinstance(previous, Transformer):
                ancestors = {previous}
                ancestors = ancestors.union(previous.ancestors())

        return ancestors

    def __signature__(self) -> Signature:
        return inspect.signature(self.transform)

    def __get_bound_types(self) -> tuple[str, str]:
        transform_signature = self.__signature__()
        input_param = str([
            v
            for k, v in transform_signature.parameters.items()
            if k != 'self'
        ][0])

        if input_param is not None:
            input_param = input_param.split(": ")[1]

        output_param = transform_signature.return_annotation

        return input_param, output_param

    def __repr__(self):
        if self.previous is None:
            return f'({type(self).__name__})'

        if type(self.previous) == tuple:
            previous_list = tuple([previous.copy() for previous in self.previous])
            previous_ancestors = [previous.ancestors() for previous in previous_list]
            common_ancestors = set.intersection(*previous_ancestors)

            if len(common_ancestors) > 0:
                first_common_ancestor = max(
                    list(common_ancestors),
                    key=lambda ancestor: len(ancestor.ancestors())
                )

                for ancestors in previous_ancestors:
                    for ancestor in ancestors:
                        if ancestor.previous == first_common_ancestor:
                            ancestor.previous = None

                fca_repr = repr(first_common_ancestor)
            else:
                fca_repr = ''

            fca_repr_len = max(len(line) for line in fca_repr.split("\n"))
            previous_reprs = [
                f'{previous} ' for previous in previous_list
            ]
            max_len = max(len(previous_repr) for previous_repr in previous_reprs)

            first_repr = fca_repr + ' ─┬── ' + previous_reprs[0].ljust(max_len, '─') + '──╮'
            middle_repr = "\n".join([
                ' ' * fca_repr_len + '  ├─⟶ ' + previous_repr.ljust(max_len, '─') + '──┤'
                for previous_repr in previous_reprs[1:-1]
            ] + [''])
            last_repr = ' ' * fca_repr_len + '  ╰─⟶ ' + previous_reprs[-1].ljust(max_len, '─') + '──┴──⟶'

            return f'{first_repr}\n{middle_repr}{last_repr} ({type(self).__name__})'

        return f'{self.previous} ─⟶ ({type(self).__name__})'

    def __call__(self, data: T) -> S:
        transformed = self.transform(data)
        for handler in self._handlers:
            handler.handle(data, transformed)
        return transformed

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[S, U]', 'Transformer[S, R1]']
    ) -> 'Transformer[T, Tuple[U, R1]]':
        pass

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]']
    ) -> 'Transformer[T, Tuple[U, R1, R2]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]'
        ]
    ) -> 'Transformer[T, Tuple[U, R1, R2, R3]]':
        pass

    @overload
    def __rshift__(self, transformer: 'Transformer[S, U]') -> 'Transformer[T, U]':
        pass

    def __rshift__(self, transformer: Any) -> 'Transformer[T, Any]':
        if isinstance(transformer, Transformer):
            return self._merge_serial_transform(self, transformer)

        elif type(transformer) == tuple and isinstance(transformer[0], Transformer) and isinstance(
            transformer[1],
            Transformer
        ):
            return self._merge_diverging_transform(self, *transformer)
        else:
            raise Exception("Unsupported transformer argument")


def transformer(func: Callable[[T], S]) -> Transformer[T, S]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformers. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaTransformer(Transformer[T, S]):
        __doc__ = func.__doc__
        __annotations__ = func.__annotations__

        def __signature__(self) -> Signature:
            return func_signature

        def transform(self, data: T) -> S:
            return func(data)

    lambda_transformer = LambdaTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    return lambda_transformer
