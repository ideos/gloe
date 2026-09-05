from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from functools import partial
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from unittest import IsolatedAsyncioTestCase, TestCase

import gloe

from .scenarios import increment, stringify


class CorePipelineTests(IsolatedAsyncioTestCase):
    async def test_one_awaited_call_supports_sync_async_and_bound_callables(
        self,
    ) -> None:
        class Service:
            async def fetch(self, value: int) -> str:
                await asyncio.sleep(0)
                return str(value)

        pipe = gloe.input() >> increment >> Service().fetch
        self.assertEqual(await pipe(2), "3")

    async def test_construction_is_lazy_and_extension_is_immutable(self) -> None:
        calls: list[int] = []

        def record(value: int) -> int:
            calls.append(value)
            return value + 1

        original = gloe.input() >> record
        extended = original >> increment
        self.assertEqual(calls, [])
        self.assertEqual(await original(1), 2)
        self.assertEqual(await extended(1), 3)
        self.assertEqual(await original(1), 2)
        self.assertEqual(calls, [1, 1, 1])

    async def test_transformer_root_supports_zero_and_multiple_data_arguments(
        self,
    ) -> None:
        source = gloe.Transformer(lambda: 4) >> increment
        combine = (
            gloe.Transformer(
                lambda number, text, *, repeat=1: str(number) + text * repeat
            )
            >> str.upper
        )
        self.assertEqual(await source(), 5)
        self.assertEqual(await combine(2, "a", repeat=2), "2AA")

    async def test_tuple_is_one_value_and_unpack_is_explicit(self) -> None:
        branch = gloe.input() >> (
            lambda pair: pair[0] + 1,
            lambda pair: pair[1] * 2,
        )
        self.assertEqual(await branch((2, 3)), (3, 6))

        def merge(number: int, text: str, *, separator: str) -> str:
            return f"{number}{separator}{text}"

        joined = (
            gloe.input()
            >> (increment, stringify)
            >> gloe.unpack(partial(merge, separator=":"))
        )
        self.assertEqual(await joined(2), "3:2")

    async def test_explicit_fork_retains_early_data_without_shared_storage(
        self,
    ) -> None:
        seen: list[str] = []

        def prefix(value: int) -> int:
            seen.append("prefix")
            return value + 1

        def work(value: int) -> int:
            seen.append("work")
            return value * 2

        def finish(original: int, computed: int) -> tuple[int, int]:
            return original, computed

        pipe = gloe.input() >> prefix >> (gloe.input(), work) >> gloe.unpack(finish)
        self.assertEqual(await pipe(2), (3, 6))
        self.assertEqual(seen, ["prefix", "work"])

    async def test_reusing_complete_pipelines_reexecutes_shared_prefix(self) -> None:
        seen: list[str] = []

        def prefix(value: int) -> int:
            seen.append("prefix")
            return value + 1

        def work(value: int) -> int:
            seen.append("work")
            return value * 2

        def finish(value: int) -> int:
            seen.append("finish")
            return value - 1

        pipe = gloe.input() >> prefix
        pipe2 = pipe >> work
        pipe3 = pipe >> finish
        self.assertEqual(await (pipe2 >> pipe3)(2), 6)
        self.assertEqual(seen, ["prefix", "work", "prefix", "finish"])

        seen.clear()
        self.assertEqual(await (pipe >> (work, finish))(2), (6, 2))
        self.assertEqual(seen, ["prefix", "work", "finish"])

    async def test_branches_run_concurrently_and_keep_declaration_order(self) -> None:
        release = asyncio.Event()
        events: list[str] = []

        async def first(value: int) -> str:
            events.append("first-start")
            await release.wait()
            events.append("first-end")
            return "first"

        async def second(value: int) -> int:
            events.append("second-start")
            release.set()
            await asyncio.sleep(0)
            events.append("second-end")
            return value

        result = await asyncio.wait_for(
            (gloe.input() >> (first, second))(2),
            timeout=1,
        )
        self.assertEqual(result, ("first", 2))
        self.assertEqual(events[:2], ["first-start", "second-start"])
        self.assertEqual(set(events[2:]), {"first-end", "second-end"})

    async def test_branch_failure_cancels_and_awaits_siblings(self) -> None:
        started = asyncio.Event()
        cleaned: list[int] = []

        async def failing(value: int) -> int:
            started.set()
            await asyncio.sleep(0)
            raise ValueError("branch failed")

        async def waiting(value: int) -> int:
            await started.wait()
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.append(value)
            return value

        with self.assertRaisesRegex(ValueError, "branch failed"):
            await (gloe.input() >> (failing, waiting))(7)
        self.assertEqual(cleaned, [7])

    async def test_parent_cancellation_cleans_up_all_branches(self) -> None:
        started = asyncio.Event()
        active = 0
        cleaned: list[int] = []

        async def wait_forever(value: int) -> int:
            nonlocal active
            active += 1
            if active == 2:
                started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.append(value)
            return value

        task = asyncio.create_task((gloe.input() >> (wait_forever, wait_forever))(2))
        await asyncio.wait_for(started.wait(), timeout=1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(cleaned, [2, 2])

    async def test_concurrent_reuse_keeps_invocations_isolated(self) -> None:
        async def delayed(value: int) -> int:
            await asyncio.sleep((5 - value) * 0.0001)
            return value + 1

        pipe = gloe.input() >> delayed >> stringify
        self.assertEqual(
            await asyncio.gather(*(pipe(value) for value in range(12))),
            [str(value + 1) for value in range(12)],
        )

    async def test_input_awaitable_remains_data(self) -> None:
        future: asyncio.Future[int] = asyncio.get_running_loop().create_future()
        future.set_result(7)
        same = await gloe.input[Awaitable[int]]()(future)
        self.assertIs(same, future)
        self.assertEqual(await same, 7)

    async def test_nested_awaitable_result_is_awaited_once(self) -> None:
        async def nested(value: int) -> Awaitable[int]:
            async def inner() -> int:
                return value + 1

            return inner()

        inner = await (gloe.input() >> nested)(2)
        self.assertTrue(inspect.isawaitable(inner))
        self.assertEqual(await inner, 3)

    async def test_long_linear_pipeline_is_iterative(self) -> None:
        pipe = gloe.input()
        for _ in range(1500):
            pipe = pipe >> increment
        self.assertEqual(await pipe(0), 1500)

    async def test_generic_configured_stage_is_reusable_across_domains(self) -> None:
        @gloe.transformer
        def replicate[T](value: T, *, count: int) -> list[T]:
            return [value] * count

        orders = gloe.input[dict[str, str]]() >> replicate(count=2)
        names = gloe.input[str]() >> replicate(count=2)
        order = {"sku": "book"}
        self.assertEqual(await orders(order), [order, order])
        self.assertEqual(await names("pen"), ["pen", "pen"])

    async def test_stdlib_partial_and_callable_objects_compose_as_stages(self) -> None:
        def label(value: int, *, prefix: str) -> str:
            return prefix + str(value)

        class Add:
            def __init__(self, amount: int) -> None:
                self.amount = amount

            def __call__(self, value: int) -> int:
                return value + self.amount

        pipe = gloe.input[int]() >> partial(label, prefix="v")
        self.assertEqual(await pipe(2), "v2")
        self.assertEqual(await (gloe.input() >> Add(3))(2), 5)

    async def test_async_iterator_stage_is_lazy_until_an_explicit_consumer(
        self,
    ) -> None:
        visited: list[int] = []

        async def generate(limit: int) -> AsyncIterator[int]:
            for value in range(limit):
                visited.append(value)
                yield value

        async def collect(values: AsyncIterator[int]) -> list[int]:
            return [value async for value in values]

        pipe = gloe.input() >> generate >> collect
        self.assertEqual(visited, [])
        self.assertEqual(await pipe(4), [0, 1, 2, 3])
        self.assertEqual(visited, [0, 1, 2, 3])

    async def test_context_manager_owns_resource_across_async_pipeline_call(
        self,
    ) -> None:
        events: list[str] = []

        @asynccontextmanager
        async def resource() -> AsyncIterator[list[str]]:
            events.append("open")
            try:
                yield events
            finally:
                events.append("close")

        async with resource() as log:

            async def stage(value: int) -> int:
                log.append("execute")
                await asyncio.sleep(0)
                return value + 1

            self.assertEqual(await (gloe.input() >> stage)(2), 3)
        self.assertEqual(events, ["open", "execute", "close"])

    async def test_recursive_algorithm_remains_one_ordinary_stage(self) -> None:
        @dataclass(frozen=True)
        class Tree:
            value: int
            children: tuple["Tree", ...] = ()

        def total(tree: Tree) -> int:
            return tree.value + sum(total(child) for child in tree.children)

        self.assertEqual(
            await (gloe.input() >> total >> stringify)(Tree(1, (Tree(2), Tree(3)))),
            "6",
        )


class FactoryAndCollectionTests(IsolatedAsyncioTestCase):
    async def test_transformer_is_always_a_keyword_configuration_factory(self) -> None:
        @gloe.transformer
        def add(value: int, *, amount: int) -> int:
            return value + amount

        @gloe.transformer
        def increment_factory(value: int) -> int:
            return value + 1

        self.assertEqual(await (gloe.input() >> add(amount=2))(3), 5)
        self.assertEqual(await (gloe.input() >> increment_factory())(3), 4)
        self.assertEqual(inspect.signature(add(amount=2)).parameters.keys(), {"value"})

        with self.assertRaises(TypeError):
            add(amount=2, unknown=True)
        with self.assertRaises(TypeError):
            add(amount=2)(3, 4)

    async def test_configured_factory_rejects_variadic_signatures(self) -> None:
        with self.assertRaisesRegex(TypeError, "explicit"):

            @gloe.transformer
            def invalid(value: int, *extra: int) -> int:
                return value + sum(extra)

        def ordinary(value: int, *extra: int) -> int:
            return value + sum(extra)

        self.assertEqual(await (gloe.input() >> ordinary)(3), 3)

    async def test_map_filter_are_ordered_sequential_and_accept_pipelines(self) -> None:
        active = 0
        maximum = 0

        async def checked(value: int) -> int:
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0)
            active -= 1
            return value + 1

        map_pipe = gloe.input() >> gloe.map(checked) >> gloe.map(stringify)
        self.assertEqual(await map_pipe([1, 2, 3]), ["2", "3", "4"])
        self.assertEqual(maximum, 1)
        self.assertEqual(await map_pipe([]), [])

        keep = gloe.input() >> increment
        nested = gloe.input() >> gloe.map(keep)
        self.assertEqual(await nested([1, 2]), [2, 3])

        with self.assertRaisesRegex(TypeError, "bool"):
            await (gloe.input() >> gloe.filter(lambda value: 1))([1])

    async def test_condition_invokes_exactly_one_selected_branch(self) -> None:
        events: list[str] = []

        def when_true(value: int) -> int:
            events.append("then")
            return value + 1

        async def when_false(value: int) -> str:
            events.append("otherwise")
            return str(value)

        pipe = gloe.input() >> gloe.condition(
            lambda value: value > 0,
            then=when_true,
            otherwise=when_false,
        )
        self.assertEqual(await pipe(2), 3)
        self.assertEqual(events, ["then"])
        self.assertEqual(await pipe(-2), "-2")
        self.assertEqual(events, ["then", "otherwise"])

    async def test_dynamic_parallel_and_sequential_return_lists(self) -> None:
        events: list[str] = []

        async def slow(value: int) -> int:
            events.append("slow-start")
            await asyncio.sleep(0)
            events.append("slow-end")
            return value + 1

        def fast(value: int) -> int:
            events.append("fast")
            return value + 2

        parallel = gloe.input() >> gloe.parallel((slow, fast))
        self.assertEqual(await parallel(3), [4, 5])
        self.assertEqual(events[:2], ["slow-start", "fast"])

        events.clear()
        sequential = gloe.input() >> gloe.sequential((slow, fast))
        self.assertEqual(await sequential(3), [4, 5])
        self.assertEqual(events, ["slow-start", "slow-end", "fast"])
        self.assertEqual(await (gloe.input() >> gloe.parallel(()))(3), [])

    async def test_removed_map_over_and_reduce_are_explicit_configured_helpers(
        self,
    ) -> None:
        def quote(value: tuple[int, str]) -> str:
            amount, sku = value
            return f"{sku}:{amount}"

        async def count(value: tuple[int, str]) -> int:
            total, word = value
            await asyncio.sleep(0)
            return total + len(word)

        @gloe.transformer
        async def map_over(
            value: int,
            *,
            items: tuple[str, ...],
            using: Callable[[tuple[int, str]], Awaitable[str]],
        ) -> list[str]:
            return [await using((value, item)) for item in items]

        @gloe.transformer
        async def reduce_values(
            values: list[str],
            *,
            using: Callable[[tuple[int, str]], Awaitable[int]],
            initial: int,
        ) -> int:
            result = initial
            for value in values:
                result = await using((result, value))
            return result

        quote_pipe = gloe.input() >> quote
        catalog = gloe.input() >> map_over(items=("book", "pen"), using=quote_pipe)
        self.assertEqual(await catalog(2), ["book:2", "pen:2"])

        reducer = gloe.input() >> reduce_values(using=gloe.input() >> count, initial=0)
        self.assertEqual(await reducer(["abc", "de"]), 5)
        self.assertEqual(await reducer([]), 0)

    async def test_composition_rejects_noncallable_nodes_and_branches(self) -> None:
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.input() >> object()
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.input() >> (increment, object())
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.map(object())
        with self.assertRaisesRegex(TypeError, "callable"):
            gloe.filter(object())


