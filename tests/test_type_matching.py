import unittest
from typing import TypeVar
from collections.abc import Iterable

from gloe import Transformer
from gloe._typing_utils import _match_types, _specify_types
from gloe.collection import MapOver


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class TestTypeMatching(unittest.TestCase):
    def assertEqualTypes(self, type1, type2):
        self.assertEqual(str(type1), str(type2))

    def test_basic_case(self):
        generic = tuple[Iterable[A], tuple[int, Iterable[Transformer[str, B]], C]]
        specific = tuple[list[float], tuple[int, list[MapOver[str, dict]], list]]

        matched_types = _match_types(generic, specific)
        self.assertDictEqual(matched_types, {A: float, B: dict, C: list})

        new_generic = _specify_types(generic, matched_types)
        expected_type = tuple[
            Iterable[float], tuple[int, Iterable[Transformer[str, dict]], list]
        ]
        self.assertEqualTypes(new_generic, expected_type)
