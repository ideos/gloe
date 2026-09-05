# Architecture and API

The runtime uses one immutable sequence of callable/branch nodes and one await-normalization boundary per invocation. Awaitable input values remain data at identity nodes. A callable result is awaited once; returned nested awaitables remain data. Synchronous work runs on the caller's thread; offloading is explicit.

Public exports: `Transformer`, `input`, `transformer`, `map`, `filter`, `condition`, `parallel`, `sequential`, `unpack`, `ensure`. `@transformer` is always a configuration factory, including functions with no configuration (call `stage()`); normally use undecorated functions directly. It returns an ordinary callable so input-scoped generic variables remain generic after configuration. Use `Transformer(fn)` when a callable must itself start an operator expression, or prefer the uniform `input() >> fn` pattern.

Core lives in `gloe/_core.py`; configuration/collection/branch factories in `gloe/_functions.py`; ensurers in `gloe/_validation.py`; graph projection in `gloe/_graph.py`. Public reexports are explicit. The bundled `gloe.mypy_plugin` may have private typing helpers but does not execute in application runtime. It asks mypy to check synthetic calls at each composition edge, normalizes one Awaitable return layer, partitions configuration signatures and infers anchors. It is pinned to the tested mypy release because checker plugins are not a stable cross-checker extension standard.

Configure `[tool.mypy] plugins = ["gloe.mypy_plugin"]`. Installation does not modify user configuration. Other checkers can check ordinary functions; they do not provide the verified composition contract.

No bridge, implicit context store, automatic caching/deduplication, attach/pick/drop helpers, domain-specific dataframes or automatic transaction/retry machinery. Preserve earlier data using explicit forks and typed joins. Use fresh immutable outputs or an explicit snapshot to compare values across mutation.

Implementation budget: replace the existing duplicated runtime modules with four small runtime modules and a checker plugin; port scenario coverage, add distinct workflow and typing regression tests, and replace stale API docs. No downstream edits or release publication.

Collection and branch helper factories take their main callback or collection positionally. `using=` remains available as an ordinary named argument, but is not required. `condition` keeps `then` and `otherwise` keyword-only. Business configuration under `@transformer` remains keyword-only.
