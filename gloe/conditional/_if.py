from gloe.exceptions import UnsupportedTransformerArgException
from gloe.conditional._if_then_else import (
    _IfThenSync,
    _IfThenAsync,
    _as_async_transformer,
    _returns_awaitable,
)
from gloe.conditional._implication import _Implication, _AsyncImplication
from typing import (
    Callable,
    Generic,
    TypeVar,
    Union,
    overload,
)
from typing import Awaitable

from gloe.transformers import Transformer


In = TypeVar("In")
ThenOut = TypeVar("ThenOut", covariant=True)


class If(Generic[In]):
    """
    It is used to start a condition chaining

    Example:
        The below example send a different email for admin and non admin users::

            send_email = (
                If(lambda user: "admin" in user.roles)
                    .Then(fetch_admin_data >> send_admin_email)
                .Else(send_member_email)
            )

    Args:
        condition: callable returning a boolean.
        name: optional argument that adds a label to condition node during plotting.
    """

    def __init__(self, condition: Callable[[In], bool], name: Union[str, None] = None):
        super().__init__()
        self._condition = condition
        self._name: str = name or condition.__name__

    @overload  # type: ignore[overload-overlap]
    def Then(  # type: ignore[overload-overlap]
        self, next_transformer: Transformer[In, Awaitable[ThenOut]]
    ) -> _IfThenAsync[In, ThenOut, ThenOut]:
        pass

    @overload  # type: ignore[overload-overlap]
    def Then(  # type: ignore[overload-overlap]
        self, next_transformer: Transformer[In, ThenOut]
    ) -> _IfThenSync[In, ThenOut, ThenOut]:
        pass

    def Then(self, next_transformer: Transformer[In, ThenOut]):
        if isinstance(next_transformer, Transformer):
            if _returns_awaitable(next_transformer):
                async_transformer = _as_async_transformer(next_transformer)
                async_implication = _AsyncImplication(self._condition, async_transformer)
                return _IfThenAsync(async_implication, name=self._name)

            sync_implication = _Implication(self._condition, next_transformer)
            return _IfThenSync(sync_implication, name=self._name)

        raise UnsupportedTransformerArgException(next_transformer)


def condition(func: Callable[[In], bool]) -> If[In]:
    """
    The condition decorator is responsible to build an instance of :code:`If[T]`
    class given a :code:`Callable[[T], bool]`.

    When instantiating the :code:`If` class, the parameter :code:`name` will be the name
    of the callable.

    See Also:
        For additional information about conditions and examples of its usage, consult
        :ref:`conditional-flows`.

    Example:
        The below example send a different email for admin and non admin users::

            @condition
            def is_admin(user: User) -> bool:
                return "admin" in user.roles

            send_email = (
                is_admin.Then(fetch_admin_data >> send_admin_email)
                .Else(send_member_email)
            )

    Args:
        func: A callable that check somenting about the incoming data and returns a
            boolean.
    """
    condition = If(func, func.__name__)
    return condition
