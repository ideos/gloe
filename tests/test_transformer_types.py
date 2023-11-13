import os
import unittest
from pathlib import Path
from typing import Iterable, TypeVar, Any

from typing_extensions import assert_type

from src.gloe.transformers import Transformer
from src.gloe import ensure
from src.gloe.utils import forward
from src.gloe.experimental.bridge import bridge
from src.gloe.collection import Map
from tests.lib.conditioners import *
from tests.lib.ensurers import is_even, same_value, same_value_int, is_greater_than_10
from tests.lib.transformers import *
from mypy import api


In = TypeVar("In")


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

        conditioned_graph = square >> square_root >> if_not_zero.Then(plus1).Else(minus1)

        assert_type(conditioned_graph, Transformer[float, float])

        conditioned_graph2 = square >> square_root >> if_not_zero.Then(to_string).Else(square)

        assert_type(conditioned_graph2, Transformer[float, str | float])

    def _test_chained_condition_flow_types(self):
        """
        Test the most simple transformer typing
        """

        chained_conditions_graph = (
            if_is_even
            .Then(square)
            .ElseIf(lambda x: x < 10)
            .Then(to_string)
            .ElseNone()
        )

        assert_type(chained_conditions_graph, Transformer[float, float | str | None])

    def _test_curried_transformer(self):
        """
        Test the curried transformer typing
        """

        log2 = logarithm(base=2)
        assert_type(log2, Transformer[float,  float])

        repeater = repeat(n_times=2, linebreak=True)
        assert_type(repeater, Transformer[str,  str])

    def _test_transformer_init(self):
        """
        Test the transformer initializer typing
        """

        formatter = format_currency(thousands_separator=',')

        assert_type(formatter, Transformer[float, str])

    def _test_transformer_map(self):
        """
        Test the transformer map collection operation
        """

        mapped_logarithm = forward[Iterable[float]]() >> Map(format_currency(thousands_separator=','))

        assert_type(mapped_logarithm, Transformer[Iterable[float], Iterable[str]])

    def _test_transformer_ensurer(self):
        @ensure(incoming=[is_even])
        @transformer
        def t1(n1: int) -> int:
            return n1 * n1

        @ensure(outcome=[is_even])
        @transformer
        def t2(n1: int) -> int:
            return n1 * n1

        @ensure(changes=[same_value_int])
        @transformer
        def t3(n1: int) -> int:
            return n1 * n1

        @ensure(incoming=[is_even], outcome=[is_even])
        @transformer
        def t4(n1: int) -> int:
            return n1 * n1

        @ensure(incoming=[is_even], outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def t5(n1: int) -> float:
            return n1 * n1

        @ensure(outcome=[is_greater_than_10], changes=[same_value])
        @transformer
        def t6(num: float) -> float:
            return num

        assert_type(t1, Transformer[int, int])
        assert_type(t2, Transformer[int, int])
        assert_type(t3, Transformer[int, int])
        assert_type(t4, Transformer[int, int])
        assert_type(t5, Transformer[int, float])
        assert_type(t6, Transformer[float, float])

    def _test_transformer_init_ensurer(self):
        @ensure(incoming=[is_even])
        @partial_transformer
        def ti1(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(outcome=[is_even])
        @partial_transformer
        def ti2(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(changes=[same_value_int])
        @partial_transformer
        def ti3(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_even], outcome=[is_even])
        @partial_transformer
        def ti4(n1: int, n2: int) -> int:
            return n1 * n2

        @ensure(incoming=[is_even], changes=[same_value_int])
        @partial_transformer
        def ti5(n1: int, n2: int) -> int:
            return n1 * n2

        assert_type(ti1(2), Transformer[int, int])
        assert_type(ti2(2), Transformer[int, int])
        assert_type(ti3(2), Transformer[int, int])
        assert_type(ti4(2), Transformer[int, int])
        assert_type(ti5(2), Transformer[int, int])

    def _test_bridge(self):
        num_bridge = bridge[float]("num")

        graph = plus1 >> num_bridge.pick() >> minus1 >> num_bridge.drop()

        assert_type(graph, Transformer[float, tuple[float, float]])

    def _test_generic_transformer(self):
        @partial_transformer
        def tuplicate(data: In) -> Tuple[In, In]:
            return data, data

        @partial_transformer
        def pick_first(data: Tuple[In, Any]) -> In:
            return data[0]

        graph = square >> tuplicate() >> pick_first() >> forward()

        assert_type(graph, Transformer[float, float])

    def test_all(self):
        file_path = Path(os.path.abspath(__file__))
        config_path = (file_path.parent.parent / 'mypy.ini').absolute()
        result = api.run([__file__, '--follow-imports=silent', f'--config-file={config_path}'])
        self.assertRegex(result[0], 'Success')


if __name__ == '__main__':
    unittest.main()
