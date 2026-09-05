# Inspecting and exporting graphs

Every pipeline exposes its dependency graph without running business
functions:

```python
import gloe


def increment(value: int) -> int:
    return value + 1


pipeline = gloe.input[int]() >> increment
result = pipeline.sync(2)  # 3
graph = pipeline.graph()
print(graph.nodes)
print(graph.edges)
```

`nodes` and `edges` are the public structural projection. A repeated stage is a
separate occurrence, so the graph reflects the sequence that will execute.
Graphs describe dependencies; they do not infer purity, caching, or
authorization.

## DOT output

Use the graph or the pipeline directly:

```python
dot_text = graph.to_dot()
dot_text = pipeline.to_dot()
pipeline.to_dot("flow.dot")
```

The optional path writes the DOT representation and returns the representation
as defined by the public API. `pipeline.to_image(path)` renders an image with
Graphviz. Install the plotting extra and the Graphviz system dependency when
image output is needed:

```shell
pip install 'gloe[plot]'
```

Graph export is a development and documentation aid. It does not change
execution or add a scheduler.
