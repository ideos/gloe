import unittest

from gloe.exceptions import TransformerRequiresMultiArgs
from gloe.utils import forward

from gloe import async_transformer
from tests.lib.transformers import square, sum_tuple2, async_plus1


@async_transformer
async def sum2(num1: float, num2: float) -> float:
    return num1 + num2


class TestMultiArgsAsyncTransformer(unittest.IsolatedAsyncioTestCase):
    async def test_basic_call(self):
        @async_transformer
        async def concat(arg1: str, arg2: int) -> str:
            return arg1 + str(arg2)

        self.assertEqual(await concat("hello", 1), "hello1")

    async def test_divergent_composition(self):

        pipeline1 = forward[float]() >> (square, square) >> sum2

        self.assertEqual(await pipeline1(1), 2)

        pipeline2 = sum2 >> (square, square) >> sum2

        self.assertEqual(await pipeline2(1, 2), 18)

    async def test_single_arg_exception(self):
        @async_transformer
        async def concat(arg1: str, arg2: str) -> str:
            return arg1 + arg2

        with self.assertRaises(TransformerRequiresMultiArgs):
            await concat("test")  # type: ignore[call-arg]

    async def test_composition_transform_method(self):
        test1 = sum2 >> async_plus1

        result = await test1.transform_async((5, 3))
        self.assertIsNone(result)

        test2 = sum2 >> (async_plus1, async_plus1)

        result2 = await test2.transform_async((5, 3))
        self.assertIsNone(result2)

    async def test_noargs_basic_call(self):
        @async_transformer
        async def randint() -> int:
            return 6  # random.randint(1, 10)

        self.assertEqual(await randint(), 6)

    async def test_noargs_divergent_composition(self):
        @async_transformer
        async def randfloat() -> float:
            return 6.0

        pipeline = randfloat >> (square, square) >> sum_tuple2

        self.assertEqual(await pipeline(), 72.0)
