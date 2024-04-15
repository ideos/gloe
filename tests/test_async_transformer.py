import asyncio
import unittest
from typing import TypeVar, Any
from gloe import (
    async_transformer,
    ensure,
    UnsupportedTransformerArgException,
    transformer,
    AsyncTransformer,
)
from gloe.async_transformer import _Out
from gloe.functional import partial_async_transformer
from gloe.utils import forward

_In = TypeVar("_In")

_DATA = {"foo": "bar"}


@async_transformer
async def request_data(url: str) -> dict[str, str]:
    await asyncio.sleep(0.1)
    return _DATA


class RequestData(AsyncTransformer[str, dict[str, str]]):
    async def transform_async(self, url: str) -> dict[str, str]:
        await asyncio.sleep(0.1)
        return _DATA


class HasNotBarKey(Exception):
    pass


class HasNotFooKey(Exception):
    pass


class HasFooKey(Exception):
    pass


class IsNotInt(Exception):
    pass


def has_bar_key(data: dict[str, str]):
    if "bar" not in data.keys():
        raise HasNotBarKey()


def has_foo_key(data: dict[str, str]):
    if "foo" not in data.keys():
        raise HasNotBarKey()


def is_int(data: Any):
    if type(data) is not int:
        raise IsNotInt()


def is_str(data: Any):
    if type(data) is not str:
        raise Exception("data is not string")


def foo_key_removed(incoming: dict[str, str], outcome: dict[str, str]):
    if "foo" not in incoming.keys():
        raise HasNotFooKey()

    if "foo" in outcome.keys():
        raise HasFooKey()


_URL = "http://my-service"


class TestAsyncTransformer(unittest.IsolatedAsyncioTestCase):
    async def test_basic_case(self):
        test_forward = request_data >> forward()

        result = await test_forward(_URL)

        self.assertDictEqual(result, _DATA)

    async def test_begin_with_transformer(self):
        test_forward = forward[str]() >> request_data

        result = await test_forward(_URL)

        self.assertDictEqual(result, _DATA)

    async def test_async_on_divergent_connection(self):
        test_forward = forward[str]() >> (forward[str](), request_data)

        result = await test_forward(_URL)

        self.assertEqual(result, (_URL, _DATA))

    async def test_divergent_connection_from_async(self):
        test_forward = request_data >> (
            forward[dict[str, str]](),
            forward[dict[str, str]](),
        )

        result = await test_forward(_URL)

        self.assertEqual(result, (_DATA, _DATA))

    async def test_partial_async_transformer(self):
        @partial_async_transformer
        async def sleep_and_forward(data: dict[str, str], delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return data

        pipeline = sleep_and_forward(0.1) >> forward()

        result = await pipeline(_DATA)

        self.assertEqual(result, _DATA)

    async def test_ensure_async_transformer(self):
        @ensure(outcome=[has_bar_key])
        @async_transformer
        async def ensured_request(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline = ensured_request >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

        @ensure(incoming=[is_int])
        @async_transformer
        async def ensured_request2(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline2 = ensured_request2 >> forward()

        with self.assertRaises(IsNotInt):
            await pipeline2(_URL)

        @async_transformer
        async def ensured_request3(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        @ensure(changes=[foo_key_removed])
        @async_transformer
        async def remove_foo_key(data: dict[str, str]) -> dict[str, str]:
            new_data = {**data}
            await asyncio.sleep(0.1)
            del new_data["foo"]
            return new_data

        pipeline3 = ensured_request3 >> remove_foo_key

        result = await pipeline3(_URL)
        self.assertDictEqual(result, {})

        @ensure(outcome=[has_foo_key])
        @async_transformer
        async def ensured_request4(url: str) -> dict[str, str]:
            await asyncio.sleep(0.1)
            return _DATA

        pipeline4 = ensured_request4 >> forward()

        self.assertDictEqual(await pipeline4(_URL), _DATA)

    async def test_ensure_partial_async_transformer(self):
        @ensure(incoming=[is_str], outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = ensured_delayed_request(0.1) >> forward()

        with self.assertRaises(HasNotBarKey):
            await pipeline(_URL)

        @ensure(incoming=[is_int])
        @partial_async_transformer
        async def ensured_delayed_request2(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline2 = ensured_delayed_request2(0.1) >> forward()

        with self.assertRaises(IsNotInt):
            await pipeline2(_URL)

        @ensure(incoming=[is_str])
        @partial_async_transformer
        async def ensured_delayed_request3(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline3 = ensured_delayed_request3(0.1) >> forward()

        self.assertDictEqual(await pipeline3(_URL), _DATA)

    async def test_async_transformer_wrong_arg(self):
        def next_transformer():
            pass

        @ensure(outcome=[has_bar_key])
        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        with self.assertRaises(UnsupportedTransformerArgException):
            pipeline = ensured_delayed_request(0.1) >> next_transformer

    async def test_async_transformer_copy(self):
        @transformer
        def add_slash(path: str) -> str:
            return path + "/"

        @partial_async_transformer
        async def ensured_delayed_request(url: str, delay: float) -> dict[str, str]:
            await asyncio.sleep(delay)
            return _DATA

        pipeline = add_slash >> ensured_delayed_request(0)

        pipeline = pipeline.copy()
        result = await pipeline(_URL)
        self.assertEqual(result, _DATA)

    def test_async_transformer_wrong_signature(self):
        with self.assertWarns(RuntimeWarning):

            @async_transformer  # type: ignore
            async def many_args(arg1: str, arg2: int):
                await asyncio.sleep(1)
                return arg1, arg2

    def test_async_transformer_signature_representation(self):
        signature = request_data.signature()

        self.assertEqual(str(signature), "(url: str) -> dict[str, str]")

    def test_async_transformer_representation(self):
        self.assertEqual(repr(request_data), "str -> (request_data) -> dict[str, str]")

        class_request_data = RequestData()
        self.assertEqual(
            repr(class_request_data), "str -> (RequestData) -> dict[str, str]"
        )
