# Core API

## `input`

`gloe.input()` creates an identity root whose input is inferred from the first
concrete stage. `gloe.input[T]()` anchors an explicit unary input when the first
stage is generic, overloaded, or ambiguous.

```python
import gloe


pipe = gloe.input[int]() >> str
result = pipe.sync(7)  # "7"
```

## `Transformer`

`gloe.Transformer(function)` wraps a callable as an explicit operator root. It
is useful for zero or multiple positional inputs, or when the callable itself
must start a `>>` expression. The type is `Transformer[P, R]`, where `P` is the
input call signature and `R` is the resolved output.

## Composition

`left >> right` returns a new immutable pipeline. `right` may be an ordinary
callable, configured callable, pipeline, or a tuple of static branch callables.
Tuples receive the same input concurrently and return an ordered tuple. A tuple
stays one value downstream; use `unpack(function)` for positional adaptation.

## Invocation and graph methods

```python
def increment(value: int) -> int:
    return value + 1


pipe = gloe.input[int]() >> increment
result = pipe.sync(2)  # 3
async_result = await pipe(2)  # 3, from an async entry point
graph = pipe.graph()
dot = pipe.to_dot()
pipe.to_dot("flow.dot")
pipe.to_image("flow.png")
```

Pipeline calls are awaitable even when every stage is synchronous. `.sync`
blocks and rejects a running event loop. Synchronous stages run on the caller's
thread.
