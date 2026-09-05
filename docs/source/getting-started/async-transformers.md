# Synchronous and asynchronous stages

Native `async def` functions are ordinary stages. There is no separate
decorator, pipeline class, or collection variant for asynchronous code:

```python
import gloe


def parse(raw: str) -> int:
    return int(raw)


async def lookup(value: int) -> str:
    return f"item-{value}"


pipe = gloe.input() >> parse >> lookup
item = await pipe("7")  # "item-7"
```

The pipeline call is always awaitable, even when every stage is synchronous.
Gloe awaits one callable result layer at the boundary. A nested awaitable that
the callable intentionally returns remains data.

## Synchronous entry points

Use `.sync(...)` from synchronous application code:

```python
result = pipe.sync("7")  # "item-7"
```

`.sync(...)` blocks while driving the same execution path and raises when
called from a running event loop. A synchronous stage runs on the caller's
thread. If blocking work must leave an async event loop, make that boundary
explicit with the application's executor or `asyncio.to_thread`.

## Branches

Static tuple branches run concurrently and return in declaration order. Mixed
sync/async branches use the same rule:

```python
def local_score(value: int) -> int:
    return value * 2


async def remote_score(value: int) -> int:
    return value + 1


scores = gloe.input[int]() >> (local_score, remote_score)
result = await scores(3)  # (6, 4)
```

If a branch fails or is cancelled, Gloe cancels and awaits outstanding sibling
branches. It does not offload synchronous branches automatically.
