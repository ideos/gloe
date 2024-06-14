from typing import Generic, TypeVar, Iterable

from gloe._plotting_utils import PlottingSettings, NodeType
from gloe.transformers import Transformer

_T = TypeVar("_T")


class Filter(Generic[_T], Transformer[Iterable[_T], Iterable[_T]]):
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

    def __init__(self, filter_transformer: Transformer[_T, bool]):
        super().__init__()
        self.filter_transformer = filter_transformer
        self.plotting_settings.invisible = True
        self._children = [filter_transformer]

        self._plotting_settings: PlottingSettings = PlottingSettings(
            has_children=True,
            node_type=NodeType.Transformer,
        )

    def transform(self, data: Iterable[_T]) -> Iterable[_T]:
        """
        Args:
            data: incoming iterable to be filtered. The items of this iterable must be
                of type :code:`_T`.

        Returns:
            The filterd iterable.
        """
        filtered_result = []
        for item in data:
            if self.filter_transformer(item):
                filtered_result.append(item)
        return filtered_result
