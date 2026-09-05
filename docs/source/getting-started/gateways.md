# Branching and dynamic collections

The tuple form after `>>` is the compact way to express a fixed set of
heterogeneous branches:

```python
import gloe


def extract_name(value: int) -> str:
    return f"user-{value}"


async def load_orders(value: int) -> list[int]:
    return [value * 10]


inspect = gloe.input[int]() >> (extract_name, load_orders)
result = await inspect(7)  # ("user-7", [70])
```

Both branches receive the same integer. They run concurrently and produce an
ordered tuple `(str, list[int])`. A failure cancels and awaits outstanding
sibling branches. The graph retains every occurrence; there is no implicit
cache or deduplication.

## Dynamic homogeneous branches

Use `parallel(callables)` when the application supplies a runtime iterable of
independent callables with one common input/output contract:

```python
def check_schema(value: int) -> str:
    return f"schema:{value}"


def check_policy(value: int) -> str:
    return f"policy:{value}"


def check_limits(value: int) -> str:
    return f"limits:{value}"


checks = gloe.parallel([check_schema, check_policy, check_limits])
pipe = gloe.input[int]() >> checks
result = await pipe(3)  # ["schema:3", "policy:3", "limits:3"]
```

Use `sequential(callables)` when the application needs a runtime collection of
callables invoked in declaration order with the shared input:

```python
checks = gloe.sequential([check_schema, check_policy, check_limits])
pipe = gloe.input[int]() >> checks
result = await pipe(3)  # ["schema:3", "policy:3", "limits:3"]
```

The dynamic helpers are ordered at the result boundary. Use a tuple when the
branch result types differ and need an exact tuple type.
