import os
import unittest
from pathlib import Path
from typing import Union

from typing_extensions import assert_type

from tests.lib.conditioners import if_not_zero
from tests.lib.transformers import *
from transformer import Transformer
from mypy import api


class TestTransformerTypes(unittest.TestCase):
    def _test_transformer_simple_typing(self):
        """
        Test the most simple transformer typing
        """

        graph = square

        assert_type(graph, Transformer[float, float])

    def _test_simple_flow_typing(self):
        """
        Test the most simple transformer typing
        """

        graph = square >> square_root

        assert_type(graph, Transformer[float, float])

    def _test_flow_with_mixed_types(self):
        """
        Test the most simple transformer typing
        """

        graph = square >> square_root >> to_string

        assert_type(graph, Transformer[float, str])

    def _test_divergent_flow_types(self):
        """
        Test the most simple transformer typing
        """

        graph = square >> square_root >> (
            to_string,
            square
        )

        assert_type(graph, Transformer[float, Tuple[str, float]])

    def _test_conditioned_flow_types(self):
        """
        Test the most simple transformer typing
        """

        conditioned_graph = square >> square_root >> if_not_zero.Then(sum1).Else(minus1)

        assert_type(conditioned_graph, Transformer[float, float])

        conditioned_graph2 = square >> square_root >> if_not_zero.Then(to_string).Else(square)

        assert_type(conditioned_graph2, Transformer[float, str | float])

    def test_all(self):
        file_path = Path(os.path.abspath(__file__))
        config_path = (file_path.parent.parent / 'mypy.ini').absolute()
        result = api.run([__file__, '--follow-imports=silent', f'--config-file={config_path}'])
        self.assertRegex(result[0], 'Success')


if __name__ == '__main__':
    unittest.main()
