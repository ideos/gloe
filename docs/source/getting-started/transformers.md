# Building a pipeline

Gloe composes ordinary typed Python functions. The standard case needs no
decorator:

```python
import gloe


def parse(raw: str) -> int:
    return int(raw)


def double(value: int) -> int:
    return value * 2


pipe = gloe.input() >> parse >> double
result = pipe.sync("7")  # 14
```

The pipeline is a value. It can be stored, passed to another function, or
composed into a larger pipeline. `>>` creates a new immutable sequence, so a
later composition cannot mutate an earlier definition.

## Configured stages

Use `@gloe.transformer` when keyword-only parameters are configuration rather
than flowing data:

```python
@gloe.transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


pipe = gloe.input() >> add(amount=2)
result = pipe.sync(3)  # 5
```

The decorator always creates a configuration factory. Positional parameters
describe pipeline input; keyword-only parameters describe configuration. After
configuration, `add(amount=2)` is an ordinary callable with the input
signature. This keeps generic input variables scoped to the configured
callable.

For a stage with no configuration, prefer an undecorated function. If a
decorator is needed for a common factory interface, call the factory with no
arguments before composing it:

```python
@gloe.transformer
def normalize(value: str) -> str:
    return value.strip().lower()


pipe = gloe.input[str]() >> normalize()
result = pipe.sync(" Hello ")  # "hello"
```

Do not use a variadic configuration factory. An ordinary variadic function can
still be composed when the incoming signature permits it.

## Callable roots and tuples

Most roots are `gloe.input() >> stage`. For a callable that must itself start
an operator expression, use `gloe.Transformer(function)`. It also supports a
root with zero or multiple positional inputs when the function's signature
requires that shape:

```python
def combine(left: int, right: int) -> int:
    return left + right


combine_root = gloe.Transformer(combine)
result = combine_root.sync(2, 3)  # 5
```

A tuple is not implicitly spread into `combine`. Adapt it explicitly:

```python
join = gloe.input[tuple[int, int]]() >> gloe.unpack(combine)
result = join.sync((2, 3))  # 5
```

## Composition boundaries

Gloe checks each edge and branch with its bundled mypy plugin. The plugin is
enabled in the consuming project's configuration; package installation never
edits that configuration. `Transformer[P, R]` exposes the input call signature
`P` and resolved result `R`, including native async stages.

Functions do not gain `fn >> fn` by being ordinary functions. Start the
expression with `gloe.input()` or wrap a callable explicitly with
`gloe.Transformer`.
