# Migrating from 0.7 to 0.8

Gloe 0.8 consolidates the runtime around one `Transformer[P, R]` model and one
awaitable invocation boundary. Treat this as a source migration: the old
decorator and helper variants are not parallel 0.8 APIs.

| 0.7 code | 0.8 code | Migration note |
| --- | --- | --- |
| `transformer` around every stage | ordinary typed function | Use no decorator for an unconfigured stage. |
| `@transformer` with configuration | `@gloe.transformer` plus keyword-only configuration | `add(amount=2)` returns an ordinary callable. |
| `@transformer` with no configuration | plain function, or `stage()` | The decorator is always a factory; call it before `>>`. |
| `async_transformer` / async transformer classes | native `async def` function | Native async and sync stages share the same pipeline model. |
| `partial_transformer` variants | ordinary Python factory or configured transformer | Keep configuration in a normal callable. |
| `pipeline(value)` | `await pipeline(value)` | Every call is awaitable. |
| synchronous call from sync code | `pipeline.sync(value)` | `.sync` blocks and rejects a running event loop. |
| implicit first-stage forwarding | `gloe.input() >> stage` | Use `gloe.input[T]()` when inference is ambiguous. |
| implicit tuple spreading | `gloe.unpack(function)` | A tuple remains one value until the adapter is explicit. |
| `Map` / `MapAsync` | `gloe.map(callback)` | One ordered factory accepts sync and async callbacks. |
| `Filter` / `FilterAsync` | `gloe.filter(predicate)` | Predicates return actual `bool`; output order is preserved. |
| `MapOver` / `MapOverAsync` | a configured function that pairs one input with each configured item | See the map-over cookbook. |
| gateway class variants | `gloe.parallel(...)` / `gloe.sequential(...)` | Dynamic collections are homogeneous. Static tuples are direct branches. |
| `If` and conditional variants | `gloe.condition(predicate, then=..., otherwise=...)` | Exactly one branch is selected. |
| bridge context or application-specific pick/forward helpers | identity branch plus a typed join | See the explicit-data cookbook. |
| `.to_agraph()` | `.graph().to_dot()` or `pipeline.to_dot(path)` | Graph projection never runs business functions. |
| image export through a graph helper | `pipeline.to_image(path)` | Install the optional plotting dependency. |

## Input and configuration

The input anchor is usually inferred:

```python
import gloe


def parse(raw: str) -> int:
    return int(raw)


def normalize(value: int) -> int:
    return value * 2


pipe = gloe.input() >> parse >> normalize
result = pipe.sync("7")  # 14
```

If the first stage is generic or overloaded, provide the anchor:

```python
def decode(value: bytes) -> str:
    return value.decode("ascii")


pipe = gloe.input[bytes]() >> decode
result = pipe.sync(b"ok")  # "ok"
```

The configured decorator convention is keyword-only:

```python
@gloe.transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


pipe = gloe.input() >> add(amount=2)
result = pipe.sync(3)  # 5
```

Positional parameters belong to the flowing data call. Keyword-only parameters
are bound configuration and are excluded from the configured callable's data
contract.

## Typing setup

Install the tested checker extra and opt in explicitly:

```shell
pip install 'gloe[types]'
```

```toml
[tool.mypy]
plugins = ["gloe.mypy_plugin"]
```

The extra pins mypy 2.3.1. Installation does not edit `pyproject.toml`,
`mypy.ini`, or another checker configuration. Other checkers do not run the
verified composition plugin.
