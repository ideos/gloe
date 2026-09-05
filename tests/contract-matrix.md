# Contract coverage and migration accounting

This matrix defines the finite acceptance surface for the 0.8 API. It does not
claim to enumerate every Python program. A supported form needs a successful
typing example and an executed result; an invalid boundary needs an intended
diagnostic or a runtime exception test. Application algorithms and external
systems remain the application's responsibility.

## Supported forms and boundaries

| Surface | Accepted and executed | Rejected or explicitly bounded |
| --- | --- | --- |
| Roots | `positive_matrix.roots`: zero, unary, multiple inputs, positional-only, defaults, keyword-only root parameters, ordinary variadics, native async, retained partial signatures | `negative_matrix`: missing/extra inputs, wrong positional/keyword types, erased inputs/results, unresolved generic partial roots |
| Input inference | `positive.py`, `positive_matrix.py`: concrete functions, methods, callable objects, configured functions, partials, compatible branches | `negative_inference.py`: unknown/generic/overloaded anchors, incompatible branches, identity-only inference; use `input[T]()` |
| Stages and values | `positive_matrix.values_and_callbacks`: functions, generic/constrained functions, protocols, nominal identifiers, TypedDict, recursive JSON aliases, callable objects, aliases, bound methods | `negative_guardrails.py`, `negative_matrix.py`: nested Any, erased callable signatures, invalid records/units/literals, recursive aliases containing Any |
| Invocation | `positive_matrix`: exact awaited result types, `.sync`, async-returning callables, custom Awaitable, Task, nested Awaitable and awaitable input data | `negative_matrix.execution`: bad awaited/blocking calls, missing await, wrong resolved output; runtime rejects `.sync` within an event loop |
| Configuration | `positive_matrix.roots`: required/default configuration, positional defaults, generic variables bound by configuration, reusable input generics, input overloads sharing config, config-selected overloads | `negative_factories.py`, `negative_matrix.py`: missing/unknown/wrong config, positional config, rebinding config at execution, variadic factories, invalid overload selections |
| Static topology | `positive_matrix.topology`: empty, singleton, eight-way, nested forks, identity branches, complete-plan reuse | `negative_matrix.py`: bad final branch, lists/raw nested tuples as stages, incompatible identities; arbitrary runtime branch collections use `parallel`/`sequential` |
| Tuple adaptation | `positive_matrix.topology` and `.roots`: zero/one/multiple arguments, defaults, optional keyword defaults, async configured functions, overloads | `negative_helpers.py`, `negative_matrix.py`: required keyword inputs, variadics, wrong arity/types, unknown tuple length, non-callables |
| Collection helpers | `positive_matrix.values_and_callbacks`, `test_runtime.py`: sync/async/generic/partial/pipeline callbacks, iterators, empty inputs, TypeIs and TypeGuard filtering | `negative_helpers.py`, `negative_matrix.py`: wrong iterable elements, erased callbacks/outputs, non-bool predicates; `test_execution_boundaries.py`: fail-fast consumption and cancellation |
| Conditions | `positive_matrix.topology` and `.values_and_callbacks`: nested optional unions, async predicates, mixed result modes, narrowed true branches | `negative_matrix.py`: bad predicate, incompatible true/false branches, unknown outputs; false branches receive the full source type |
| Dynamic branches | `positive_matrix.py`, `test_runtime.py`: mixed sync/async homogeneous contracts, empty typed collections, declaration order | `negative_matrix.py`: non-callables, erased signatures/outputs; `test_execution_boundaries.py`: configuration snapshots, repeated execution, sequential short-circuit |
| Validation | `positive.py`, `positive_matrix.py`, runtime/boundary tests: incoming/output/changes, lists/tuples/callable validators, function aliases, overloads, both decorator orders, async isolation, default inputs | Negative fixtures: wrong validator inputs/outputs, non-None/async validators, non-unary and variadic stages; runtime failures prevent later effects |
| Lifetimes and failures | `test_runtime.py`, `test_execution_boundaries.py`, `test_workflows.py`: original exceptions, sibling/parent cancellation, stream closing, resource scopes, concurrent reuse, reference semantics | No hidden offloading, snapshotting, retry, deduplication, transaction, or context-store guarantees |
| Graphs | `test_graph.py`: pure projection, nested/empty forks, identities, repeated occurrences, helper callbacks, independent snapshots, DOT and actual SVG export | Missing optional Graphviz dependency has an explicit installation error; old representation/styling internals are not retained |
| Checker execution | `test_typing.py`: cold and warm caches, changed dependency invalidation, exact diagnostics and error codes, source checking in CI | Missing plugin and erased checker information fail closed; other checkers are not claimed equivalent |

`test_execution_boundaries.test_mixed_generated_plans_match_direct_arithmetic`
also varies depth, width, empty forks and reusable mixed sync/async subplans
with a fixed random seed and an independent arithmetic result. This complements
named examples; it does not replace exact static type assertions.

