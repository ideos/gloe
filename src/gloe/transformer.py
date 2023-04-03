import copy
import traceback
import types
import uuid
import inspect
import warnings
from abc import ABC, ABCMeta, abstractmethod
from inspect import Signature
from types import FunctionType
from typing import Any, \
    Callable, \
    Generic, \
    Protocol, Tuple, \
    TypeAlias, TypeVar, \
    Union, cast, overload
from uuid import UUID
from schemdraw import Drawing, flow
import schemdraw.elements as elm
from schemdraw.elements import Element
from schemdraw.util import Point

from .sequential_pass import SequentialPass

A = TypeVar("A")
S = TypeVar("S")
U = TypeVar("U")

R1 = TypeVar("R1")
R2 = TypeVar("R2")
R3 = TypeVar("R3")
R4 = TypeVar("R4")
R5 = TypeVar("R5")
R6 = TypeVar("R6")


class TransformerHandler(Generic[A, S], ABC):

    @abstractmethod
    def handle(self, input_data: A, output: S):
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
        internal_exception: Union['TransformerException', Exception],
        raiser_transformer: 'Transformer',
        message: str | None = None
    ):
        self.internal_exception = internal_exception
        self.raiser_transformer = raiser_transformer
        internal_exception.__context__ = self
        super().__init__(message)


