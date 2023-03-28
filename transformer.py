import traceback
import uuid
import inspect
import warnings
from abc import ABC, abstractmethod
from inspect import Signature
from traceback import TracebackException
from types import FunctionType
from typing import Annotated
from typing import Any, \
    Callable, \
    Generic, \
    ParamSpec, Tuple, \
    TypeAlias, TypeVar, \
    Union, cast, overload, \
    Concatenate
from uuid import UUID

from typing_extensions import TypeVarTuple

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")

R1 = TypeVar("R1")
R2 = TypeVar("R2")
R3 = TypeVar("R3")
R4 = TypeVar("R4")
R5 = TypeVar("R5")
R6 = TypeVar("R6")


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
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer'],
    tuple['Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer']
]


class TransformerException(Exception):
    def __init__(
        self,
        previous_exception: Union['TransformerException', Exception],
        raiser_transformer: 'Transformer',
        message: str | None = None
    ):
        self.previous_exception = previous_exception
        self.raiser_transformer = raiser_transformer
        super().__init__(message)


class Transformer(Generic[T, S], ABC):
    """
    A Transformer is generic block with the responsibility to take an input of type `T`
    and transform it to an output of type `S`.


    Typical usage example:

    class Stringifier(Transformer[dict, str]):
        ...

    """

    @staticmethod
    def _merge_serial_connection(
        transformer1: 'Transformer[T, S]', transformer2: 'Transformer[S, U]'
    ) -> 'Transformer[T, U]':
        transformer1 = transformer1.copy()
        transformer2 = transformer2.copy()
        transformer2._set_previous(transformer1)

        transformer1_signature: Signature = transformer1.__signature__()
        transformer2_signature: Signature = transformer2.__signature__()
        new_signature = transformer2_signature \
            .replace(parameters=list(transformer1_signature.parameters.values()))

        class NewTransformer(Transformer[T, U]):
            def transform(self, data: T) -> U:
                return transformer2(transformer1(data))

            def __signature__(self) -> Signature:
                return new_signature

            def __len__(self):
                return len(transformer2) + len(transformer1)

            def graph_nodes(self) -> dict[UUID, 'Transformer']:
                transformer1_nodes = transformer1.graph_nodes()
                transformer2_nodes = transformer2.graph_nodes()
                return {**transformer1_nodes, **transformer2_nodes}

        new_transformer = NewTransformer()
        new_transformer.__class__.__name__ = transformer2.__class__.__name__
        new_transformer._set_previous(transformer2.previous)
        return new_transformer

    @staticmethod
    def _merge_diverging_connection(
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
                return split_result(data)

            def __signature__(self) -> Signature:
                return new_signature

            def __len__(self):
                lengths = [len(t) for t in receiving_transformers]
                return sum(lengths) + len(incident_transformer)

            def graph_nodes(self) -> dict[UUID, 'Transformer']:
                incident_transformer_nodes = incident_transformer.graph_nodes()
                receiving_transformers_nodes = [
                    t.graph_nodes() for t in receiving_transformers
                ]
                all_nodes = incident_transformer_nodes
                for nodes in receiving_transformers_nodes:
                    all_nodes = {**all_nodes, **nodes}
                return all_nodes

        new_transformer = NewTransformer()
        new_transformer.previous = cast(PreviousTransformer, receiving_transformers)
        new_transformer.__class__.__name__ = 'Converge'
        return new_transformer

    def __init__(self):
        self._handlers: list[TransformerHandler[T, S]] = []
        self.previous: PreviousTransformer = None
        self.id = uuid.uuid4()
        self.__class__.__annotations__ = self.transform.__annotations__
        self._signature = inspect.signature(self.transform)

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

    def copy(self, transform: Callable[['Transformer', T], S] | None = None, copy_previous: bool = True) -> 'Transformer[T, S]':
        _copy = type(
            type(self).__name__, (self.__class__,), {
                'transform': self.transform if transform is None else transform,
                '__call__': self.__class__.__call__,
                '__signature__': self.__signature__,
            }
        )
        copied = _copy()
        copied.id = self.id
        copied._handlers = self._handlers
        if self.previous is not None and copy_previous:
            if type(self.previous) == tuple:
                copied.previous = tuple([
                    previous_transformer.copy(copy_previous=False)
                    for previous_transformer in self.previous
                ])
            elif isinstance(self.previous, Transformer):
                copied.previous = self.previous.copy(copy_previous=False)
        else:
            copied.previous = self.previous

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
        return self._signature

    def _set_signature(self, signature: Signature):
        self._signature = signature

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
                    key=lambda anc: len(anc.ancestors())
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

            first_repr = fca_repr + ' ─┬─⟶ ' + previous_reprs[0].ljust(max_len, '─') + '──╮'
            middle_repr = "\n".join([
                ' ' * fca_repr_len + '  ├─⟶ ' + previous_repr.ljust(max_len, '─') + '──┤'
                for previous_repr in previous_reprs[1:-1]
            ] + [''])
            last_repr = ' ' * fca_repr_len + '  ╰─⟶ ' + previous_reprs[-1].ljust(max_len, '─') + '──┴──⟶'

            return f'{first_repr}\n{middle_repr}{last_repr} ({type(self).__name__})'

        return f'{self.previous} ─⟶ ({type(self).__name__})'

    def graph_nodes(self) -> dict[UUID, 'Transformer']:
        return {self.id: self}

    def __len__(self):
        return 1

    def __call__(self, data: T) -> S:
        internal_exception = None
        transformed: S | None = None
        try:
            transformed = self.transform(data)
            for handler in self._handlers:
                handler.handle(data, transformed)
        except TransformerException as exception:
            internal_exception = TransformerException(
                previous_exception=exception,
                raiser_transformer=self
            )
        except Exception as exception:
            internal_exception = TransformerException(
                previous_exception=exception,
                raiser_transformer=self,
                message=f"Error occurred in node with ID {self.id}."
            )

        if internal_exception is not None and type(internal_exception.previous_exception) != TransformerException:
            # print(traceback.format_tb(internal_exception.previous_exception.__traceback__))
            raise internal_exception.previous_exception

        if transformed is not None:
            return transformed

        raise NotImplementedError

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
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]', 'Transformer[S, R4]'
        ]
    ) -> 'Transformer[T, Tuple[U, R1, R2, R3, R4]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]', 'Transformer[S, R4]', 'Transformer[S, R5]'
        ]
    ) -> 'Transformer[T, Tuple[U, R1, R2, R3, R4, R5]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]', 'Transformer[S, R4]', 'Transformer[S, R5]', 'Transformer[S, R6]'
        ]
    ) -> 'Transformer[T, Tuple[U, R1, R2, R3, R4, R5, R6]]':
        pass

    @overload
    def __rshift__(self: 'Transformer[T, S]', next_transformer: 'Transformer[S, U]') -> 'Transformer[T, U]':
        pass

    # @overload
    # def __rshift__(self: 'Transformer[T, S]', next_transformer: 'Blank[S, U]') -> 'GenericTransformer[T, U, [GenericTransformer[S, U, []]]]':
    #     pass

    def __rshift__(self, next_transformers: Any):
        if isinstance(next_transformers, Transformer):
            return self._merge_serial_connection(self, next_transformers)

        elif type(next_transformers) == tuple:
            is_all_transformers = all(
                isinstance(next_transformer, Transformer)
                for next_transformer in next_transformers
            )
            if is_all_transformers:
                return self._merge_diverging_connection(self, *next_transformers)

            raise Exception("Unsupported transformer argument")
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
        __annotations__ = cast(FunctionType, func).__annotations__

        def __signature__(self) -> Signature:
            return func_signature

        def transform(self, data: T) -> S:
            return func(data)

    lambda_transformer = LambdaTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    return lambda_transformer


class Blank(Generic[T, S]):

    def transform(self, data: T) -> S:
        raise Exception('Blank transformers must be filled.')


A = ParamSpec("A")


# class GenericTransformer(Generic[T, S, A], ABC):
#     @overload
#     def __rshift__(
#         self,
#         next_transformer: Transformer[S, U]
#     ) -> 'GenericTransformer[T, U, A]':
#         pass
#
#     @overload
#     def __rshift__(
#         self,
#         next_transformer: Blank[S, U]
#     ) -> 'GenericTransformer[T, U, Concatenate[Transformer[S, U], A]]':
#         pass
#
#     @overload
#     def __rshift__(
#         self,
#         next_transformer: 'GenericTransformer[S, U, ]'
#     ) -> 'GenericTransformer[T, U, Concatenate[GenericTransformer[S, U], A]]':
#         pass
#
#     def __rshift__(self, next_transformer: Any):
#         print('top')


class Begin(Generic[T], Transformer[T, T]):
    def __repr__(self):
        return str(self.previous)

    def transform(self, data: T) -> T:
        return data
