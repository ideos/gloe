import unittest

from gloe.functional import transformer
from gloe.collection import Map, MapOver, Filter
from tests.lib.transformers import square, plus1, sum_tuple2


class TestTransformerCollection(unittest.TestCase):
    def test_transformer_multiargs_inside_map(self):
        @transformer
        def many_args(arg1: str, arg2: int) -> str:
            return arg1 + str(arg2)

        mapping = Map(many_args)

        result = list(mapping([("hello", 1), ("world", 2)]))

        self.assertListEqual(result, ["hello1", "world2"])

    def test_transformer_map(self):
        """
        Test the map transformer
        """

        mapping1 = Map(square) >> Map(plus1)
        mapping2 = Map(square >> plus1)

        seq = [10.0, 9.0, 3.0, 2.0, -1.0]
        result1 = list(mapping1(seq))
        result2 = list(mapping2(seq))

        expected = [101.0, 82.0, 10.0, 5.0, 2.0]
        self.assertListEqual(expected, result1)
        self.assertListEqual(expected, result2)

    def test_transformer_filter(self):
        """
        Test the filter transformer
        """

        @transformer
        def is_even(num: int) -> bool:
            return num % 2 == 0

        _filter = Filter(is_even)

        seq = [10, 9, 3, 2, 1]
        result = _filter(seq)

        expected = [10, 2]
        self.assertListEqual(expected, list(result))

    def test_transformer_map_over(self):
        """
        Test the map over transformer
        """

        data = [10.0, 9.0, 3.0, 2.0, -1.0]
        mapping = MapOver(data, sum_tuple2) >> Map(plus1)

        result = list(mapping(-1.0))

        self.assertListEqual(result, data)

    def test_transformer_multiargs_inside_map_over(self):
        roles: list[str] = ['admin_role', 'member_role', 'manager_role']

        @transformer
        def format_user(user: str, role: str) -> str:
            return f'User {user} has the role {role}.'

        format_users = MapOver(roles, format_user)

        self.assertListEqual(
            format_users('Alice'),
            ['User Alice has the role admin_role.',
             'User Alice has the role member_role.',
             'User Alice has the role manager_role.']
        )
