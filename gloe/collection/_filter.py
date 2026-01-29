import asyncio
from inspect import isawaitable
from typing import Generic, TypeVar, Iterable, Awaitable, Any, overload, cast

from gloe._plotting_utils import PlottingSettings, NodeType
from gloe.transformers import Transformer

_T = TypeVar("_T")
_Out = TypeVar("_Out")


class Filter(Generic[_T, _Out], Transformer[Iterable[_T], _Out]):
    """
    Transformer used to filter values in an iterable using other transformers instead of
    functions.

    Example:
        In this example, we fetch a list of users and then filter the administrators.::

            @transformer
            def is_admin(user: User) -> bool: ...

            get_admin_users: Transformer[Group, Iterable[User]] = (
                get_users >> Filter(is_admin)
            )
    Args:
        filter_transformer: transformer applied to each item of the input iterable and
            check if this item must be dropped or not.
    """

    @overload
    def __init__(
        self: "Filter[_T, list[_T]]", filter_transformer: Transformer[_T, bool]
    ):
        ...

    @overload
    def __init__(
        self: "Filter[_T, Awaitable[list[_T]]]",
        filter_transformer: Transformer[_T, Awaitable[bool]],
    ):
        ...

    def __init__(self, filter_transformer: Transformer[_T, Any]):
        super().__init__()
        self.filter_transformer = filter_transformer
        self.plotting_settings.invisible = True
        self._children = [filter_transformer]

        self._plotting_settings: PlottingSettings = PlottingSettings(
            has_children=True,
            node_type=NodeType.Transformer,
        )

    def transform(self, data: Iterable[_T]) -> _Out:
        """
        Args:
            data: incoming iterable to be filtered. The items of this iterable must be
                of type :code:`_T`.

        Returns:
            The filtered iterable.
        """
        items: list[_T] = []
        checks: list[Any] = []
        awaitables: list[tuple[int, Awaitable[bool]]] = []

        for item in data:
            items.append(item)
            result = self.filter_transformer(item)
            if isawaitable(result):
                awaitables.append((len(checks), result))
                checks.append(None)
            else:
                checks.append(result)

        if len(awaitables) == 0:
            return cast(_Out, [item for item, keep in zip(items, checks) if keep])

        async def _await_checks() -> list[_T]:
            awaited = await asyncio.gather(*[result for _, result in awaitables])
            for (index, _), value in zip(awaitables, awaited):
                checks[index] = value
            return [item for item, keep in zip(items, checks) if keep]

        return cast(_Out, _await_checks())
