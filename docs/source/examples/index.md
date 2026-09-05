# Examples

These examples show the 0.8 composition vocabulary. They use ordinary typed
functions for domain work and keep application-owned state explicit.

The executable contract at [`pipelines.py`](pipelines.py) runs the same shapes
with concrete values and assertions. From the repository root, with the
project dependencies installed:

```shell
python -m docs.source.examples.pipelines
```

It exits silently when every expected result matches.

```{toctree}
:maxdepth: 2

consumer-scenarios
```
