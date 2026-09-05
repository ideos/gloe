# Function cookbooks

Use an ordinary typed function when the operation is an algorithm, loop, or
domain policy. Compose that function with Gloe instead of adding a new operator
for each list shape.

## Reduce

Keep the accumulator policy in a normal function. The reducer receives explicit
arguments; there is no special high-order pipeline class:

```python
import gloe
from collections.abc import Callable, Iterable


def reduce_values[T, S](
    values: Iterable[T],
    reducer: Callable[[S, T], S],
    initial: S,
) -> S:
    result = initial
    for value in values:
        result = reducer(result, value)
    return result


def add(total: int, value: int) -> int:
    return total + value


def sum_values(values: list[int]) -> int:
    return reduce_values(values, add, 0)


pipeline = gloe.input() >> sum_values
result = pipeline.sync([1, 2, 3, 4])  # 10
```

For a reusable configured reducer, use a normal factory or `@gloe.transformer`
with keyword-only configuration. Keep the accumulator type visible in the
function signature so the checker can validate it.

## Map over configured data

`MapOver` paired the same flowing input with every configured item. Preserve
that behavior with an ordinary configured function:

```python
import gloe
from collections.abc import Callable


@gloe.transformer
def map_over[T, U, R](
    value: T,
    *,
    items: tuple[U, ...],
    combine: Callable[[T, U], R],
) -> list[R]:
    return [combine(value, item) for item in items]


def multiply(value: int, factor: int) -> int:
    return value * factor


pipeline = gloe.input() >> map_over(items=(2, 3, 4), combine=multiply)
result = pipeline.sync(5)  # [10, 15, 20]
```

This function defines a synchronous loop. For asynchronous domain work, use an
`async def` function and await the operation inside its loop; the surrounding
pipeline pattern stays the same. For two flowing collections, write an ordinary
function that calls `zip`, choosing its length-mismatch policy explicitly.

## Explicit data retention

When later work needs both the original value and derived data, branch
explicitly and join a named record or tuple:

```python
import gloe


def tokenize(document: str) -> tuple[str, ...]:
    return tuple(document.split())


def build_report(original: str, tokens: tuple[str, ...]) -> str:
    return f"{original!r}: {len(tokens)} tokens"


prefix = gloe.input[str]()
pipeline = prefix >> (gloe.input(), tokenize) >> gloe.unpack(build_report)
result = pipeline.sync("hello world")  # "'hello world': 2 tokens"
```

The identity branch retains a reference. Use immutable domain records or an
explicit snapshot when mutation must be compared with a before value.

## Dynamic report selection

For a runtime registry of homogeneous report callables, keep the registry and
selection in ordinary application code and use `map` for ordered execution:

```python
import gloe
from collections.abc import Awaitable, Callable


ReportFunction = Callable[[int], Awaitable[int]]


async def sales(query: int) -> int:
    return query


async def rebates(query: int) -> int:
    return query // 2


@gloe.transformer
async def run_report(function: ReportFunction, *, query: int) -> int:
    return await function(query)


selected: list[ReportFunction] = [rebates, sales]
run_selected = gloe.input[list[ReportFunction]]() >> gloe.map(
    run_report(query=10)
)
result = await run_selected(selected)  # [5, 10]
```

This is the shape exercised by the Partech consumer scenarios. Database names,
registry contents, and query ownership remain runtime boundaries. The research
used synthetic fixtures; it did not run a production integration.

## Keep transactions outside the pipeline

An application owns the transaction and passes its session through explicit
configuration:

```python
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass

import gloe


@dataclass(frozen=True)
class ImportBatch:
    rows: tuple[int, ...]


@dataclass
class Session:
    inserted: list[int]


@asynccontextmanager
async def transaction():
    yield Session([])


def validate_rows(batch: ImportBatch) -> ImportBatch:
    if any(row < 0 for row in batch.rows):
        raise ValueError("rows must be nonnegative")
    return batch


def insert_rows(*, session: Session):
    def insert(batch: ImportBatch) -> ImportBatch:
        session.inserted.extend(batch.rows)
        return batch

    return insert


def update_invoices(*, session: Session):
    def update(batch: ImportBatch) -> ImportBatch:
        # The real function updates invoice records in the session.
        return batch

    return update


async def run_import(batch: ImportBatch) -> tuple[ImportBatch, tuple[int, ...]]:
    """Keep transaction ownership in application code."""

    async with transaction() as session:
        import_rows = (
            gloe.input[ImportBatch]()
            >> validate_rows
            >> insert_rows(session=session)
            >> update_invoices(session=session)
        )
        result = await import_rows(batch)
        return result, tuple(session.inserted)


result = asyncio.run(run_import(ImportBatch((101, 102))))
# ImportBatch(rows=(101, 102)), (101, 102)
assert result == (ImportBatch(rows=(101, 102)), (101, 102))
```

Gloe does not infer commit, rollback, retries, or resource ownership.

## Geo Routes as a candidate shape

One researched route endpoint can be expressed as a possible data-flow shape:

```python
from dataclasses import dataclass
from collections.abc import Callable

import gloe


@dataclass(frozen=True)
class Segment:
    name: str
    hot: bool
    available: bool
    meters: int


def is_hot(segment: Segment) -> bool:
    return segment.hot


def is_available(segment: Segment) -> bool:
    return segment.available


def within_budget(*, limit: int) -> Callable[[Segment], bool]:
    return lambda segment: segment.meters <= limit


def build_route_inputs(
    branches: tuple[list[Segment], list[Segment]],
) -> tuple[list[Segment], list[Segment]]:
    return branches


seeds = (
    gloe.input[list[Segment]]()
    >> gloe.filter(is_hot)
    >> within_budget(limit=100)
)

prepare = (
    gloe.input[list[Segment]]()
    >> gloe.filter(is_available)
    >> (gloe.input(), seeds)
    >> build_route_inputs
)


segments = [
    Segment("a", hot=False, available=True, meters=50),
    Segment("b", hot=True, available=True, meters=150),
    Segment("c", hot=True, available=True, meters=80),
    Segment("d", hot=True, available=False, meters=120),
]
result = prepare.sync(segments)
assert result == (segments[:3], [segments[2]])
```

Geo Routes was inspected as a candidate consumer, not as a current Gloe user.
The example does not validate route connectivity, coordinate systems, map
matching, or real integration behavior.
