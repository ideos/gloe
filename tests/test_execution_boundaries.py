"""Failure, lifetime, and reuse contracts across the public execution helpers."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Iterator
from contextlib import aclosing
from unittest import IsolatedAsyncioTestCase, TestCase

import gloe


class ExecutionBoundaries(IsolatedAsyncioTestCase):
    async def test_collection_failure_stops_consumption_and_preserves_exception(
        self,
    ) -> None:
        for helper in (gloe.map, gloe.filter):
            consumed: list[int] = []
            called: list[int] = []
            failure = ValueError("bad item")

            def values() -> Iterator[int]:
                for value in range(4):
                    consumed.append(value)
                    yield value

            async def apply(value: int) -> bool:
                called.append(value)
                if value == 1:
                    raise failure
                return True

            with self.subTest(helper=helper.__name__):
                with self.assertRaises(ValueError) as caught:
                    await (gloe.input() >> helper(apply))(values())
                self.assertIs(caught.exception, failure)
                self.assertEqual(called, [0, 1])
                self.assertEqual(consumed, [0, 1])

    async def test_sequential_failure_does_not_start_later_effects(self) -> None:
        calls: list[str] = []
        failure = LookupError("missing")

        async def first(value: int) -> int:
            calls.append("first")
            return value

        def fail(value: int) -> int:
            calls.append("fail")
            raise failure

        async def last(value: int) -> int:
            calls.append("last")
            return value

        pipe = gloe.input[int]() >> gloe.sequential([first, fail, last])
        with self.assertRaises(LookupError) as caught:
            await pipe(1)
        self.assertIs(caught.exception, failure)
        self.assertEqual(calls, ["first", "fail"])

    async def test_dynamic_branch_configuration_is_snapshotted_not_results(
        self,
    ) -> None:
        calls: list[int] = []

        def track(value: int) -> int:
            calls.append(value)
            return value * 2

        configured = [track]
        parallel = gloe.input[int]() >> gloe.parallel(iter(configured))
        sequential = gloe.input[int]() >> gloe.sequential(configured)
        configured.clear()
        for pipe in (parallel, sequential):
            self.assertEqual(await pipe(2), [4])
            self.assertEqual(await pipe(3), [6])
        self.assertEqual(calls, [2, 3, 2, 3])

    async def test_collection_cancellation_propagates_and_closes_owned_stream(
        self,
    ) -> None:
        events: list[str] = []
        started = asyncio.Event()

        async def stream():
            try:
                yield 1
                await asyncio.Event().wait()
            finally:
                events.append("closed")

        async def consume(value: int) -> int:
            async with aclosing(stream()) as source:
                async for item in source:
                    started.set()
                    await asyncio.Event().wait()
            return value

        pipe = gloe.input[list[int]]() >> gloe.map(consume)
        task = asyncio.create_task(pipe([1, 2]))
        await asyncio.wait_for(started.wait(), timeout=1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(events, ["closed"])

    async def test_failed_changes_validation_blocks_join_effects(self) -> None:
        effects: list[int] = []

        def same(before: int, after: int) -> None:
            if before != after:
                raise ValueError("changed")

        @gloe.ensure(changes=same)
        async def altered(value: int) -> int:
            return value + 1

        def save(value: tuple[int, int]) -> int:
            effects.append(value[1])
            return value[1]

        pipe = gloe.input[int]() >> (gloe.input(), altered) >> save
        with self.assertRaisesRegex(ValueError, "changed"):
            await pipe(1)
        self.assertEqual(effects, [])

    async def test_mixed_generated_plans_match_direct_arithmetic(self) -> None:
        # A fixed seed makes failures reproducible. Vary plan width and depth,
        # sync/async stage forms, empty forks, and reused complete subplans.
        rng = random.Random(812)
        for case in range(80):
            value = rng.randrange(-20, 21)
            expected = value
            pipe = gloe.input[int]()
            for _ in range(rng.randrange(1, 8)):
                amount = rng.randrange(-5, 6)
                width = rng.randrange(0, 10)

                def add(value: int, *, amount: int = amount) -> int:
                    return value + amount

                async def double(value: int) -> int:
                    return value * 2

                subplan = gloe.input[int]() >> add >> double
                branches = tuple(subplan for _ in range(width))
                pipe = pipe >> gloe.parallel(branches) >> sum
                expected = (expected + amount) * 2 * width
            with self.subTest(case=case):
                self.assertEqual(await pipe(value), expected)
                self.assertEqual(await pipe(value), expected)


class ConstructionBoundaries(TestCase):
    def test_ensurer_rejects_variadic_keywords_like_the_checker(self) -> None:
        def stage(value: int, **options: int) -> int:
            return value

        with self.assertRaisesRegex(TypeError, "one positional data input"):
            gloe.ensure()(stage)

    def test_factories_and_adapters_preserve_input_metadata(self) -> None:
        import inspect

        @gloe.transformer
        def configured(first: int, /, second: str = "x", *, suffix: str) -> str:
            """A documented application operation."""
            return f"{first}{second}{suffix}"

        bound = configured(suffix="!")
        self.assertEqual(bound.__name__, "configured")
        self.assertEqual(bound.__doc__, "A documented application operation.")
        signature = inspect.signature(bound)
        self.assertEqual(tuple(signature.parameters), ("first", "second"))
        self.assertEqual(
            signature.parameters["first"].kind, inspect.Parameter.POSITIONAL_ONLY
        )
        self.assertEqual(signature.parameters["second"].default, "x")
        with self.assertRaises(TypeError):
            bound(1, suffix="?")
        with self.assertRaises(TypeError):
            bound(first=1)
        adapted = gloe.unpack(bound)
        self.assertEqual(tuple(inspect.signature(adapted).parameters), ("values",))
        self.assertEqual(adapted((1, "y")), "1y!")

    def test_callable_validators_keep_order_and_observe_default_data(self) -> None:
        observed: list[int] = []

        class Validator:
            def __call__(self, value: int) -> None:
                observed.append(value)

        @gloe.ensure(incoming=[Validator()], outcome=(Validator(),))
        def stage(value: int = 2) -> int:
            return value + 1

        self.assertEqual(stage(), 3)
        self.assertEqual(observed, [2, 3])
