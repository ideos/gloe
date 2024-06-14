from typing import Generic, TypeVar, Iterable

from gloe import AsyncTransformer

_T = TypeVar("_T", contravariant=True)
_U = TypeVar("_U", covariant=True)


class MapAsync(Generic[_T, _U], AsyncTransformer[Iterable[_T], Iterable[_U]]):
    """
    Transformer used to map values in an iterable using other async transformers instead
    of functions.

    Example:
        In this example, we fetch a list of users that belongs to a group.
        Then, we get the posts of each user and finally turn it into a single list
        of posts.::

            @async_transformer
            async def get_user_posts(user: User) -> list[Post]: ...

            get_posts_by_group: AsyncTransformer[Group, Iterable[Post]] = (
                get_users_by_group >> MapAsync(get_user_posts) >> flatten
            )
    Args:
        mapping_transformer: async transformer applied to each item of the
            input iterable the yield the mapped item of the output iterable.
    """

    def __init__(self, mapping_transformer: AsyncTransformer[_T, _U]):
        super().__init__()
        self.mapping_transformer = mapping_transformer
        self.plotting_settings.has_children = True
        self._children = [mapping_transformer]

    async def transform_async(self, data: Iterable[_T]) -> Iterable[_U]:
        """
        Args:
            data: incoming iterable to be mapped. The items of this iterable must be of
                type :code:`_T`.

        Returns:
            The mapped iterable. The items of this new iterable are of type :code:`_U`.
        """
        mapping_result = []
        for item in data:
            mapping_result.append(await self.mapping_transformer(item))
        return mapping_result
