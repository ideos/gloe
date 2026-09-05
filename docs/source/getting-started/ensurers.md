# Runtime validation with `ensure`

`ensure` decorates an ordinary unary data function with synchronous validators.
An incoming validator checks the data before the function runs, an outcome
validator checks the resolved result, and a changes validator receives both
values:

```python
import gloe


def nonnegative(value: int) -> None:
    if value < 0:
        raise ValueError("value must be nonnegative")


def increased(before: int, after: int) -> None:
    if after <= before:
        raise ValueError("value did not increase")


@gloe.ensure(incoming=nonnegative, outcome=nonnegative, changes=increased)
def add_one(value: int) -> int:
    return value + 1


pipe = gloe.input[int]() >> add_one
result = pipe.sync(2)  # 3
```

Validators return `None` or raise. They are synchronous and run before later
pipeline effects. Supply one validator or a tuple/list of validators for each
kind. The wrapped function remains an ordinary callable with its data
signature; configuration is outside the data contract.

## Configured functions

Place `@gloe.transformer` outside `@gloe.ensure` when the function also has
keyword-only configuration:

```python
@gloe.transformer
@gloe.ensure(incoming=nonnegative, outcome=nonnegative)
def add(value: int, *, amount: int) -> int:
    return value + amount


pipe = gloe.input[int]() >> add(amount=2)
result = pipe.sync(1)  # 3
```

This order lets `ensure` validate the unary data input and resolved output
while `transformer` binds `amount` as configuration. An identity branch keeps a
reference to the incoming value; it is not an automatic deep copy. Use an
immutable result or an explicit snapshot when `changes` needs a before value.
