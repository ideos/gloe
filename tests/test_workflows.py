from __future__ import annotations

import asyncio
import threading
from unittest import IsolatedAsyncioTestCase

import gloe

from .scenarios import (
    Compensation,
    Edge,
    ImportBatch,
    Indicator,
    IndicatorFunction,
    MatchedPoint,
    Meters,
    Notice,
    Query,
    Reconciliation,
    ReportSpec,
    RouteInputs,
    build_report,
    conserved,
    enabled,
    flatten,
    group_reports,
    hot,
    insert_rows,
    loaders,
    load_configs,
    mean_speeds,
    rebates,
    reconcile,
    route_inputs,
    run_indicator,
    runners,
    sales,
    split_compensation,
    transaction,
    update_invoices,
    valid_compensation,
    validate_rows,
    available,
    within_budget,
)


class ReportingAndDataWorkflows(IsolatedAsyncioTestCase):
    async def test_config_driven_reporting_builds_runners(self) -> None:
        catalog = (
            ReportSpec(2, "sales"),
            ReportSpec(1, "sales"),
            ReportSpec(2, "rebates"),
            ReportSpec(1, "disabled", False),
        )
        build = gloe.transformer(build_report)(
            registered=frozenset({"sales", "rebates"})
        )
        load = gloe.transformer(load_configs)(catalog=catalog)
        reports = (
            gloe.input() >> gloe.filter(enabled) >> gloe.map(build) >> group_reports
        )
        graph = gloe.input() >> load >> (reports, loaders) >> runners

        result = await graph([1, 2])
        self.assertEqual([runner.network for runner in result], [2, 1])
        self.assertEqual(
            [report.name for report in result[0].reports],
            ["sales", "rebates"],
        )
        self.assertEqual(result[1].loader, "loader-1")
        self.assertEqual(await graph([]), [])

    async def test_reporting_registry_errors_at_runtime_boundary(self) -> None:
        build = gloe.transformer(build_report)(registered=frozenset({"sales"}))
        pipe = gloe.input() >> gloe.map(build)
        with self.assertRaisesRegex(ValueError, "Unknown report"):
            await pipe([ReportSpec(1, "unknown")])

    async def test_generic_flatten_and_hierarchical_reconciliation_preserve_state(
        self,
    ) -> None:
        flat = gloe.input[list[list[int]]]() >> flatten >> gloe.map(str)
        self.assertEqual(await flat([[1], [], [2, 3]]), ["1", "2", "3"])

        original = Reconciliation(
            (
                Notice(1, "exact", "fallback"),
                Notice(2, "missing", "fallback"),
                Notice(3, "none", "none"),
            )
        )
        exact = gloe.transformer(reconcile)(index={"exact": 10}, exact=True)
        fallback = gloe.transformer(reconcile)(index={"fallback": 20}, exact=False)
        pipe = gloe.input() >> exact >> fallback
        result = await pipe(original)
        self.assertEqual(result.matched, ((1, 10), (2, 20)))
        self.assertEqual(tuple(item.id for item in result.unmatched), (3,))
        self.assertEqual(original.matched, ())
        self.assertEqual(await pipe(original), result)
        self.assertEqual(await pipe(Reconciliation(())), Reconciliation(()))

    async def test_compensation_split_conserves_cents_and_stops_bad_persistence(
        self,
    ) -> None:
        split = gloe.ensure(
            incoming=[valid_compensation],
            changes=[conserved],
        )(split_compensation)
        pipe = gloe.input() >> split
        for cents in (-101, -1, 0, 1, 101):
            for parts in (1, 2, 3, 10):
                with self.subTest(cents=cents, parts=parts):
                    result = await pipe(Compensation(cents, parts))
                    self.assertEqual(sum(result), cents)
                    self.assertEqual(len(result), parts)
        with self.assertRaises(ValueError):
            await pipe(Compensation(10, 0))

        persisted: list[tuple[int, ...]] = []

        def faulty(value: Compensation) -> tuple[int, ...]:
            return (value.cents // value.parts,) * value.parts

        faulty = gloe.ensure(changes=[conserved])(faulty)

        def save(value: tuple[int, ...]) -> tuple[int, ...]:
            persisted.append(value)
            return value

        with self.assertRaises(ValueError):
            await (gloe.input() >> faulty >> save)(Compensation(101, 3))
        self.assertEqual(persisted, [])

    async def test_dynamic_indicator_selection_is_homogeneous_and_ordered(self) -> None:
        registry: dict[str, IndicatorFunction] = {
            "sales": sales,
            "rebates": rebates,
        }
        selected = [registry[name] for name in ("rebates", "sales")]
        run = gloe.transformer(run_indicator)(query=Query(10))
        pipe = gloe.input() >> gloe.map(run)
        self.assertEqual(
            await pipe(selected),
            [Indicator("rebates", 5), Indicator("sales", 10)],
        )
        self.assertEqual(await pipe([]), [])
        self.assertEqual(await pipe(selected[:1]), [Indicator("rebates", 5)])

    async def test_route_preparation_keeps_network_and_filtered_hot_seeds(self) -> None:
        seeds = (
            gloe.input()
            >> gloe.filter(hot)
            >> gloe.transformer(within_budget)(limit=Meters(100))
        )
        pipe = (
            gloe.input()
            >> gloe.filter(available)
            >> (gloe.input(), seeds)
            >> route_inputs
        )
        network = [
            Edge(1, Meters(50), True),
            Edge(2, Meters(25), False),
            Edge(3, Meters(20), True, True),
            Edge(4, Meters(200), True),
        ]
        result = await pipe(network)
        self.assertEqual([edge.id for edge in result.network], [1, 2, 4])
        self.assertEqual([edge.id for edge in result.seeds], [1])
        self.assertTrue(network[2].blocked)
        self.assertEqual(await pipe([]), RouteInputs((), ()))

    async def test_speed_aggregation_and_explicit_thread_offloading(self) -> None:
        speeds = gloe.input() >> mean_speeds
        self.assertEqual(
            await speeds(
                [MatchedPoint(1, 10), MatchedPoint(1, 20), MatchedPoint(2, 40)]
            ),
            {1: 15.0, 2: 40.0},
        )
        self.assertEqual(await speeds([]), {})

        caller = threading.get_ident()

        def blocking(value: int) -> tuple[int, int]:
            return value + 1, threading.get_ident()

        result, worker = await asyncio.to_thread((gloe.input() >> blocking).sync, 2)
        self.assertEqual(result, 3)
        self.assertNotEqual(worker, caller)


class TransactionalImportWorkflows(IsolatedAsyncioTestCase):
    async def test_import_accumulates_errors_and_commits_at_context_owner(self) -> None:
        committed: list[int] = []
        events: list[str] = []
        async with transaction(committed, events) as session:
            pipe = (
                gloe.input()
                >> validate_rows
                >> gloe.transformer(insert_rows)(session=session)
                >> gloe.transformer(update_invoices)(session=session)
            )
            result = await pipe(ImportBatch((1, -2, 3), ("parse-error",)))
            self.assertEqual(
                result,
                ImportBatch((1, 3), ("parse-error", "invalid:-2"), 2),
            )
            self.assertEqual(committed, [])
        self.assertEqual(committed, [1, 3])
        self.assertEqual(events, ["begin", "insert", "update", "commit", "close"])
        self.assertTrue(session.closed)

    async def test_import_failure_rolls_back_and_closes_context(self) -> None:
        committed: list[int] = []
        events: list[str] = []
        with self.assertRaisesRegex(ValueError, "Updater failed"):
            async with transaction(committed, events) as session:
                pipe = (
                    gloe.input()
                    >> validate_rows
                    >> gloe.transformer(insert_rows)(session=session)
                    >> gloe.transformer(update_invoices)(session=session, fail=True)
                )
                await pipe(ImportBatch((1,)))
        self.assertEqual(committed, [])
        self.assertEqual(events, ["begin", "insert", "update", "rollback", "close"])

    async def test_empty_import_skips_updater_and_cancellation_rolls_back(self) -> None:
        committed: list[int] = []
        events: list[str] = []
        async with transaction(committed, events) as session:
            pipe = (
                gloe.input()
                >> validate_rows
                >> gloe.transformer(insert_rows)(session=session)
                >> gloe.transformer(update_invoices)(session=session)
            )
            self.assertEqual(
                await pipe(ImportBatch((-1,))),
                ImportBatch((), ("invalid:-1",), 0),
            )
        self.assertEqual(events, ["begin", "commit", "close"])

        committed.clear()
        events.clear()
        started = asyncio.Event()

        async def wait(batch: ImportBatch) -> ImportBatch:
            started.set()
            await asyncio.Event().wait()
            return batch

        async def run() -> None:
            async with transaction(committed, events) as session:
                await (
                    gloe.input()
                    >> gloe.transformer(insert_rows)(session=session)
                    >> wait
                )(ImportBatch((1,)))

        task = asyncio.create_task(run())
        await asyncio.wait_for(started.wait(), timeout=1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(committed, [])
        self.assertEqual(events, ["begin", "insert", "rollback", "close"])

    async def test_schema_checks_are_explicit_boundary_validators(self) -> None:
        def required_columns(rows: list[dict[str, str]]) -> None:
            if any("invoice" not in row for row in rows):
                raise ValueError("Missing invoice column")

        @gloe.ensure(incoming=[required_columns])
        def extract(rows: list[dict[str, str]]) -> list[str]:
            return [row["invoice"] for row in rows]

        pipe = gloe.input() >> extract
        self.assertEqual(await pipe([{"invoice": "a"}]), ["a"])
        with self.assertRaisesRegex(ValueError, "Missing invoice"):
            await pipe([{"other": "a"}])
