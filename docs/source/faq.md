# FAQ

## Why does every pipeline call need `await`?

One invocation contract keeps synchronous, asynchronous, and mixed pipelines
interchangeable. Use `pipe.sync(value)` at a synchronous boundary. It blocks and
rejects a running event loop.

## Does Gloe run synchronous work in a thread?

No. Synchronous stages stay on the caller's thread. Choose an explicit executor
or `asyncio.to_thread` when an application needs that boundary.

## How do I keep the original value after a transformation?

Fork explicitly with an identity stage and join the resulting tuple with an
ordinary typed function. The identity branch keeps a reference. It does not
deep-copy or snapshot mutable data.

## Why does mypy need a plugin?

Python's type system does not provide a general mapped type for heterogeneous
branch tuples and resolved awaitable return types. Gloe's bundled plugin checks
each composition edge and branch with mypy's call checker. Install
`gloe[types]` and add `plugins = ["gloe.mypy_plugin"]` to the project's mypy
configuration. Installation does not edit that file.

## Can another type checker validate composition?

Other checkers can type-check the ordinary functions. Gloe only claims the
composition contract for the tested mypy plugin path.

## Is Gloe a workflow scheduler?

No. Scheduling, retries, transactions, resource lifetimes, loops, and domain
algorithms remain explicit application code.

## Where is the migration guide?

See the [0.7 to 0.8 migration table](migration.md) and the
[function cookbooks](cookbooks.md).
