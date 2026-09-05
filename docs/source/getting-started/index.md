# Getting started

The guide uses one pattern throughout:

```python
import gloe


def parse(raw: str) -> int:
    return int(raw)


def validate(value: int) -> int:
    if value < 0:
        raise ValueError("negative value")
    return value


def save(value: int) -> str:
    return f"saved:{value}"


pipe = gloe.input() >> parse >> validate >> save
result = pipe.sync("7")  # "saved:7"
```

Each name after `>>` is an ordinary callable, a configured callable factory,
another pipeline, or a documented branch factory. Construction is immutable and
does not execute user code.

```{toctree}
:maxdepth: 2

main-concepts
transformers
async-transformers
conditional-flows
collection
ensurers
utilities
gateways
plotting
partial-transformers
```
