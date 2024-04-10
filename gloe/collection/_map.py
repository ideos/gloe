from typing import Generic, TypeVar

from gloe.transformers import Transformer

_T = TypeVar("_T")
_S = TypeVar("_S")
_U = TypeVar("_U")


class Map(Generic[_T, _U], Transformer[list[_T], list[_U]]):
    """
    Transformer used to map values in a list using other transformers instead of
    functions.

    Unfortunately, we must use :code:`list` instead of a more general type like
    :code:`Iterable`, because neither Python nor Mypy recognizes :code:`list[T]` as a
    subclass of :code:`Iterable[T]`. A consequence of this limitation is::

        get_user_posts: Transformer[User, list[Post]]
        filter_archived_posts: Transformer[Iterable[Post], Iterable[Post]]

        get_user_posts >> filter_archived_posts
        # ERROR: Unsupported operand types for >> ("Transformer[User, list[Post]]" and "Transformer[Iterable[Post], Iterable[Post]]")

    To solve this problem, we need to use `Higher Kinded Types
    <https://sobolevn.me/2020/10/higher-kinded-types-in-python>`_, but this is only currently possible using
    `Mypy Plugins <https://mypy.readthedocs.io/en/stable/extending_mypy.html>`_.
    Gloe aims to avoid the need for such solutions.

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
            input list the yield the mapped item of the output list.
    """

    def __init__(self, mapping_transformer: Transformer[_T, _U]):
        super().__init__()
        self.mapping_transformer = mapping_transformer
        self._invisible = True
        self._children = [mapping_transformer]

        mapping_transformer._graph_node_props = mapping_transformer.graph_node_props | {
            "parent_id": self.instance_id,
            "bounding_box": True,
            "box_label": "mapping",
        }

    def transform(self, data: list[_T]) -> list[_U]:
        """
        Args:
            data: incoming list to be mapped. The items of this list must be of
                type :code:`_T`.

        Returns:
            The mapped list. The items of this new list are of type :code:`_U`.
        """
        mapping_result = []
        for item in data:
            mapping_result.append(self.mapping_transformer(item))
        return mapping_result
