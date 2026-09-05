# Configured functions

Use a normal Python factory when configuration is already explicit:

```python
def add(amount: int):
    def apply(value: int) -> int:
        return value + amount

    return apply


pipe = gloe.input[int]() >> add(2)
result = pipe.sync(3)  # 5
```

Use `@gloe.transformer` when the keyword-only configuration should be part of
the declared pipeline contract:

```python
@gloe.transformer
def add(value: int, *, amount: int) -> int:
    return value + amount


pipe = gloe.input() >> add(amount=2)
result = pipe.sync(3)  # 5
```

After configuration, both examples supply an ordinary unary callable. The
configured callable can be reused in several pipelines without carrying
invocation-specific state.

`@gloe.transformer` is always a factory, even when it has no keyword-only
parameters. In that case call it with no arguments before composition; for most
unconfigured stages, a plain function is clearer.
