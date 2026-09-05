# Boundaries and limitations

Gloe checks callable signatures and executes the declared pipeline. It does not
prove that business logic is correct, pure, authorized, idempotent, or safe to
retry.

- Synchronous stages are not automatically offloaded.
- Identity branches retain references; they do not make deep copies or
  snapshots.
- Static typing cannot establish database contents, file schemas, dataframe
  columns, coordinate systems, or units. Validate those boundaries at runtime.
- Runtime-selected callable collections need a homogeneous contract.
- Graphs show dependency structure, not inferred caching or purity.
- A validator observes the values it receives. If code mutates the same object
  in place, use a fresh output or explicit snapshot when a before value matters.
- Async validators are outside the `ensure` contract; validators are
  synchronous and return `None` or raise.
- `transformer` and `ensure` inspect function signatures. For a callable
  object, decorate its bound `operation.__call__` method or an ordinary typed
  adapter. Decorate stages before composing them into a pipeline.
- Generic or overloaded first stages need `input[T]()`. A generic partial
  also needs a concrete input anchor instead of a direct `Transformer` root.
  Retain inferred partial types; an annotation such as `partial[str]` erases
  the parameter contract.
- Predicate narrowing is supported for concrete TypeIs/TypeGuard targets that
  are subtypes of the source item. Other targets retain the source type.
  Ambiguous overloaded or generic guards may require a typed adapter; a
  conditional's false branch must accept the full source type.
- Collection helper inference follows callback annotations. For example,
  `filter(bool)` has an `object` item contract; a predicate declared with an
  `int` parameter retains an `int` result element type. Use a domain-typed
  predicate when that precision matters downstream.

Keep loops, resource lifetimes, transactions, retries, and specialized domain
algorithms in ordinary typed Python when adding a Gloe operator would only give
them a new name.
