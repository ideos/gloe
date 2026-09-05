# Conditional flows

Use `condition(predicate, then=..., otherwise=...)` when one value should take
exactly one of two callable branches:

```python
import gloe


def is_priority(order_total: int) -> bool:
    return order_total > 100


def send_priority(order_total: int) -> str:
    return f"priority:{order_total}"


def send_standard(order_total: int) -> str:
    return f"standard:{order_total}"


route = gloe.condition(
    is_priority,
    then=send_priority,
    otherwise=send_standard,
)
process = gloe.input[int]() >> route
priority_result = process.sync(150)  # "priority:150"
standard_result = process.sync(80)  # "standard:80"
```

The predicate is evaluated once for the current value and only the selected
branch runs. The branches may be synchronous, asynchronous, configured
callables, or pipelines when their input and output contracts agree.

For more than two cases, keep the selection logic as an ordinary typed
function or use a named dispatch table. That makes domain policy visible and
avoids hiding a growing decision tree inside a convenience operator.
