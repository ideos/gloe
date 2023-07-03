import unittest

from src.gloe import EmptyBridgeOnDrop, bridge
from tests.lib.transformers import *


class TestTransformerBridges(unittest.TestCase):
    def test_basic_case(self):
        num_bridge = bridge[float]("num")

        graph = sum1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()

        self.assertEqual((10.0, 11.0), graph(10.0))

    def test_error_case(self):
        num_bridge = bridge[float]("num")

        graph = sum1 >> minus1 >> num_bridge.drop()

        self.assertRaises(EmptyBridgeOnDrop, lambda: graph(0))
