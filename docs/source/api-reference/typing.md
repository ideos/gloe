# Typing and mypy

Install the tested checker extra:

```shell
pip install 'gloe[types]'
```

Enable the bundled plugin explicitly in the consuming project:

```toml
[tool.mypy]
plugins = ["gloe.mypy_plugin"]
```

The extra pins mypy 2.3.1. Installation does not edit the configuration. The
plugin checks each composition edge and branch, normalizes one awaitable return
layer, partitions transformer configuration signatures, and infers input
anchors when the first stage supplies a concrete constraint.

Other checkers can analyze the ordinary functions, but Gloe's verified
composition contract is the mypy plugin path. Static typing does not establish
runtime database values, file contents, purity, authorization, or business
correctness.
