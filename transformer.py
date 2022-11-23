import uuid
import inspect
import warnings
from abc import ABC, abstractmethod
from inspect import Signature
from typing import Any, \
    Callable, \
    Generic, \
    Tuple, \
    TypeVar, \
    Union, overload

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")
V = TypeVar("V")


class TransformerHandler(Generic[T, S], ABC):

    @abstractmethod
    def handle(self, input_data: T, output: S):
        pass


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
            transform = custom_transform

            def __signature__(self) -> Signature:
                return new_signature

        new_transformer = NewTransformer()
        new_transformer.__class__.__name__ = transformer2.__class__.__name__
        new_transformer._set_previous(transformer2.previous)
        return new_transformer

    @staticmethod
    def _merge_diverging_transform(
        transformer1: 'Transformer[T, S]',
        transformer2: 'Transformer[S, U]',
        transformer3: 'Transformer[S, V]',
    ) -> 'Transformer[T, tuple[U, V]]':
        transformer1 = transformer1.copy()
        transformer2 = transformer2.copy()
        transformer3 = transformer3.copy()
        transformer2._set_previous(transformer1)
        transformer3._set_previous(transformer1)

        def split_result(data: T) -> Tuple[U, V]:
            intermediate_result = transformer1(data)
            return (
                transformer2(intermediate_result), transformer3(intermediate_result)
            )

        tuple_transform: Callable[[Any, T], Tuple[U, V]] = lambda _, data: split_result(data)

        trfm1_signature: Signature = transformer1.__signature__()
        trfm2_signature: Signature = transformer2.__signature__()
        trfm3_signature: Signature = transformer3.__signature__()
        new_signature = trfm1_signature.replace(
            return_annotation=f"({trfm2_signature.return_annotation}, {trfm3_signature.return_annotation})"
        )

        class NewTransformer(Transformer[T, U]):
            transform = tuple_transform

            def __signature__(self) -> Signature:
                return new_signature

        new_transformer = NewTransformer()
        new_transformer.previous = (transformer2, transformer3)
        new_transformer.__class__.__name__ = 'Converge'
        return new_transformer

    def __init__(self):
        self._handlers: list[TransformerHandler[T, S]] = []
        self.previous: Union[Transformer, Tuple[Transformer, Transformer], None] = None
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
                previous[0].add_handler(handler)
                previous[1].add_handler(handler)
            elif isinstance(previous, Transformer):
                previous.add_handler(handler)

    def copy(self):
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
                copied.previous = (
                    self.previous[0].copy(),
                    self.previous[1].copy()
                )
            elif isinstance(self.previous, Transformer):
                copied.previous = self.previous.copy()

        return copied

    def _set_previous(self, previous: 'Transformer[Any, Any]'):
        if self.previous is None:
            self.previous = previous
        elif type(self.previous) == tuple:
            self.previous[0]._set_previous(previous)
            self.previous[1]._set_previous(previous)
        elif isinstance(self.previous, Transformer):
            self.previous._set_previous(previous)

    def ancestors(self) -> set['Transformer']:
        ancestors: set['Transformer'] = set()
        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
                ancestors = {previous[0], previous[1]}
                ancestors = ancestors.union(previous[0].ancestors())
                ancestors = ancestors.union(previous[1].ancestors())
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
            input_type, output_type = self.__get_bound_types()
            return f'({type(self).__name__})'

        input_type, _ = self.__get_bound_types()
        if type(self.previous) == tuple:
            pr0 = self.previous[0].copy()
            pr1 = self.previous[1].copy()
            pr0_ancestors = pr0.ancestors()
            pr1_ancestors = pr1.ancestors()
            common_ancestors = pr1_ancestors.intersection(pr0_ancestors)

            if len(common_ancestors) > 0:
                first_common_ancestor = max(
                    list(common_ancestors),
                    key=lambda ancestor: len(ancestor.ancestors())
                )

                for ancestor in pr0_ancestors:
                    if ancestor.previous == first_common_ancestor:
                        ancestor.previous = None

                for ancestor in pr1_ancestors:
                    if ancestor.previous == first_common_ancestor:
                        ancestor.previous = None

                fca_repr = repr(first_common_ancestor)

            else:
                fca_repr = ''

            pr0_repr = repr(pr0) + ' '
            pr1_repr = repr(pr1) + ' '
            max_len = max(len(pr0_repr), len(pr1_repr))
            pr0_repr = fca_repr + f' ─┬─── ' + pr0_repr.ljust(max_len, '─') + '─╮'
            pr1_repr = ' ' * len(fca_repr) + '  ╰──⟶ ' + pr1_repr.ljust(max_len, '─') + '─┴──⟶'

            return f'{pr0_repr} \n{pr1_repr} ─⟶ ({type(self).__name__})'

        return f'{repr(self.previous)} ─⟶ ({type(self).__name__})'

    def __call__(self, data: T) -> S:
        transformed = self.transform(data)
        for handler in self._handlers:
            handler.handle(data, transformed)
        return transformed

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[S, U]', 'Transformer[S, V]']
    ) -> 'Transformer[T, Tuple[U, V]]':
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
            return self._merge_diverging_transform(self, transformer[0], transformer[1])
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