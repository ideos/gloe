"""Runtime failures stay explicit even when a caller bypasses static checking."""

import inspect
import sys
from contextlib import redirect_stdout
from io import StringIO
from collections.abc import Coroutine
from typing import Any
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import patch

import gloe


def increment(value: int) -> int:
    return value + 1


class ValidatorBoundaryTests(IsolatedAsyncioTestCase):
    async def test_invalid_validator_collections_and_async_validators(self) -> None:
        for value in (None, [increment, 1], "validator"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "Validators"):
                    gloe.ensure(incoming=value)

        async def asynchronous(value: int) -> None:
            pass

        with self.assertRaisesRegex(TypeError, "synchronous"):
            gloe.ensure(outcome=asynchronous)

        class AsyncValidator:
            async def __call__(self, value: int) -> None:
                pass

        with self.assertRaisesRegex(TypeError, "synchronous"):
            gloe.ensure(incoming=AsyncValidator())

    async def test_accidental_validator_coroutine_is_closed(self) -> None:
        created: list[Coroutine[Any, Any, None]] = []

        async def asynchronous(value: int) -> None:
            pass

        def deferred(value: int) -> Coroutine[Any, Any, None]:
            result = asynchronous(value)
            created.append(result)
            return result

        checked = gloe.ensure(incoming=deferred)(increment)
        with self.assertRaisesRegex(TypeError, "None or raise"):
            await (gloe.input() >> checked)(1)
        self.assertEqual(inspect.getcoroutinestate(created[0]), inspect.CORO_CLOSED)


class ConstructionBoundaryTests(TestCase):
    def test_decorators_do_not_resolve_forward_annotations(self) -> None:
        # Exercise native deferred annotations on 3.14, not the future import.
        source = """
import gloe

@gloe.transformer
def configured(value: Later, *, enabled: bool) -> Later:
    return value

@gloe.ensure()
def checked(value: Later) -> Later:
    return value

def join(left: Later, right: Later) -> Later:
    return left

adapted = gloe.ensure()(gloe.unpack(join))

class Later:
    pass

value = Later()
assert configured(enabled=True)(value) is value
assert checked(value) is value
assert adapted((value, value)) is value
"""
        if sys.version_info < (3, 14):
            source = "from __future__ import annotations\n" + source
        exec(compile(source, "<forward-annotations>", "exec", dont_inherit=True), {})

    def test_bad_roots_and_configured_branches_fail_before_invocation(self) -> None:
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.Transformer(None)
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.condition(increment, then=None, otherwise=increment)
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.parallel([increment, None])

    def test_missing_optional_plot_dependency_has_install_guidance(self) -> None:
        pipe = gloe.input() >> increment
        with patch.dict("sys.modules", {"pygraphviz": None}):
            with self.assertRaisesRegex(ImportError, r"gloe\[plot\]"):
                pipe.to_image("unused.svg")


class CallableOverrideTests(IsolatedAsyncioTestCase):
    async def test_custom_callable_behavior_is_not_flattened_away(self) -> None:
        class Custom(gloe.Transformer[[int], object]):
            async def __call__(self, value: int) -> str:
                return f"custom:{value}"

        stage = Custom(increment)
        pipe = gloe.input[int]() >> stage
        self.assertEqual(await pipe(2), "custom:2")
        labels = [node["label"] for node in pipe.graph().nodes.values()]
        self.assertIn("Custom", labels)
        self.assertNotIn("increment", labels)


class PlainBuiltinStages(IsolatedAsyncioTestCase):
    async def test_original_arithmetic_fork_sum_and_print(self) -> None:
        @gloe.transformer
        def add(value: int, *, amount: int) -> int:
            return value + amount

        def multiply(value: int) -> int:
            return value * 2

        def divide(value: int) -> float:
            return value / 2

        pipe = (
            gloe.input()
            >> add(amount=2)
            >> (multiply, divide)
            >> sum
            >> print  # noqa: F633
        )
        output = StringIO()
        with redirect_stdout(output):
            result = await pipe(2)
        self.assertIsNone(result)
        self.assertEqual(output.getvalue(), "10.0\n")


class AdaptedValidationTests(IsolatedAsyncioTestCase):
    async def test_ensure_observes_the_tuple_adapter_signature(self) -> None:
        observed: list[tuple[int, str]] = []

        def before(values: tuple[int, str]) -> None:
            observed.append(values)

        def join(value: int, label: str) -> str:
            return f"{label}:{value}"

        for function in (join, gloe.transformer(join)()):
            adapted = gloe.ensure(incoming=before)(gloe.unpack(function))
            self.assertEqual(await (gloe.input() >> adapted)((2, "count")), "count:2")
            self.assertEqual(tuple(inspect.signature(adapted).parameters), ("values",))
        self.assertEqual(observed, [(2, "count"), (2, "count")])
