# Verification

Runtime tests cover CAP-PIPE-001–009 with arithmetic, mixed async work, generics/configuration, nested and dynamic branches, cancellation/errors, iteration, graph inspection, repeated stages and concurrent reuse. Real workflow fixtures cover reporting registries, reconciliation, monetary conservation, route preparation, indicators and transactional imports with synthetic data and explicit resource ownership.

Typing tests assert exact inferred types, configuration signatures and branch results. Negative fixtures require diagnostics at marked source lines for incompatible edges, unknown outputs, invalid configuration, invalid validators and malformed callbacks. Source checking is separate from intentionally invalid fixtures. Run supported Python versions, formatting, package build/install and documentation build; optional Graphviz export is exercised where its dependency is installed.

No finite suite claims all possible Python programs. Consumer scenarios verify library contracts; they do not claim execution of external databases or geospatial/dataframe integrations.

`tests/contract-matrix.md` accounts for supported input/callable/configuration/result/topology forms, rejections, real scenarios and retired 0.7 behavior. Positive matrix programs execute as well as type-check. Rejection fixtures require their intended messages and error codes, not just an error on the expected line. Cold/warm checker caches and dependency invalidation are part of the gate.
