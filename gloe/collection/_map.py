import asyncio
from inspect import isawaitable
from typing import Generic, TypeVar, Iterable, Awaitable, Any, overload, cast
from typing_extensions import TypeVarTuple, Unpack

from gloe.transformers import Transformer

_T = TypeVar("_T", contravariant=True)
_U = TypeVar("_U", covariant=True)
_Out = TypeVar("_Out")
Args = TypeVarTuple("Args")


class Map(Generic[_T, _Out], Transformer[Iterable[_T], _Out]):
    """
    Transformer used to map values in an iterable using other transformers instead of
    functions.

    Example:
        In this example, we fetch a list of users that belongs to a group.
        Then, we get the posts of each user and finally turn it into a single list
        of posts.::

            @transformer
            def get_user_posts(user: User) -> list[Post]: ...

            get_posts_by_group: Transformer[Group, list[Post]] = (
                get_users_by_group >> Map(get_user_posts) >> flatten
            )
    Args:
        mapping_transformer: transformer applied to each item of the
            input iterable the yield the mapped item of the output iterable.
    """

    @overload
    def __init__(self: "Map[_T, list[_U]]", mapping_transformer: Transformer[_T, _U]):
        ...

    @overload
    def __init__(
        self: "Map[_T, Awaitable[list[_U]]]",
        mapping_transformer: Transformer[_T, Awaitable[_U]],
    ):
        ...

    @overload
    def __init__(
        self: "Map[tuple[Unpack[Args]], list[_U]]",
        mapping_transformer: Transformer[Unpack[Args], _U],
    ):
        ...

    @overload
    def __init__(
        self: "Map[tuple[Unpack[Args]], Awaitable[list[_U]]]",
        mapping_transformer: Transformer[Unpack[Args], Awaitable[_U]],
    ):
        ...

    def __init__(self, mapping_transformer: Transformer[Any, Any]):  # type: ignore[misc]
        super().__init__()
        self.mapping_transformer = mapping_transformer
        self.plotting_settings.has_children = True
        self._children = [mapping_transformer]

    def transform(self, data: Iterable[_T]) -> _Out:
        """
        Args:
            data: incoming iterable to be mapped. The items of this iterable must be of
                type :code:`_T`.

        Returns:
            The mapped iterable. The items of this new iterable are of type :code:`_U`.
        """
        mapping_result: list[Any] = []
        awaitables: list[tuple[int, Awaitable[Any]]] = []

        for item in data:
            result = self.mapping_transformer(item)
            if isawaitable(result):
                awaitables.append((len(mapping_result), result))
                mapping_result.append(None)
            else:
                mapping_result.append(result)

        if len(awaitables) == 0:
            return cast(_Out, mapping_result)

        async def _await_results() -> list[Any]:
            awaited = await asyncio.gather(*[result for _, result in awaitables])
            for (index, _), value in zip(awaitables, awaited):
                mapping_result[index] = value
            return mapping_result

        return cast(_Out, _await_results())
