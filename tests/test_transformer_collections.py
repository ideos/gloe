import unittest

from gloe.collection import Map, MapOver
from tests.lib.transformers import square, plus1, sum_tuple2


class TestTransformerCollections(unittest.TestCase):
    def test_transformer_map(self):
        """
        Test the mapping transformer
        """

        mapping1 = Map(square) >> Map(plus1)
        mapping2 = Map(square >> plus1)

        seq = [10.0, 9.0, 3.0, 2.0, -1.0]
        result1 = list(mapping1(seq))
        result2 = list(mapping2(seq))

        expected = [101.0, 82.0, 10.0, 5.0, 2.0]
        self.assertListEqual(expected, result1)
        self.assertListEqual(expected, result2)

    def test_transformer_map_over(self):
        """
        Test the mapping transformer
        """

        data = [10.0, 9.0, 3.0, 2.0, -1.0]
        mapping = MapOver(data, sum_tuple2) >> Map(plus1)

        result = list(mapping(-1.0))

        self.assertListEqual(result, data)
