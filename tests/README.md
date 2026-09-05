# Runtime verification map

See [the contract matrix](contract-matrix.md) for accepted forms, intentional
rejections, real scenarios and the accounting for removed 0.7 tests.

The runtime suite targets the 0.8 public API and uses only the
standard library plus Gloe itself.  `tests/scenarios.py` contains synthetic
records and operations shaped like reporting, reconciliation, route
preparation, indicator selection, monetary allocation, and transactional import
workflows; it does not connect to external services or use production data.

| Contract | Runtime coverage |
| --- | --- |
| CAP-PIPE-001 | `test_runtime.py`: one async call path, ordinary sync/async/bound callables, `.sync()` |
| CAP-PIPE-002 | Explicit and inferred input roots; zero/multiple root arguments; reusable calls |
| CAP-PIPE-003 | Lazy immutable plans, declaration order, failure and cancellation cleanup, long chains |
| CAP-PIPE-004 | Configuration-only keyword binding, no-config factories, variadic rejection, ordinary variadics |
| CAP-PIPE-005 | Ordered sequential map/filter, pipeline callbacks, boolean predicates, selected conditions, dynamic branch collections |
| CAP-PIPE-006 | Tuple-as-value behavior and explicit `unpack` adapter |
| CAP-PIPE-007 | Incoming/outcome/change validation, async isolation, validator shape/return checks, mutation reference semantics |
| CAP-PIPE-008 | Explicit data fork/join and repeated complete-pipeline execution |
| CAP-PIPE-009 | Graph projection, repeated occurrences, nested fanout, callback edges, DOT and optional SVG export |

Core runtime tests live in `test_runtime.py`, `test_workflows.py`, `test_graph.py`
and `test_boundaries.py`. Execution-boundary, service-workflow and shared
typing/runtime matrix tests extend those contracts. SVG export is optional locally and required by the CI
environment, which installs Graphviz. Run the complete contract with:

```sh
python -m pip install -e '.[dev,plot]'
python -m unittest discover
```

The typing suite separately checks positive type assertions, consumer records,
exact negative diagnostics and error codes at marked source lines, cold/warm
checker caches, dependency invalidation, and failure without plugin setup.
The `positive_matrix.py` programs are both checked and executed. Service
scenarios exercise typed ports for request handling and event ingestion.
The original arity/sync class permutations are consolidated under the one
executor; removed bridge cases are represented by explicit data fork/join and
concurrent invocation tests. Internal type-formatting/class-copy tests have no
remaining production counterpart.
