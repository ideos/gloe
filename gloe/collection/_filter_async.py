from typing import Generic, TypeVar, Iterable

from gloe import AsyncTransformer
from gloe._plotting_utils import PlottingSettings, NodeType

_T = TypeVar("_T")


class FilterAsync(Generic[_T], AsyncTransformer[Iterable[_T], Iterable[_T]]):
    """
    Async transformer used to filter values in an iterable using other async
    transformers instead of functions.

    Example:
        In this example, we fetch a list of users and then filter the administrators.::

            @async_transformer
            async def check_is_admin(user: User) -> bool: ...

            get_admin_users: AsyncTransformer[Group, Iterable[User]] = (
                get_users >> Filter(check_is_admin)
            )
    Args:
        filter_transformer: async transformer applied to each item of the input iterable
        and check if this item must be dropped or not.
    """

    def __init__(self, filter_transformer: AsyncTransformer[_T, bool]):
        super().__init__()
        self.filter_transformer = filter_transformer
        self.plotting_settings.invisible = True
        self._children = [filter_transformer]

        self._plotting_settings: PlottingSettings = PlottingSettings(
            has_children=True,
            node_type=NodeType.Transformer,
        )

    async def transform_async(self, data: Iterable[_T]) -> Iterable[_T]:
        """
        Args:
            data: incoming iterable to be filtered. The items of this iterable must be
                of type :code:`_T`.

        Returns:
            The filterd iterable.
        """
        filtered_result = []
        for item in data:
            result = await self.filter_transformer(item)
            if result:
                filtered_result.append(item)
        return filtered_result
