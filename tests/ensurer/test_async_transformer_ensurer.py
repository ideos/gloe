import asyncio
import unittest
from typing import TypeVar

from gloe import (
    async_transformer,
    ensure,
    UnsupportedTransformerArgException,
    AsyncTransformer,
)
from gloe.functional import partial_async_transformer
from gloe.utils import forward
from tests.lib.ensurers import (
    has_bar_key,
    is_int,
    has_foo_key,
    foo_key_removed,
    is_str,
    is_odd,
)
from tests.lib.exceptions import NumbersEqual, NumberIsEven, HasNotBarKey, IsNotInt
from tests.lib.transformers import async_plus1, minus1

_In = TypeVar("_In")

_DATA = {"foo": "bar"}


async def raise_an_error():
    await asyncio.sleep(0.1)
    raise NotImplementedError()


@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.01)
    return _DATA


class RequestData(AsyncTransformer[str, dict[str, str]]):
    async def transform_async(self, url: str) -> dict[str, str]:
        await asyncio.sleep(0.01)
        return _DATA


_URL = "http://my-service"


class TestAsyncTransformerEnsurer(unittest.IsolatedAsyncioTestCase):
    async def test_ensure_async_transformer(self):
        @ensure(outcome=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.01)
            return _DATA

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

        @ensure(incoming=[is_int])
        @async_transformer
        async def ensured_request2(url: str) -> dict[str, str]:
            await asyncio.sleep(0.01)
            return _DATA

        pipeline2 = ensured_request2 >> forward()

        with self.assertRaises(IsNotInt):
            await pipeline2(_URL)

        @async_transformer
        async def ensured_request3(url: str) -> dict[str, str]:
            await asyncio.sleep(0.01)
            return _DATA

        @ensure(changes=[foo_key_removed])
        @async_transformer
        async def remove_foo_key(data: dict[str, str]) -> dict[str, str]:
            new_data = {**data}
            await asyncio.sleep(0.01)
            del new_data["foo"]
            return new_data

        pipeline3 = ensured_request3 >> remove_foo_key
        result = await pipeline3(_URL)
        self.assertDictEqual(result, {})

        @ensure(outcome=[has_foo_key])
        @async_transformer
        async def ensured_request4(url: str) -> dict[str, str]:
            await asyncio.sleep(0.01)
            return _DATA

        pipeline4 = ensured_request4 >> forward()

        self.assertDictEqual(await pipeline4(_URL), _DATA)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[is_str], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = ensured_delayed_request(0.01) >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

        @ensure(incoming=[is_int])
        @partial_async_transformer
        async def ensured_delayed_request2(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline2 = ensured_delayed_request2(0.01) >> forward()

        with self.assertRaises(IsNotInt):
            await pipeline2(_URL)

        @ensure(incoming=[is_str])
        @partial_async_transformer
        async def ensured_delayed_request3(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline3 = ensured_delayed_request3(0.01) >> forward()

        self.assertDictEqual(await pipeline3(_URL), _DATA)

        @ensure(incoming=[is_str], outcome=[has_foo_key])
        @partial_async_transformer
        async def ensured_delayed_request4(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline4 = ensured_delayed_request4(0.01) >> forward()

        self.assertDictEqual(await pipeline4(_URL), _DATA)

    async def test_async_transformer_wrong_arg(self):
        def next_transformer():
            pass

        @ensure(outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        with self.assertRaises(UnsupportedTransformerArgException):
            ensured_delayed_request(0.01) >> next_transformer  # type: ignore

    async def test_async_pipeline_ensurer_error_handling(self):
        def is_not_equal(_in: int, _out: int):
            if _in == _out:
                raise NumbersEqual()

        incoming_odd_ensurer = ensure(incoming=[is_odd])
        ensured_pipeline = incoming_odd_ensurer(async_plus1 >> minus1)
        with self.assertRaises(NumberIsEven):
            await ensured_pipeline(2)

        ensured_pipeline = incoming_odd_ensurer(minus1 >> async_plus1)
        with self.assertRaises(NumberIsEven):
            await ensured_pipeline(2)

        outcome_odd_ensurer = ensure(outcome=[is_odd])
        ensured_pipeline = outcome_odd_ensurer(async_plus1 >> minus1)
        with self.assertRaises(NumberIsEven):
            await ensured_pipeline(2)

        ensured_pipeline = outcome_odd_ensurer(minus1 >> async_plus1)
        with self.assertRaises(NumberIsEven):
            await ensured_pipeline(2)

        not_equal_ensurer = ensure(changes=[is_not_equal])
        ensured_pipeline = not_equal_ensurer(async_plus1 >> minus1) >> forward()
        with self.assertRaises(NumbersEqual):
            await ensured_pipeline(2)

        ensured_pipeline = not_equal_ensurer(minus1 >> async_plus1) >> forward()
        with self.assertRaises(NumbersEqual):
            await ensured_pipeline(2)

    async def test_async_pipeline_ensurer_success(self):
        outcome_odd_ensurer = ensure(outcome=[is_odd])
        ensured_pipeline = outcome_odd_ensurer(async_plus1 >> minus1)
        self.assertEqual(1, await ensured_pipeline(1))

        outcome_odd_ensurer = ensure(outcome=[is_odd])
        ensured_pipeline = outcome_odd_ensurer(minus1 >> async_plus1)
        self.assertEqual(1, await ensured_pipeline(1))


if __name__ == "__main__":
    unittest.main()
