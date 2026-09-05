<div align="center" style="margin-top: 2rem;">
  <img src="https://gloe.ideos.com.br/_static/assets/gloe-logo.png" alt="Gloe"><br>
</div>

<div align="center">
<a href="https://github.com/ideos/gloe/actions/workflows/test.yml">
  <img src="https://github.com/ideos/gloe/actions/workflows/test.yml/badge.svg" alt="CI - Test">
</a>
<a href="https://pypi.org/project/gloe">
  <img src="https://img.shields.io/pypi/v/gloe.svg?color=%2334D058" alt="PyPI Latest Release">
</a>
<a href="https://www.python.org/">
  <img src="https://img.shields.io/pypi/pyversions/gloe.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://www.apache.org/licenses/LICENSE-2.0">
  <img src="https://img.shields.io/pypi/l/gloe.svg?color=%2304b367" alt="License - Apache 2.0">
</a>
</div>

Gloe is a small, typed language for building inspectable Python pipelines. A
pipeline is an immutable sequence of ordinary callables and branches. Gloe
connects those functions, checks their declared edges with its bundled mypy
plugin, executes synchronous and asynchronous callables through one invocation
boundary, and exposes the resulting graph.

Read the [documentation](https://gloe.ideos.com.br) or the
[source code](https://github.com/ideos/gloe).

## Install

Gloe supports Python 3.12, 3.13, and 3.14.

```shell
pip install gloe
```

Install the optional typing tools when the project uses composition checks:

```shell
pip install 'gloe[types]'
```

The extra pins mypy 2.3.1, the tested checker release. Installation does
not change a project's checker configuration. Enable the bundled plugin
explicitly:

```toml
[tool.mypy]
plugins = ["gloe.mypy_plugin"]
```

Other checkers can check the ordinary functions in a pipeline, but Gloe's
verified composition contract is provided by this mypy plugin.

## The canonical pipeline

Use an ordinary typed function for a stage. Use `@gloe.transformer` only when a
function has keyword-only configuration that should be bound before the
pipeline runs. The decorator always returns a configuration factory:

```python
import gloe


@gloe.transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


def as_text(value: int) -> str:
    return str(value)


pipe = gloe.input() >> add(amount=2) >> as_text
result = pipe.sync(3)  # "5"
```

`gloe.input()` infers the concrete input from the first stage. If the entry
point is generic or ambiguous, anchor it explicitly:

```python
explicit = gloe.input[int]() >> add(amount=2) >> as_text
result = explicit.sync(3)  # "5"
```

Pipeline construction does not execute a stage. Calling a pipeline is always
awaitable, including when every stage is synchronous:

```python
result = await pipe(3)  # "5", from an async entry point
```

Synchronous code can use the same execution path through `.sync(...)`:

```python
result = pipe.sync(3)  # "5"
```

`.sync(...)` blocks and rejects calls made from an already running event loop.
Synchronous stages run on the caller's thread; use an explicit executor or
`asyncio.to_thread` when that boundary is required.

For a function with no configuration, prefer a plain function. If the
decorator is useful for a uniform public factory, call the no-configuration
factory before composing it:

```python
@gloe.transformer
def normalize(value: str) -> str:
    return value.strip().lower()


pipe = gloe.input[str]() >> normalize()
result = pipe.sync(" Hello ")  # "hello"
```

## Branches and data flow

A tuple after `>>` is a static fan-out. Each branch receives the same value,
runs concurrently, and returns a tuple in declaration order:

```python
def word_count(value: str) -> int:
    return len(value.split())


async def fetch_score(value: str) -> float:
    return len(value) / 2


analysis = gloe.input[str]() >> (word_count, fetch_score)
result = await analysis("hello world")  # (2, 5.5)
```

Failures cancel and await outstanding sibling branches. Synchronous work is not
silently moved to a worker. A pipeline has no implicit cache or deduplication:
composing `pipe2 >> pipe3` executes both complete sequences. Share a prefix
explicitly when the data flow should fork:

```python
prefix = gloe.input[str]() >> normalize()
pipeline = prefix >> (word_count, fetch_score)
result = await pipeline("Hello")  # (1, 2.5)
```

Tuples remain one value. To call a function with positional arguments from a
tuple, make that adaptation explicit:

```python
def finish(count: int, score: float) -> str:
    return f"{count}:{score:.2f}"


pipeline = analysis >> gloe.unpack(finish)
result = await pipeline("hello world")  # "2:5.50"
```

To retain an earlier value, use an identity branch and a typed join. The
identity branch keeps a reference; it is not a deep copy or a snapshot:

```python
def tokenize(document: str) -> tuple[str, ...]:
    return tuple(document.split())


def finish(original: str, tokens: tuple[str, ...]) -> str:
    return f"{original!r}: {len(tokens)} tokens"


retained = prefix >> (gloe.input(), tokenize) >> gloe.unpack(finish)
result = await retained("Hello")  # "'hello': 1 tokens"
```

Use immutable outputs or an explicit copy when a before/after comparison needs
a snapshot.

## Reusable operations

Gloe's public operations are lowercase factories with one consistent
configuration vocabulary:

```python
def positive(value: int) -> bool:
    return value > 0


def double(value: int) -> int:
    return value * 2


numbers = gloe.input() >> gloe.filter(positive) >> gloe.map(double)
result = await numbers([-2, 0, 3])  # [6]
```

`map(callback)` and `filter(predicate)` consume iterables sequentially and
return ordered lists. Their callbacks may be synchronous or asynchronous.
`condition(predicate, then=..., otherwise=...)` selects one branch. Use
`parallel(callables)` for a runtime homogeneous collection of independent
callables, or `sequential(callables)` when those callables must run in order.
Both return ordered lists. Static heterogeneous fan-out uses the tuple form
shown above.

For validation, keep synchronous validators small and explicit:

```python
def nonnegative(value: int) -> None:
    if value < 0:
        raise ValueError("value must be nonnegative")


@gloe.transformer
@gloe.ensure(incoming=nonnegative, outcome=nonnegative)
def add_checked(value: int, *, amount: int) -> int:
    return value + amount


pipeline = gloe.input[int]() >> add_checked(amount=2)
result = pipeline.sync(3)  # 5
```

Validators return `None` or raise. Configuration is excluded from the data
contract. Put `@gloe.transformer` outside `@gloe.ensure` for configured
functions; an unconfigured function can use `@gloe.ensure` directly.

## Inspect the graph

Graph inspection does not run business functions:

```python
graph = pipeline.graph()
nodes = graph.nodes
edges = graph.edges
result = pipeline.sync(3)  # 5

dot = pipeline.to_dot()       # DOT text
pipeline.to_dot("flow.dot")   # optional file path
pipeline.to_image("flow.png") # requires gloe[plot]
```

Repeated occurrences stay distinct in the graph. Graphs describe dependencies;
they do not claim that a stage is pure or cached.

## Migration

Gloe 0.8 uses one pipeline model. Functions and callable objects are ordinary
Python values, `@gloe.transformer` is a configuration factory, and native async
functions are composed directly. See the [migration table](docs/source/migration.md)
and [function cookbooks](docs/source/cookbooks.md) for common 0.7 rewrites.

## Scope

Gloe helps a team write, inspect, and type-check a flow. It is not a scheduler,
workflow service, transaction manager, retry system, dataframe schema
language, or automatic concurrency runtime. Resource lifetimes, retries,
transactions, loops, and domain algorithms stay in ordinary Python around the
pipeline.

Gloe is distributed under the [Apache License 2.0](LICENSE).
