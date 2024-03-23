import unittest

from gloe.experimental import EmptyBridgeOnDrop, bridge
from tests.lib.transformers import plus1, minus1


class TestTransformerBridges(unittest.TestCase):
    def test_basic_case(self):
        num_bridge = bridge[float]("num")

        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()

        self.assertEqual((10.0, 11.0), graph(10.0))

    def test_error_case(self):
        num_bridge = bridge[float]("num")

        graph = plus1 >> minus1 >> num_bridge.drop()

        self.assertRaises(EmptyBridgeOnDrop, lambda: graph(0))
