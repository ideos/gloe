# Graph API

`pipe.graph()` returns the public graph projection. It exposes `nodes` and
`edges` and can produce DOT without running pipeline stages:

```python
import gloe


def increment(value: int) -> int:
    return value + 1


pipe = gloe.input[int]() >> increment
result = pipe.sync(2)  # 3
graph = pipe.graph()
nodes = graph.nodes
edges = graph.edges
dot = graph.to_dot()  # DOT text containing "increment"
```

The pipeline forwards the same export operations:

```python
dot = pipe.to_dot()
pipe.to_dot("flow.dot")
pipe.to_image("flow.png")
```

`to_image` uses the optional Graphviz integration. Install `gloe[plot]` and
the system Graphviz executable when image output is required. Repeated nodes
remain distinct and graph projection never infers caching or purity.
