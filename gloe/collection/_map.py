from typing import Generic, TypeVar, Iterable

from gloe.transformers import Transformer

_T = TypeVar("_T", contravariant=True)
_U = TypeVar("_U", covariant=True)


class Map(Generic[_T, _U], Transformer[Iterable[_T], Iterable[_U]]):
    """
    Transformer used to map values in an iterable using other transformers instead of
    functions.

    Example:
        In this example, we fetch a list of users that belongs to a group.
        Then, we get the posts of each user and finally turn it into a single list
        of posts.::

            @transformer
            def get_user_posts(user: User) -> list[Post]: ...

            get_posts_by_group: Transformer[Group, Iterable[Post]] = (
                get_users_by_group >> Map(get_user_posts) >> flatten
            )
    Args:
        mapping_transformer: transformer applied to each item of the
            input iterable the yield the mapped item of the output iterable.
    """

    def __init__(self, mapping_transformer: Transformer[_T, _U]):
        super().__init__()
        self.mapping_transformer = mapping_transformer
        self.plotting_settings.has_children = True
        self._children = [mapping_transformer]

    def transform(self, data: Iterable[_T]) -> Iterable[_U]:
        """
        Args:
            data: incoming iterable to be mapped. The items of this iterable must be of
                type :code:`_T`.

        Returns:
            The mapped iterable. The items of this new iterable are of type :code:`_U`.
        """
        mapping_result = []
        for item in data:
            mapping_result.append(self.mapping_transformer(item))
        return mapping_result
