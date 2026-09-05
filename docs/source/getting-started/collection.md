# Collections

Use lowercase `map(callback)` and `filter(predicate)` factories for the
common ordered collection operations. They accept ordinary synchronous or
asynchronous callbacks and return lists:

```python
import gloe


def is_positive(value: int) -> bool:
    return value > 0


def double(value: int) -> int:
    return value * 2


positive = gloe.filter(is_positive)
twice = gloe.map(double)


pipe = gloe.input[list[int]]() >> positive >> twice
result = await pipe([-2, 0, 3])  # [2, 6]
```

The input iterable is consumed sequentially. Output order matches input order.
`filter` requires callbacks to return actual booleans; it does not treat an
arbitrary truthy value as a predicate result. A callback can be another Gloe
pipeline or a configured callable.

```python
async def keep_remote(value: int) -> bool:
    return value % 2 == 0


async_filter = gloe.filter(keep_remote)
async_pipe = gloe.input[list[int]]() >> async_filter
result = await async_pipe([1, 2, 3])  # [2]
```

## Runtime-selected operations

When an application has a homogeneous iterable of callables at runtime, use
`parallel(callables)` or `sequential(callables)`:

```python
def check_schema(value: int) -> str:
    return f"schema:{value}"


def check_policy(value: int) -> str:
    return f"policy:{value}"


checks = gloe.parallel([check_schema, check_policy])
parallel_pipe = gloe.input[int]() >> checks
parallel_result = await parallel_pipe(3)  # ["schema:3", "policy:3"]


def normalize(value: int) -> int:
    return value + 1


def enrich(value: int) -> int:
    return value + 10


ordered = gloe.sequential([normalize, enrich])
sequential_pipe = gloe.input[int]() >> ordered
sequential_result = await sequential_pipe(3)  # [4, 13]
```

Both helpers return lists in declaration order. `parallel` cancels and awaits
sibling work after a failure; `sequential` invokes each callable in order.
These helpers keep the collection homogeneous; a fixed tuple of different
branch result types belongs directly after `>>`.

## Keep specialized algorithms in Python

There is no separate operation for every list method. A typed ordinary
function is easier to read and keeps its domain rules visible:

```python
def flatten[T](groups: list[list[T]]) -> list[T]:
    return [item for group in groups for item in group]


pipe = gloe.input[list[list[int]]]() >> flatten
result = pipe.sync([[1, 2], [3]])  # [1, 2, 3]
```

See the [cookbooks](../cookbooks.md) for `reduce` and the old map-over-data
pattern.
