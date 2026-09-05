# Explicit adapters

Gloe keeps data flow visible through ordinary Python values. Two small adapters
cover the cases that are ambiguous in a generic callable composition.

## `unpack`

A tuple is one value. Use `unpack(function)` when a tuple must be passed as
positional arguments:

```python
import gloe


def format_pair(left: str, right: int) -> str:
    return f"{left}:{right}"


pipe = gloe.input[tuple[str, int]]() >> gloe.unpack(format_pair)
result = pipe.sync(("id", 3))  # "id:3"
```

Do not infer tuple spreading by counting parameters. Defaults, `*args`,
callable objects, partials, and `print` make that rule ambiguous.

## `Transformer`

`gloe.input() >> function` is the normal operator root. Wrap a callable with
`gloe.Transformer(function)` when it must itself start an expression or has a
zero/multiple-input signature:

```python
def combine(left: int, right: int) -> int:
    return left + right


pipe = gloe.Transformer(combine) >> str
result = pipe.sync(2, 3)  # "5"
```

The explicit wrapper does not change the function's runtime behavior; it gives
the composition system a root with a known call signature.

## Retaining earlier data

Use an identity branch and a typed join instead of hidden context:

```python
def extract(value: int) -> tuple[int, ...]:
    return (value, value + 1)


def finish(original: int, words: tuple[int, ...]) -> str:
    return f"{original}:{len(words)}"


prefix = gloe.input[int]()
pipeline = prefix >> (gloe.input(), extract) >> gloe.unpack(finish)
result = pipeline.sync(7)  # "7:2"
```

The identity branch retains a reference. It does not make a copy, attach
invocation state, or deduplicate repeated work. Use immutable domain values or
an explicit snapshot when a stable before value is needed.