class Transformer(Generic[A, S], SequentialPass['Transformer'], ABC):
    """
    A Transformer is generic block with the responsibility to take an input of type `T`
    and transform it to an output of type `S`.


    Typical usage example:

    class Stringifier(Transformer[dict, str]):
        ...

    """

    @staticmethod
    def _merge_serial_connection(
        transformer1: 'Transformer[A, S]', transformer2: 'Transformer[S, U]'
    ) -> 'Transformer[A, U]':
        transformer1 = transformer1.copy()
        transformer2 = transformer2.copy()
        transformer2._set_previous(transformer1)

        transformer1_signature: Signature = transformer1.__signature__()
        transformer2_signature: Signature = transformer2.__signature__()
        new_signature = transformer2_signature \
            .replace(parameters=list(transformer1_signature.parameters.values()))

        class NewTransformer(Transformer[A, U]):
            def transform(self, data: A) -> U:
                transformer2_call = transformer2.__call__
                transformer1_call = transformer1.__call__
                return transformer2_call(transformer1_call(data))

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
        incident_transformer: 'Transformer[A, S]',
        *receiving_transformers: 'Transformer[S, Any]'
    ) -> 'Transformer[A, tuple]':
        incident_transformer = incident_transformer.copy()
        receiving_transformers = tuple([
            receiving_transformer.copy() for receiving_transformer in receiving_transformers
        ])
        for receiving_transformer in receiving_transformers:
            receiving_transformer._set_previous(incident_transformer)

        def split_result(data: A) -> Tuple[Any, ...]:
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

        class NewTransformer(Transformer[A, Tuple[Any, ...]]):
            def transform(self, data: A) -> Tuple[Any, ...]:
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
        self._handlers: list[TransformerHandler[A, S]] = []
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
    def transform(self, data: A) -> S:
        pass

    def add_handler(self, handler: TransformerHandler[A, S]):
        if handler not in self._handlers:
            self._handlers = self._handlers + [handler]

        previous = self.previous
        if previous is not None:
            if type(previous) == tuple:
                for previous_transformer in previous:
                    previous_transformer.add_handler(handler)
            elif isinstance(previous, Transformer):
                previous.add_handler(handler)

    def copy(self,
             transform: Callable[['Transformer', A], S] | None = None,
             copy_previous: bool = True) -> 'Transformer[A, S]':
        _copy = copy.copy(self)

        if transform is not None:
            func_type = types.MethodType
            setattr(_copy, 'transform', func_type(transform, _copy))

        copied = _copy
        copied.id = self.id
        copied._handlers = self._handlers
        if self.previous is not None and copy_previous:
            if type(self.previous) == tuple:
                copied.previous = cast(PreviousTransformer, tuple([
                    previous_transformer.copy(copy_previous=False)
                    for previous_transformer in self.previous
                ]))
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

    # def _flow_drawing(
    #     self,
    #     drawing: Drawing,
    #     common_ancestor: Union['Transformer', None] = None,
    #     add_last_arrow: bool = True,
    #     anchor: Union[Point, None] = None,
    #     dx: float = 0,
    #     dy: float = 0
    # ) -> Union[Element, list[Element]]:
    #
    #     last_box = flow.Process().label(self.__class__.__name__)
    #     first_box: Union[Element, list[Element]] = last_box
    #
    #     previous = self.previous
    #     if previous is not None and previous != common_ancestor:
    #         if type(previous) == tuple:
    #             previous_list = tuple([prev.copy() for prev in previous])
    #             previous_ancestors = [previous.ancestors() for previous in previous_list]
    #             common_ancestors = set.intersection(*previous_ancestors)
    #
    #             if len(common_ancestors) > 0:
    #                 first_common_ancestor = max(
    #                     list(common_ancestors),
    #                     key=lambda anc: len(anc.ancestors())
    #                 )
    #
    #                 first_common_ancestor.previous._flow_drawing(drawing)
    #                 gateway = flow.Decision()
    #                 drawing += gateway
    #
    #                 boxes = [
    #                     prev._flow_drawing(
    #                         drawing,
    #                         first_common_ancestor,
    #                         add_last_arrow=False,
    #                         anchor=gateway.S,
    #                         dx=i * 5,
    #                         dy=-2
    #                     )
    #                     for i, prev in enumerate(previous_list)
    #                 ]
    #
    #                 for box in boxes:
    #                     drawing += elm.RightLines(arrow='->').at(gateway.S).to(box.N)
    #
    #                 first_box = boxes
    #                 # drawing += flow.Decision()
    #
    #         elif isinstance(previous, Transformer):
    #             first_box = previous._flow_drawing(
    #                 drawing,
    #                 common_ancestor=common_ancestor,
    #                 add_last_arrow=add_last_arrow,
    #                 anchor=anchor,
    #                 dx=dx,
    #                 dy=dy
    #             )
    #     else:
    #         if anchor is not None:
    #             drawing.move_from(anchor, dx=dx, dy=dy)
    #         else:
    #             drawing.move(dy=dy)
    #
    #     drawing += last_box
    #
    #     drawing += flow.Arrow().label(str(self.__signature__().return_annotation))
    #
    #     return first_box
    #
    #
    # def save(self, svg_file: str):
    #     d = Drawing(canvas='svg')
    #     d.config(fontsize=10, unit=1)
    #     d += flow.Start().label('Start')
    #     parameters = self.__signature__().parameters
    #     parameter_names = list(parameters.keys())
    #     first_parameter = parameters[parameter_names[0]]
    #     d += flow.Arrow().label(str(first_parameter.annotation.__name__))
    #     self._flow_drawing(d)
    #     # d += flow.StateEnd().label('End')
    #     d.save(svg_file)

    def __len__(self):
        return 1

    def __call__(self, data: A) -> S:
        transform_exception = None

        transformed: S | None = None
        try:
            transformed = self.transform(data)
            for handler in self._handlers:
                handler.handle(data, transformed)
        except TransformerException as exception:
            transform_exception = TransformerException(
                internal_exception=exception.internal_exception,
                raiser_transformer=self,
                message=f"Error occurred in node with ID {self.id}."
            )
        except Exception as exception:
            if type(exception.__context__) == TransformerException:
                transform_exception = cast(TransformerException, exception.__context__)
            else:
                transform_exception = TransformerException(
                    internal_exception=exception,
                    raiser_transformer=self,
                    message=f"Error occurred in node [{self.__class__.__name__}]."
                )

        if transform_exception is not None:
            # print(traceback.format_tb(internal_exception.previous_exception.__traceback__))
            raise transform_exception.internal_exception

        if type(transformed) is not None:
            return transformed

        raise NotImplementedError

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[S, U]', 'Transformer[S, R1]']
    ) -> 'Transformer[A, Tuple[U, R1]]':
        pass

    @overload
    def __rshift__(
        self, transformers: Tuple['Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]']
    ) -> 'Transformer[A, Tuple[U, R1, R2]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]'
        ]
    ) -> 'Transformer[A, Tuple[U, R1, R2, R3]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]', 'Transformer[S, R4]'
        ]
    ) -> 'Transformer[A, Tuple[U, R1, R2, R3, R4]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]', 'Transformer[S, R4]', 'Transformer[S, R5]'
        ]
    ) -> 'Transformer[A, Tuple[U, R1, R2, R3, R4, R5]]':
        pass

    @overload
    def __rshift__(
        self,
        transformers: Tuple[
            'Transformer[S, U]', 'Transformer[S, R1]', 'Transformer[S, R2]', 'Transformer[S, R3]', 'Transformer[S, R4]', 'Transformer[S, R5]', 'Transformer[S, R6]'
        ]
    ) -> 'Transformer[A, Tuple[U, R1, R2, R3, R4, R5, R6]]':
        pass

    @overload
    def __rshift__(self, next_transformer: 'Transformer[S, U]') -> 'Transformer[A, U]':
        pass

    def __rshift__(self, next_step: Any):
        if isinstance(next_step, Transformer):
            return self._merge_serial_connection(self, next_step)

        elif type(next_step) == tuple:
            is_all_transformers = all(
                isinstance(next_transformer, Transformer)
                for next_transformer in next_step
            )
            if is_all_transformers:
                return self._merge_diverging_connection(self, *next_step)

            raise Exception("Unsupported transformer argument")
        else:
            raise Exception("Unsupported transformer argument")


def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    func_signature = inspect.signature(func)
    if len(func_signature.parameters) > 1:
        warnings.warn(
            "Only one parameter is allowed on Transformers. "
            f"Function '{func.__name__}' has the following signature: {func_signature}. "
            "To pass a complex data, use a complex type like named tuples, "
            "typed dicts, dataclasses or anything else.",
            category=RuntimeWarning
        )

    class LambdaTransformer(Transformer[A, S]):
        __doc__ = func.__doc__
        __annotations__ = cast(FunctionType, func).__annotations__

        def __signature__(self) -> Signature:
            return func_signature

        def transform(self, data: A) -> S:
            return func(data)

    lambda_transformer = LambdaTransformer()
    lambda_transformer.__class__.__name__ = func.__name__
    return lambda_transformer


class Blank(Generic[A, S]):

    def transform(self, data: A) -> S:
        raise Exception('Blank transformers must be filled.')


# A = ParamSpec("A")


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


class Begin(Generic[A], Transformer[A, A]):
    def __repr__(self):
        return str(self.previous)

    def transform(self, data: A) -> A:
        return data
