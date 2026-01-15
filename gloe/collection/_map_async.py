from typing import Awaitable, Callable, Generic, Iterable, TypeVar

from gloe._node_utils import _coerce_transformer
from gloe import AsyncTransformer

_T = TypeVar("_T", contravariant=True)
_U = TypeVar("_U", covariant=True)


class MapAsync(Generic[_T, _U], AsyncTransformer[Iterable[_T], list[_U]]):
    """
    Transformer used to map values in an iterable using other async transformers instead
    of functions.

    Example:
        In this example, we fetch a list of users that belongs to a group.
        Then, we get the posts of each user and finally turn it into a single list
        of posts.::

            @async_transformer
            async def get_user_posts(user: User) -> list[Post]: ...

            get_posts_by_group: AsyncTransformer[Group, list[Post]] = (
                get_users_by_group >> MapAsync(get_user_posts) >> flatten
            )
    Args:
        mapping_transformer: async transformer applied to each item of the
            input iterable the yield the mapped item of the output iterable.
    """

    def __init__(
        self,
        mapping_transformer: AsyncTransformer[_T, _U]
        | Callable[[_T], Awaitable[_U]]
        | Callable[[_T], _U],
    ):
        super().__init__()
        self.mapping_transformer = _coerce_transformer(mapping_transformer)
        self.plotting_settings.has_children = True
        self._children = [self.mapping_transformer]

    async def transform_async(self, data: Iterable[_T]) -> list[_U]:
        """
        Args:
            data: incoming iterable to be mapped. The items of this iterable must be of
                type :code:`_T`.

        Returns:
            The mapped iterable. The items of this new iterable are of type :code:`_U`.
        """
        mapping_result = []
        for item in data:
            if isinstance(self.mapping_transformer, AsyncTransformer):
                result = await self.mapping_transformer(item)
            else:
                result = self.mapping_transformer(item)
            mapping_result.append(result)
        return mapping_result
