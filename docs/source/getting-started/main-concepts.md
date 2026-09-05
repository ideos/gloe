# Main concepts

Gloe has a deliberately small runtime model:

- a pipeline is an immutable sequence of callable and branch nodes;
- one invocation boundary normalizes one awaitable result layer;
- ordinary functions, callable objects, bound methods, partials, and pipelines
  can be stages;
- synchronous work stays on the caller's thread;
- graph projection describes dependencies without executing stages.

## Input anchors

`gloe.input()` is an identity stage. It infers its input from the first concrete
stage:

```python
import gloe


def parse(raw: str) -> int:
    return int(raw)


parse_number = gloe.input() >> parse
result = parse_number.sync("7")  # 7
```

Use `gloe.input[T]()` when the first stage is generic, overloaded, or otherwise
ambiguous:

```python
identity = gloe.input[bytes]()
result = identity.sync(b"data")  # b"data"
```

Inference is local to the composition edge. It does not inspect future calls or
runtime data. The explicit anchor resolves that ambiguity for both the runtime
and the mypy plugin.

## Values and edges

Each stage receives one preceding value. A tuple is one value, even when it was
created by a branch. Use `gloe.unpack(function)` when a tuple must become
positional arguments. `Transformer(function)` is the explicit root for a
callable with zero or multiple positional inputs; most pipelines are clearer
with `input()` and one ordinary stage.

`>>` returns a new pipeline. It never runs a stage while constructing the
pipeline and it never deduplicates repeated sequences. If a prefix must feed
two computations, put the identity stage and the computations in one explicit
tuple branch.

## Invocation

Every pipeline call is awaitable. A synchronous pipeline still uses the same
async boundary, which keeps composition predictable when an async stage is
introduced later. `.sync(...)` drives that execution for synchronous callers
and rejects a running event loop.

Native async functions can be stages directly. Gloe awaits the callable's
result once; a nested awaitable returned intentionally by a callable remains
data. A synchronous callable is never automatically offloaded.

## Static and dynamic branches

The tuple form is a static heterogeneous fan-out. Its branches receive the
same value concurrently and produce an ordered tuple. `parallel(callables)`
and `sequential(callables)` are for a runtime homogeneous iterable of
callables. The former runs independent callables concurrently; the latter
runs them in order. Their cancellation and error behavior is part of the
pipeline contract: an error cancels and awaits outstanding siblings.
