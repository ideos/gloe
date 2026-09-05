"""Small, dependency-free workflow records used by the runtime test suite.

These are synthetic consumer-shaped operations.  They deliberately keep
sessions, registries, and transaction ownership in ordinary Python so the
tests exercise Gloe's composition contract without requiring an application
database or network service.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from typing import NewType


@dataclass(frozen=True)
class Order:
    sku: str
    units: int
    unit_price_cents: int


@dataclass(frozen=True)
class Receipt:
    sku: str
    total_cents: int


def charge(order: Order, *, discount_cents: int = 0) -> Receipt:
    if order.units < 1:
        raise ValueError("Order must contain at least one unit")
    return Receipt(
        order.sku, max(0, order.units * order.unit_price_cents - discount_cents)
    )


async def render(receipt: Receipt, *, prefix: str) -> str:
    await asyncio.sleep(0)
    return f"{prefix}:{receipt.sku}:{receipt.total_cents}"


def increment(value: int) -> int:
    return value + 1


async def stringify(value: int) -> str:
    await asyncio.sleep(0)
    return str(value)


def positive(value: int) -> bool:
    return value > 0


async def even(value: int) -> bool:
    await asyncio.sleep(0)
    return value % 2 == 0


def replicate[T](value: T, *, count: int) -> list[T]:
    return [value] * count


@dataclass(frozen=True)
class Document:
    name: str
    body: str


@dataclass(frozen=True)
class Analysis:
    original: Document
    words: tuple[str, ...]


def document_body(value: Document) -> str:
    return value.body


def tokenize(value: str) -> tuple[str, ...]:
    return tuple(value.lower().split())


def assemble(original: Document, words: tuple[str, ...]) -> Analysis:
    return Analysis(original, words)


@dataclass(frozen=True)
class ReportSpec:
    network: int
    name: str
    enabled: bool = True


@dataclass(frozen=True)
class Report:
    network: int
    name: str


@dataclass(frozen=True)
class Runner:
    network: int
    reports: tuple[Report, ...]
    loader: str


def load_configs(
    ids: list[int], *, catalog: tuple[ReportSpec, ...]
) -> list[ReportSpec]:
    return [spec for spec in catalog if spec.network in ids]


def enabled(spec: ReportSpec) -> bool:
    return spec.enabled


def build_report(spec: ReportSpec, *, registered: frozenset[str]) -> Report:
    if spec.name not in registered:
        raise ValueError("Unknown report factory")
    return Report(spec.network, spec.name)


def group_reports(reports: list[Report]) -> dict[int, tuple[Report, ...]]:
    groups: dict[int, tuple[Report, ...]] = {}
    for report in reports:
        groups[report.network] = (*groups.get(report.network, ()), report)
    return groups


def loaders(specs: list[ReportSpec]) -> dict[int, str]:
    return {spec.network: f"loader-{spec.network}" for spec in specs}


def runners(
    parts: tuple[dict[int, tuple[Report, ...]], dict[int, str]],
) -> list[Runner]:
    reports, available = parts
    return [
        Runner(network, group, available[network]) for network, group in reports.items()
    ]


def flatten[T](groups: Iterable[Iterable[T]]) -> list[T]:
    return [item for group in groups for item in group]


@dataclass(frozen=True)
class Notice:
    id: int
    exact: str
    fallback: str


@dataclass(frozen=True)
class Reconciliation:
    unmatched: tuple[Notice, ...]
    matched: tuple[tuple[int, int], ...] = ()


def reconcile(
    state: Reconciliation,
    *,
    index: Mapping[str, int],
    exact: bool,
) -> Reconciliation:
    matches = list(state.matched)
    unmatched: list[Notice] = []
    for notice in state.unmatched:
        invoice = index.get(notice.exact if exact else notice.fallback)
        if invoice is None:
            unmatched.append(notice)
        else:
            matches.append((notice.id, invoice))
    return Reconciliation(tuple(unmatched), tuple(matches))


@dataclass(frozen=True)
class Compensation:
    cents: int
    parts: int


def valid_compensation(value: Compensation) -> None:
    if value.parts <= 0:
        raise ValueError("Parts must be positive")


def conserved(before: Compensation, after: tuple[int, ...]) -> None:
    if sum(after) != before.cents:
        raise ValueError("Value was not conserved")


def split_compensation(value: Compensation) -> tuple[int, ...]:
    sign = -1 if value.cents < 0 else 1
    quotient, remainder = divmod(abs(value.cents), value.parts)
    return (sign * (quotient + remainder),) + (sign * quotient,) * (value.parts - 1)


@dataclass(frozen=True)
class Query:
    amount: int


@dataclass(frozen=True)
class Indicator:
    name: str
    value: int


IndicatorFunction = Callable[[Query], Awaitable[Indicator]]


async def run_indicator(function: IndicatorFunction, *, query: Query) -> Indicator:
    return await function(query)


async def sales(query: Query) -> Indicator:
    await asyncio.sleep(0)
    return Indicator("sales", query.amount)


async def rebates(query: Query) -> Indicator:
    await asyncio.sleep(0)
    return Indicator("rebates", query.amount // 2)


Meters = NewType("Meters", int)
Kilometers = NewType("Kilometers", int)


@dataclass(frozen=True)
class Edge:
    id: int
    length: Meters
    hot: bool
    blocked: bool = False


def available(edge: Edge) -> bool:
    return not edge.blocked


def hot(edge: Edge) -> bool:
    return edge.hot


def within_budget(edges: list[Edge], *, limit: Meters) -> list[Edge]:
    return [edge for edge in edges if edge.length <= limit]


@dataclass(frozen=True)
class RouteInputs:
    network: tuple[Edge, ...]
    seeds: tuple[Edge, ...]


def route_inputs(parts: tuple[list[Edge], list[Edge]]) -> RouteInputs:
    return RouteInputs(tuple(parts[0]), tuple(parts[1]))


@dataclass(frozen=True)
class MatchedPoint:
    edge_id: int
    speed: float


def mean_speeds(points: list[MatchedPoint]) -> dict[int, float]:
    grouped: dict[int, list[float]] = {}
    for point in points:
        grouped.setdefault(point.edge_id, []).append(point.speed)
    return {edge: sum(speeds) / len(speeds) for edge, speeds in grouped.items()}


@dataclass(frozen=True)
class ImportBatch:
    rows: tuple[int, ...]
    errors: tuple[str, ...] = ()
    inserted: int = 0


@dataclass
class Session:
    pending: list[int]
    events: list[str]
    closed: bool = False


@asynccontextmanager
async def transaction(
    committed: list[int], events: list[str]
) -> AsyncIterator[Session]:
    session = Session([], events)
    events.append("begin")
    try:
        yield session
    except BaseException:
        events.append("rollback")
        raise
    else:
        committed.extend(session.pending)
        events.append("commit")
    finally:
        session.closed = True
        events.append("close")


def validate_rows(batch: ImportBatch) -> ImportBatch:
    return replace(
        batch,
        rows=tuple(row for row in batch.rows if row > 0),
        errors=batch.errors + tuple(f"invalid:{row}" for row in batch.rows if row <= 0),
    )


async def insert_rows(batch: ImportBatch, *, session: Session) -> ImportBatch:
    if session.closed:
        raise RuntimeError("Session is closed")
    if batch.rows:
        session.pending.extend(batch.rows)
        session.events.append("insert")
    return replace(batch, inserted=len(batch.rows))


async def update_invoices(
    batch: ImportBatch,
    *,
    session: Session,
    fail: bool = False,
) -> ImportBatch:
    if batch.inserted:
        session.events.append("update")
        if fail:
            raise ValueError("Updater failed")
    return batch
