# Generic pipelines and explicit roots

The public type is `Transformer[P, R]`: `P` is the callable input signature and
`R` is the resolved output. A function with one integer input and a string
output can be named explicitly as:

```python
import gloe
from gloe import Transformer


def stringify(value: int) -> str:
    return str(value)


stage: Transformer[[int], str] = Transformer(stringify)
result = stage.sync(7)  # "7"
```

Most code can leave the type to the plugin:

```python
pipeline = gloe.input() >> stringify
result = pipeline.sync(7)  # "7"
```

Use an explicit anchor when a generic function cannot establish its input from
the first edge:

```python
def identity[T](value: T) -> T:
    return value


pipeline = gloe.input[int]() >> identity
result = pipeline.sync(7)  # 7
```

The plugin checks each composition edge and branch. It does not infer a whole
program's runtime values, database state, or protocol intersections. For a
callable with multiple positional inputs, `Transformer(function)` supplies the
operator root; a tuple-to-call adaptation still requires `gloe.unpack`.
