import asyncio
import unittest
from typing_extensions import assert_type

from gloe import partial_async_transformer, AsyncTransformer, Transformer
from gloe.utils import forward
from tests.lib.transformers import logarithm, repeat, format_currency
from tests.type_utils.mypy_test_suite import MypyTestSuite


class TestPartialTransformerTypes(unittest.IsolatedAsyncioTestCase, MypyTestSuite):
    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: int) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(1) >> forward()

        assert_type(pipeline, AsyncTransformer[dict[str, str], dict[str, str]])

    def test_partial_transformer(self):
        """
        Test the curried transformer typing
        """

        log2 = logarithm(base=2)
        assert_type(log2, Transformer[float, float])

        repeater = repeat(n_times=2, linebreak=True)
        assert_type(repeater, Transformer[str, str])

    def test_transformer_init(self):
        """
        Test the transformer initializer typing
        """

        formatter = format_currency(thousands_separator=",")

        assert_type(formatter, Transformer[float, str])