## Real application scenarios

- Reporting registries and loader/report fan-in, including unknown registry entries.
- Hierarchical reconciliation preserving unmatched state and original input.
- Monetary allocation with positive/negative/zero amounts, remainder conservation,
  invalid configuration and prevention of faulty persistence.
- Route preparation retaining the network while selecting constrained hot seeds;
  nominal distance units are checked separately from runtime data validity.
- Dynamic indicator registries with sync/async implementations and stable order.
- Transactional imports with accumulated errors, commit, rollback, cancellation,
  empty work and explicit context ownership.
- Request handling with an async protocol port, found/missing users, correlation
  data retention and authorization failure before I/O.
- Event ingestion with validation, bounded transient retries, cancellation and
  duplicate delivery; the application ledger owns deduplication.

These scenarios use synthetic data and in-memory ports. They do not claim
database, HTTP framework, dataframe or geospatial engine integration coverage.

## Accounting for removed 0.7 tests

| Removed tests | Replacement or intentional retirement |
| --- | --- |
| `basic/test_transformer_basic.py`, `basic/test_async_transformer.py` | Core execution, immutability, ordinary callables, long chains, recursive application stages, failure identity and loop boundaries in `test_runtime.py`; metadata in `test_execution_boundaries.py`. Separate class copying, repr, equality and signature-rendering internals were retired. |
| `basic/test_basic_transformer_types.py` | `positive.py`, `positive_matrix.py`: linear/mixed pipelines, fan-out beyond the old seven-branch limit, identity retention and async normalization. |
| `multiargs/test_multiargs_transformer_basic.py`, `test_async_multiargs_transformer.py`, `test_multiargs_transformer_types.py` | `positive_matrix.roots`/`.topology`, runtime root/tuple tests and negative root/adapter cases. Implicit tuple spreading and separate arity classes were retired. |
| `partial/test_partial_transformer.py`, `test_partial_async_transformer.py`, `test_partial_transformer_types.py` | Configured and stdlib partial cases in positive/negative fixtures and runtime tests, including async and generic reuse. Separate partial decorators/classes were retired. |
| `collection/test_transformer_collection.py`, `test_transformer_collection_async.py`, `test_transformer_collection_types.py` | Lowercase helper fixtures, fail-fast iterable tests, pipeline callbacks and explicit map-over/reduce application helpers. The Map/Filter/MapOver class families were retired. |
| `conditional/test_conditioner_transformer.py`, `test_async_conditioner_transformer.py`, `test_conditional_transformer_types.py` | Nested `condition` fixtures covering optional unions, async predicates/branches and selected-only execution. The fluent If/Then/Else class builder was retired. |
| `ensurer/test_transformer_ensurer.py`, `test_async_transformer_ensurer.py`, `test_transformer_ensurer_types.py` | Decorator order, signature preservation, overload validation, failure sequencing, callable validators, invocation-local state and tuple adapters in runtime/boundary/typing fixtures. Decorate the underlying function before pipeline composition. |
| `test_gateways.py` | Dynamic parallel/sequential tests, mixed callback modes, ordering, failure and reuse tests. |
| `test_transformer_bridge.py` and bridge typing cases | Explicit identity fork/join, retained request/document data, concurrent invocation isolation and repeated-prefix tests. Shared bridge storage was deliberately removed. |
| `test_transformer_graph.py`, `test_transformer_export.py` | `test_graph.py` and optional-dependency boundary tests. Old private node classes, begin/invisible-node conventions, custom subgraph internals and deprecated export names were retired. |
| `test_transformer_utils.py` | Identity, tuple adaptation, explicit fork/join and ordinary side-effect stages. Attach/forward/debug wrappers and private composition entry points were retired. |
| `test_type_formatting.py` | Retired with the custom type-formatting implementation; no public replacement contract. |

## Maintaining rejection evidence

Each `# reject: case_name` is matched to `diagnostics.json`. The harness checks
all messages and error codes at that source location, rejects unexpected
diagnostics elsewhere, and rejects missing or stale case identifiers. Do not
refresh expected diagnostics just to make a test pass: inspect whether the
failure still proves the named boundary. A checker-version change requires a
deliberate review of this contract.

Runtime line coverage omits the plugin because mypy executes in subprocesses.
The plugin is tested through the real checker, not mocked mypy contexts. A
separate coverage audit can instrument mypy with `coverage run` and
`--no-fast-exit`; that audit identifies missing public paths without turning
defensive mypy-internal branches into artificial acceptance requirements.

The matrix also records conservative inference boundaries: a broad builtin
predicate such as `bool` gives `filter` an `object` item contract, while a
domain-typed predicate retains that domain. TypeGuard targets outside the
source item's subtype relationship retain the source type. These limitations
have explicit positive assertions instead of silently claiming narrower types.
