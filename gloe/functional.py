import inspect
from inspect import Signature
from types import FunctionType
from typing import Callable, TypeVar, cast, Awaitable, overload

from typing_extensions import Concatenate, TypeVarTuple, Unpack, ParamSpec, deprecated

from gloe.exceptions import TransformerRequiresMultiArgs
from gloe.transformers import Transformer

__all__ = [
    "transformer",
    "partial_transformer",
    "async_transformer",
    "partial_async_transformer",
]

A = TypeVar("A")
S = TypeVar("S")
S2 = TypeVar("S2")
P1 = ParamSpec("P1")
P2 = ParamSpec("P2")


def _awaitable_signature(signature: Signature) -> Signature:
    if signature.return_annotation is inspect._empty:
        return signature
    return signature.replace(
        return_annotation=Awaitable[signature.return_annotation],  # type: ignore[name-defined]
    )



@overload
def partial_transformer(
    func: Callable[Concatenate[A, P1], S],
) -> Callable[P1, Transformer[A, S]]:
    pass


@overload
def partial_transformer(
    func: Callable[Concatenate[A, P1], Awaitable[S]],
) -> Callable[P1, Transformer[A, Awaitable[S]]]:
    pass


def partial_transformer(
    func: Callable[Concatenate[A, P1], object],
) -> Callable[P1, Transformer[A, object]]:
    """
    This decorator let us create partial transformers, which are transformers that
    allow for partial application of their arguments. This capability is particularly
    useful for creating configurable transformer instances where some arguments are
    preset enhancing modularity and reusability in data processing pipelines.

    See Also:
        For further details on partial transformers and their applications, see
        :ref:`partial-transformers`.

    Example:
        Here's how to apply the `@partial_transformer` decorator to create a transformer
        with a pre-applied argument::

            @partial_transformer
            def enrich_data(data: Data, enrichment_type: str) -> Data:
                # Implementation for data enrichment based on the enrichment_type
                ...

            # Instantiate a transformer with the 'enrichment_type' pre-set
            enrich_with_metadata = enrich_data(enrichment_type="metadata")

            # Use the partially applied transformer
            get_enriched_data = get_data >> enrich_with_metadata

    Args:
        func: A callable with one or more arguments. The first argument is of
            type :code:`A`. The subsequent arguments are retained for use during
            transformer instantiation. This callable returns a value of type
            :code:`S`.

    Returns:
        A callable that receives the same arguments as :code:`func`, excluding the first
        one and returns a transformer with incoming type being :code:`A` and with
        :code:`S` as the outcome type.
    """

    def partial(*args: P1.args, **kwargs: P1.kwargs) -> Transformer[A, object]:
        func_signature = inspect.signature(func)
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            async_func = cast(Callable[Concatenate[A, P1], Awaitable[S]], func)

            class LambdaAsyncTransformer(Transformer[A, Awaitable[S]]):
                __doc__ = func.__doc__
                __annotations__ = cast(FunctionType, func).__annotations__

                def signature(self) -> Signature:
                    return _awaitable_signature(func_signature)

                def transform(self, data: A) -> Awaitable[S]:
                    return async_func(data, *args, **kwargs)

        else:
            sync_func = cast(Callable[Concatenate[A, P1], S], func)

            class LambdaSyncTransformer(Transformer[A, S]):
                __doc__ = func.__doc__
                __annotations__ = cast(FunctionType, func).__annotations__

                def signature(self) -> Signature:
                    return func_signature

                def transform(self, data: A) -> S:
                    return sync_func(data, *args, **kwargs)

        if is_async:
            lambda_transformer: Transformer[A, object] = cast(
                Transformer[A, object], LambdaAsyncTransformer()
            )
        else:
            lambda_transformer = cast(Transformer[A, object], LambdaSyncTransformer())
        lambda_transformer.__class__.__name__ = func.__name__
        lambda_transformer._label = func.__name__
        return lambda_transformer

    return partial


@deprecated("Use @partial_transformer with async callables instead.")
def partial_async_transformer(
    func: Callable[Concatenate[A, P1], Awaitable[S]],
) -> Callable[P1, Transformer[A, Awaitable[S]]]:
    """
    This decorator enables the creation of partial asynchronous transformers, which are
    transformers capable of partial argument application. Such functionality is
    invaluable for crafting reusable asynchronous transformer instances where certain
    arguments are predetermined, enhancing both modularity and reusability within
    asynchronous data processing flows.

    See Also:
        For additional insights into partial asynchronous transformers and their
        practical applications, consult :ref:`partial-async-transformers`.

    Example:
        Utilize the `@partial_async_transformer` decorator to build a transformer with
        a pre-set argument::

            @partial_async_transformer
            async def load_data(user_id: int, data_type: str) -> Data:
                # Logic for loading data based on user_id and data_type
                ...

            # Instantiate a transformer with 'data_type' predefined
            load_user_data = load_data(data_type="user_profile")

            # Subsequent usage requires only the user_id
            user_data = await load_user_data(user_id=1234)

    Args:
        func: A callable with one or more arguments, the first of which is of type `A`.
            Remaining arguments are preserved for later use during the instantiation of
            the transformer. This callable must asynchronously return a result of type
            `S`, indicating an operation that produces an output of type `S` upon
            completion.

    Returns:
        A callable that receives the same arguments as :code:`func`, excluding the first
        one and returns a transformer with incoming type being :code:`A` and with
        :code:`S` as the outcome type.
    """

    return partial_transformer(func)


