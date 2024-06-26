import unittest

from tests.lib.transformers import logarithm


class TestPartialTransformer(unittest.TestCase):
    def test_partial_transformer(self):
        """
        Test the curried transformer
        """

        graph = logarithm(base=2)
        self.assertEqual(graph(2), 1)
        self.assertEqual(graph.label, "logarithm")
