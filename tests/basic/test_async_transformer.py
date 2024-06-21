import asyncio
import unittest
from inspect import Signature
from typing import TypeVar, Any, cast

from gloe import (
    async_transformer,
    ensure,
    UnsupportedTransformerArgException,
    transformer,
    AsyncTransformer,
    TransformerException,
    BaseTransformer,
)
from gloe.async_transformer import _execute_async_flow
from gloe.functional import partial_async_transformer
from gloe.utils import forward
from tests.lib.exceptions import LnOfNegativeNumber
from tests.lib.transformers import async_plus1, async_natural_logarithm

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

        self.assertDictEqual(_DATA, result)

    async def test_begin_with_transformer(self):
        test_forward = forward[str]() >> request_data

        result = await test_forward(_URL)

        self.assertDictEqual(_DATA, result)

    async def test_async_on_divergent_connection(self):
        test_forward = forward[str]() >> (forward[str](), request_data)

        result = await test_forward(_URL)

        self.assertEqual((_URL, _DATA), result)

    async def test_divergent_connection_from_async(self):
        test_forward = request_data >> (
            forward[dict[str, str]](),
            forward[dict[str, str]](),
        )

        result = await test_forward(_URL)

        self.assertEqual((_DATA, _DATA), result)

        @async_transformer
        async def request_foo(url: str) -> str:
            await asyncio.sleep(0.01)
            return "foo"

        @async_transformer
        async def request_bar(url: str) -> str:
            await asyncio.sleep(0.01)
            return "bar"

        @async_transformer
        async def request_baz(url: str) -> str:
            await asyncio.sleep(0.01)
            return "baz"

        test_forward2 = forward[str]() >> (
            request_foo,
            request_bar,
            request_baz,
        )

        result2 = await test_forward2(_URL)

        self.assertEqual(("foo", "bar", "baz"), result2)

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
        self.assertEqual(_DATA, result)

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

        @transformer
        def dict_to_str(_dict: dict) -> str:
            return str(_dict)

        request_and_serialize = request_data >> dict_to_str
        self.assertEqual(
            repr(request_and_serialize), "dict -> (2 transformers omitted) -> str"
        )

    async def test_exhausting_large_flow(self):
        """
        Test the instantiation of large graph
        """
        graph = async_plus1

        max_iters = 1500
        for i in range(max_iters):
            graph = graph >> async_plus1

        result = await graph(0)
        self.assertEqual(result, max_iters + 1)

    async def test_async_transformer_error_handling(self):
        """
        Test if a raised error stores the correct TransformerException as its cause
        """

        async_graph = async_plus1 >> async_natural_logarithm

        try:
            await async_graph(-2)
        except LnOfNegativeNumber as exception:
            self.assertEqual(type(exception.__cause__), TransformerException)

            exception_ctx = cast(TransformerException, exception.__cause__)
            self.assertEqual(async_natural_logarithm, exception_ctx.raiser_transformer)

    async def test_execute_async_wrong_flow(self):

        flow = [2]
        with self.assertRaises(NotImplementedError):
            await _execute_async_flow(flow, 1)  # type: ignore

        class WrongTransformer(BaseTransformer):
            def signature(self) -> Signature:
                return Signature()

        flow2 = [WrongTransformer()]
        with self.assertRaises(NotImplementedError):
            await _execute_async_flow(flow2, 1)  # type: ignore

    async def test_composition_transform_method(self):
        test3 = forward[float]() >> async_plus1

        result = await test3.transform_async(5)
        self.assertIsNone(result)
        test2 = forward[float]() >> (async_plus1, async_plus1)

        result2 = await test2.transform_async(5)
        self.assertIsNone(result2)