Rest = TypeVarTuple("Rest")


B = TypeVar("B")


@overload
def transformer(
    func: Callable[[A, B, Unpack[Rest]], S],
) -> Transformer[A, B, Unpack[Rest], S]:
    pass


@overload
def transformer(
    func: Callable[[A, B, Unpack[Rest]], Awaitable[S]],
) -> Transformer[A, B, Unpack[Rest], Awaitable[S]]:
    pass


@overload
def transformer(func: Callable[[], Awaitable[S]]) -> Transformer[None, Awaitable[S]]:
    pass


@overload
def transformer(func: Callable[[], S]) -> Transformer[None, S]:
    pass


@overload
def transformer(func: Callable[[A], S]) -> Transformer[A, S]:
    pass


@overload
def transformer(func: Callable[[A], Awaitable[S]]) -> Transformer[A, Awaitable[S]]:
    pass


def transformer(func: Callable[..., object]) -> Transformer:
    """
    Convert a callable to an instance of the Transformer class.

    Example:
        The most common use is as a decorator::

            @transformer
            def filter_subscribed_users(users: list[User]) -> list[User]:
               ...

            subscribed_users = filter_subscribed_users(users_list)

    Args:
        func: A callable with only positional arguments and returns a result. The
            callable should return an instance of the generic type :code:`S` specified.
    Returns:
        An instance of the Transformer class, encapsulating the transformation logic
        defined in the provided callable.
    """
    func_signature = inspect.signature(func)
    is_async = inspect.iscoroutinefunction(func)

    if len(func_signature.parameters) > 1:

        if is_async:

            class LambdaAsyncMultiArgsTransformer(Transformer):
                __doc__ = func.__doc__
                __annotations__ = cast(FunctionType, func).__annotations__

                def signature(self) -> Signature:
                    return _awaitable_signature(func_signature)

                def transform(self, data) -> Awaitable[object]:
                    if type(data) is tuple:
                        if len(data) == 1:
                            raise TransformerRequiresMultiArgs()
                        return cast(Callable[..., Awaitable[object]], func)(*data)
                    raise NotImplementedError()  # pragma: no cover

        else:

            class LambdaSyncMultiArgsTransformer(Transformer):
                __doc__ = func.__doc__
                __annotations__ = cast(FunctionType, func).__annotations__

                def signature(self) -> Signature:
                    return func_signature

                def transform(self, data) -> object:
                    if type(data) is tuple:
                        if len(data) == 1:
                            raise TransformerRequiresMultiArgs()
                        return cast(Callable[..., object], func)(*data)
                    raise NotImplementedError()  # pragma: no cover

        if is_async:
            lambda_transformer1: Transformer = LambdaAsyncMultiArgsTransformer()
        else:
            lambda_transformer1 = LambdaSyncMultiArgsTransformer()
        lambda_transformer1._multi_args = True
        lambda_transformer1.__class__.__name__ = func.__name__
        lambda_transformer1._label = func.__name__
        return cast(Transformer, lambda_transformer1)

    if is_async:

        class LambdaAsyncTransformer(Transformer):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return _awaitable_signature(func_signature)

            def transform(self, data=None) -> Awaitable[object]:
                async_func = cast(Callable[..., Awaitable[object]], func)
                if len(func_signature.parameters) == 0:
                    return async_func()
                return async_func(data)

    else:

        class LambdaSyncTransformer(Transformer):
            __doc__ = func.__doc__
            __annotations__ = cast(FunctionType, func).__annotations__

            def signature(self) -> Signature:
                return func_signature

            def transform(self, data=None) -> object:
                sync_func = cast(Callable[..., object], func)
                if len(func_signature.parameters) == 0:
                    return sync_func()
                return sync_func(data)

    if is_async:
        lambda_transformer2: Transformer = LambdaAsyncTransformer()
    else:
        lambda_transformer2 = LambdaSyncTransformer()
    lambda_transformer2.__class__.__name__ = func.__name__
    lambda_transformer2._label = func.__name__
    return lambda_transformer2


@overload
def async_transformer(
    func: Callable[[A, B, Unpack[Rest]], Awaitable[S]],
) -> Transformer[A, B, Unpack[Rest], Awaitable[S]]:
    pass


@overload
def async_transformer(func: Callable[[], Awaitable[S]]) -> Transformer[None, Awaitable[S]]:
    pass


@overload
def async_transformer(func: Callable[[A], Awaitable[S]]) -> Transformer[A, Awaitable[S]]:
    pass


@deprecated("Use @transformer with async callables instead.")
def async_transformer(func):
    """
    Convert a callable to an instance of the Transformer class.

    See Also:
        For more information about this feature, refer to the :ref:`async-transformers`.

    Example:
        The most common use is as a decorator::

            @async_transformer
            async def get_user_by_role(role: str) -> list[User]:
               ...

            await get_user_by_role("admin")

    Args:
        func: A callable with only positional arguments and returns a coroutine.
    Returns:
        Returns an instance of the Transformer class, representing the built async
        transformer.
    """
    return transformer(func)
