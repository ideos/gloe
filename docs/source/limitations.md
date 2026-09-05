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

Keep loops, resource lifetimes, transactions, retries, and specialized domain
algorithms in ordinary typed Python when adding a Gloe operator would only give
them a new name.
