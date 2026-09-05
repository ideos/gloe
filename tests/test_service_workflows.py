"""Application ownership of I/O, retries, deduplication and request context."""

import asyncio
from unittest import IsolatedAsyncioTestCase

from .typing.positive_services import (
    Event,
    Receipt,
    Request,
    Response,
    User,
    endpoint,
    ingestion,
)


class RequestWorkflows(IsolatedAsyncioTestCase):
    async def test_lookup_keeps_request_context_and_blocks_unauthorized_io(
        self,
    ) -> None:
        class Directory:
            calls: list[int]

            def __init__(self) -> None:
                self.calls = []

            async def fetch(self, user_id: int) -> User | None:
                self.calls.append(user_id)
                await asyncio.sleep(0)
                return User(1, "Ada") if user_id == 1 else None

        directory = Directory()
        pipe = endpoint(directory)
        results = await asyncio.gather(
            pipe(Request(1, "test-token", "first")),
            pipe(Request(2, "test-token", "second")),
        )
        self.assertEqual(
            results,
            [Response(200, "Ada", "first"), Response(404, "Not found", "second")],
        )
        with self.assertRaises(PermissionError):
            await pipe(Request(3, "wrong", "third"))
        self.assertEqual(directory.calls, [1, 2])

    async def test_retry_and_duplicate_delivery_are_owned_by_the_ledger(self) -> None:
        class MemoryLedger:
            def __init__(self) -> None:
                self.calls = 0
                self.total = 0
                self.receipts: dict[str, Receipt] = {}

            async def apply_once(self, event: Event) -> Receipt:
                self.calls += 1
                if self.calls == 1:
                    raise ConnectionError("Transient transport failure")
                if event.id not in self.receipts:
                    self.total += event.amount
                    self.receipts[event.id] = Receipt(event.id, self.total)
                return self.receipts[event.id]

        ledger = MemoryLedger()
        pipe = ingestion(ledger)
        self.assertEqual(await pipe(Event("a", 3)), Receipt("a", 3))
        self.assertEqual(await pipe(Event("a", 3)), Receipt("a", 3))
        self.assertEqual(await pipe(Event("b", 4)), Receipt("b", 7))
        # Gloe called the stage again; the ledger, not the pipeline, deduplicated.
        self.assertEqual(ledger.calls, 4)
        self.assertEqual(ledger.total, 7)
        with self.assertRaises(ValueError):
            await pipe(Event("bad", -1))
        self.assertEqual(ledger.calls, 4)

    async def test_retry_budget_and_cancellation_are_not_hidden_by_pipeline(
        self,
    ) -> None:
        calls = 0

        class Offline:
            async def apply_once(self, event: Event) -> Receipt:
                nonlocal calls
                calls += 1
                raise ConnectionError("Offline")

        with self.assertRaises(ConnectionError):
            await ingestion(Offline())(Event("a", 1))
        self.assertEqual(calls, 2)

        class Cancelled:
            async def apply_once(self, event: Event) -> Receipt:
                nonlocal calls
                calls += 1
                raise asyncio.CancelledError()

        with self.assertRaises(asyncio.CancelledError):
            await ingestion(Cancelled())(Event("a", 1))
        self.assertEqual(calls, 3)
