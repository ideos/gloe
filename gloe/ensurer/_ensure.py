from typing import overload, Sequence, Callable, Any, TypeVar

from gloe.ensurer._transformer_ensurer import (
    _ensure_incoming,
    _ensure_outcome,
    _ensure_changes,
    _ensure_both,
)

_T = TypeVar("_T")
_S = TypeVar("_S")


@overload
def ensure(*, incoming: Sequence[Callable[[_T], Any]]) -> _ensure_incoming[_T]:
    pass


@overload
def ensure(*, outcome: Sequence[Callable[[_S], Any]]) -> _ensure_outcome[_S]:
    pass


@overload
def ensure(*, changes: Sequence[Callable[[_T, _S], Any]]) -> _ensure_changes[_T, _S]:
    pass


@overload
def ensure(
    *, incoming: Sequence[Callable[[_T], Any]], outcome: Sequence[Callable[[_S], Any]]
) -> _ensure_both[_T, _S]:
    pass


@overload
def ensure(
    *,
    incoming: Sequence[Callable[[_T], Any]],
    changes: Sequence[Callable[[_T, _S], Any]],
) -> _ensure_both[_T, _S]:
    pass


@overload
def ensure(
    *,
    outcome: Sequence[Callable[[_T], Any]],
    changes: Sequence[Callable[[_T, _S], Any]],
) -> _ensure_both[_T, _S]:
    pass


@overload
def ensure(
    *,
    incoming: Sequence[Callable[[_T], Any]],
    outcome: Sequence[Callable[[_S], Any]],
    changes: Sequence[Callable[[_T, _S], Any]],
) -> _ensure_both[_T, _S]:
    pass


def ensure(*args, **kwargs):
    """
    This decorator is used in transformers to ensure some validation based on its
    incoming data, outcome data, or both.

    These validations are performed by validators. Validators are simple callable
    functions that validate certain aspects of the input, output, or the differences
    between them. If the validation fails, it must raise an exception.

    The decorator :code:`@ensure` returns some intermediate classes to assist with the
    internal logic of Gloe. However, the result of applying it to a transformer is just
    a new transformer with the exact same attributes, but it includes an additional
    validation layer.

    The motivation of the many overloads is just to allow the user to define different
    types of validators interchangeably.

    See also:
        For more detailed information about this feature, refer to the :ref:`ensurers`
        page.

    Args:
        incoming (Sequence[Callable[[_T], Any]]): sequence of validators that will be
            applied to the incoming data. The type :code:`_T` refers to the incoming
            type. Defaut value: :code:`[]`.
        outcome (Sequence[Callable[[_S], Any]]): sequence of validators that will be
            applied to the outcome data. The type :code:`_S` refers to the outcome type.
            Defaut value: :code:`[]`.
        changes (Sequence[Callable[[_T, _S], Any]]): sequence of validators that will be
            applied to both incoming and outcome data. The type :code:`_T` refers to the
            incoming type, and type :code:`_S` refers to the outcome type.
            Defaut value: :code:`[]`.
    """
    if len(kwargs.keys()) == 1 and "incoming" in kwargs:
        return _ensure_incoming(kwargs["incoming"])

    if len(kwargs.keys()) == 1 and "outcome" in kwargs:
        return _ensure_outcome(kwargs["outcome"])

    if len(kwargs.keys()) == 1 and "changes" in kwargs:
        return _ensure_changes(kwargs["changes"])

    if len(kwargs.keys()) > 1:
        incoming = []
        if "incoming" in kwargs:
            incoming = kwargs["incoming"]

        outcome = []
        if "outcome" in kwargs:
            outcome = kwargs["outcome"]

        changes = []
        if "changes" in kwargs:
            changes = kwargs["changes"]

        return _ensure_both(incoming, outcome, changes)