class ValidationTests(IsolatedAsyncioTestCase):
    async def test_ensure_runs_incoming_outcome_and_changes_in_order(self) -> None:
        events: list[str] = []

        def incoming(value: int) -> None:
            events.append(f"in:{value}")

        def outcome(value: int) -> None:
            events.append(f"out:{value}")

        def changes(before: int, after: int) -> None:
            events.append(f"change:{before}:{after}")

        @gloe.ensure(
            incoming=(incoming,),
            outcome=[outcome],
            changes=changes,
        )
        def add(value: int) -> int:
            events.append("stage")
            return value + 1

        self.assertEqual(await (gloe.input() >> add)(2), 3)
        self.assertEqual(
            events,
            ["in:2", "stage", "out:3", "change:2:3"],
        )

    async def test_ensure_can_wrap_a_configured_factory(self) -> None:
        def nonnegative(value: int) -> None:
            if value < 0:
                raise ValueError("negative")

        def increased(before: int, after: int) -> None:
            if after <= before:
                raise ValueError("did not increase")

        @gloe.transformer
        @gloe.ensure(incoming=[nonnegative], changes=[increased])
        def add(value: int, *, amount: int) -> int:
            return value + amount

        self.assertEqual(await (gloe.input() >> add(amount=2))(1), 3)
        with self.assertRaisesRegex(ValueError, "did not increase"):
            await (gloe.input() >> add(amount=0))(1)

    async def test_failed_incoming_validation_prevents_stage_and_downstream(
        self,
    ) -> None:
        events: list[str] = []

        def rejected(value: int) -> None:
            raise ValueError("input rejected")

        @gloe.ensure(incoming=rejected)
        def stage(value: int) -> int:
            events.append("stage")
            return value

        def save(value: int) -> int:
            events.append("save")
            return value

        with self.assertRaisesRegex(ValueError, "input rejected"):
            await (gloe.input() >> stage >> save)(2)
        self.assertEqual(events, [])

    async def test_failed_outcome_validation_prevents_downstream(self) -> None:
        events: list[str] = []

        def nonnegative(value: int) -> None:
            if value < 0:
                raise ValueError("negative")

        @gloe.ensure(outcome=[nonnegative])
        def stage(value: int) -> int:
            events.append("stage")
            return -value

        def save(value: int) -> int:
            events.append("save")
            return value

        with self.assertRaisesRegex(ValueError, "negative"):
            await (gloe.input() >> stage >> save)(1)
        self.assertEqual(events, ["stage"])

    async def test_async_ensure_keeps_before_values_invocation_local(self) -> None:
        def unchanged(before: int, after: int) -> None:
            if after != before + 1:
                raise ValueError("unexpected change")

        @gloe.ensure(changes=(unchanged,))
        async def add(value: int) -> int:
            await asyncio.sleep(0)
            return value + 1

        pipe = gloe.input() >> add
        self.assertEqual(
            await asyncio.gather(*(pipe(value) for value in range(20))),
            list(range(1, 21)),
        )

    async def test_sync_ensure_wrapper_can_return_an_awaitable(self) -> None:
        def increased(before: int, after: int) -> None:
            if after != before + 1:
                raise ValueError("unexpected result")

        @gloe.ensure(changes=increased)
        def add(value: int) -> Awaitable[int]:
            async def finish() -> int:
                await asyncio.sleep(0)
                return value + 1

            return finish()

        self.assertEqual(await (gloe.input() >> add)(2), 3)

    async def test_mutation_is_reference_based_until_caller_takes_a_snapshot(
        self,
    ) -> None:
        @dataclass
        class Box:
            value: int

        seen: list[tuple[bool, int, int]] = []

        def changes(before: Box, after: Box) -> None:
            seen.append((before is after, before.value, after.value))

        @gloe.ensure(changes=changes)
        def mutate(box: Box) -> Box:
            box.value += 1
            return box

        box = Box(1)
        self.assertIs(await (gloe.input() >> mutate)(box), box)
        self.assertEqual(seen, [(True, 2, 2)])

    async def test_validator_return_must_be_none_and_unary_data_is_required(
        self,
    ) -> None:
        @gloe.ensure(incoming=lambda value: False)
        def stage(value: int) -> int:
            return value

        with self.assertRaisesRegex(TypeError, "None"):
            await (gloe.input() >> stage)(1)

        with self.assertRaises(TypeError):
            gloe.ensure(incoming=lambda value: None)(lambda left, right: left + right)


class BlockingEntryTests(TestCase):
    def test_sync_executes_async_stages_outside_running_loop(self) -> None:
        async def add(value: int) -> int:
            await asyncio.sleep(0)
            return value + 1

        self.assertEqual((gloe.input() >> add).sync(2), 3)

    def test_sync_is_rejected_inside_a_running_loop(self) -> None:
        async def run() -> None:
            with self.assertRaisesRegex(RuntimeError, "await pipe"):
                (gloe.input() >> increment).sync(2)

        asyncio.run(run())
