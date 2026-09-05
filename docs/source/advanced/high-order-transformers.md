# Higher-order functions

When a stage receives another callable, keep that contract in an ordinary
function. Gloe can compose the resulting callable or pipeline without a
special high-order class.

```python
import gloe
from collections.abc import Callable


def make_reducer(
    reducer: Callable[[int, int], int], *, initial: int = 0
) -> Callable[[list[int]], int]:
    def reduce_values(values: list[int]) -> int:
        result = initial
        for value in values:
            result = reducer(result, value)
        return result

    return reduce_values


sum_values = make_reducer(lambda total, value: total + value)
pipeline = gloe.input[list[int]]() >> sum_values
result = pipeline.sync([1, 2, 3])  # 6
```

If configuration should be visible to the pipeline checker, use a
keyword-configured function:

```python
@gloe.transformer
def reduce_with(value: list[int], *, reducer: Callable[[int, int], int]) -> int:
    total = 0
    for item in value:
        total = reducer(total, item)
    return total


pipeline = gloe.input() >> reduce_with(reducer=lambda a, b: a + b)
result = pipeline.sync([1, 2, 3])  # 6
```

The [function cookbooks](../cookbooks.md) cover reductions, map-over-data, and
runtime-selected callables. Keep domain rules and resource ownership in these
ordinary functions.
