# Consumer-shaped scenarios

The repository research inspected the Partech engines, where Gloe 0.7 is an
actual dependency, and used small synthetic scenarios to exercise the 0.8
surface. It also inspected Geo Routes as a candidate use case. These examples
do not claim production integration tests.

## Report builders

Load report specifications as ordinary records, then keep selection and report
construction in a typed pipeline:

```python
import gloe
from dataclasses import dataclass


@dataclass(frozen=True)
class ReportSpec:
    network: int
    name: str
    enabled: bool = True


def is_enabled(spec: ReportSpec) -> bool:
    return spec.enabled


def build_report(spec: ReportSpec) -> str:
    return f"{spec.network}:{spec.name}"


def group_reports(reports: list[str]) -> tuple[str, ...]:
    return tuple(reports)


reports = (
    gloe.input[list[ReportSpec]]()
    >> gloe.filter(is_enabled)
    >> gloe.map(build_report)
    >> group_reports
)
result = reports.sync(
    [ReportSpec(2, "sales"), ReportSpec(1, "disabled", False), ReportSpec(1, "rebates")]
)  # ("2:sales", "1:rebates")
```

Database names and registry contents remain runtime boundaries. Use named
records when a later stage needs more than one value.

## Ordered reconciliation

Sequential stages can carry a named record containing matched and remaining
items. The second stage sees only the output of the first:

```python
import gloe
from dataclasses import dataclass


@dataclass(frozen=True)
class Reconciliation:
    matched: tuple[int, ...]
    remaining: tuple[int, ...]


def exact(value: Reconciliation) -> Reconciliation:
    matched = value.matched + tuple(item for item in value.remaining if item % 2 == 0)
    remaining = tuple(item for item in value.remaining if item % 2 != 0)
    return Reconciliation(matched, remaining)


def fallback(value: Reconciliation) -> Reconciliation:
    matched = value.matched + value.remaining[:1]
    return Reconciliation(matched, value.remaining[1:])


reconciliation = gloe.input[Reconciliation]() >> exact >> fallback
result = reconciliation.sync(Reconciliation((), (1, 2, 3)))
assert result == Reconciliation((2, 1), (3,))
```

Gloe does not create hidden context slots for previously matched values.

## Explicit validation

Keep business invariants in `ensure` validators around the function that owns
the transformation:

```python
import gloe


def nonnegative(value: int) -> None:
    if value < 0:
        raise ValueError("negative")


def increased(before: int, after: int) -> None:
    if after <= before:
        raise ValueError("did not increase")


@gloe.ensure(incoming=nonnegative, changes=increased)
def increment(value: int) -> int:
    return value + 1


validated = gloe.input[int]() >> increment
result = validated.sync(2)  # 3
```

Use fresh results or an explicit snapshot when conservation compares before and
after values. An identity branch is only a reference.

## Runtime-selected reports

When selected report functions share a homogeneous contract, use an ordered
map:

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

Use a static tuple for a fixed set of heterogeneous branches. Use
`parallel(callables)` only when the runtime collection is homogeneous and its
failure/resource policy is explicit.
