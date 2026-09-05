```{eval-rst}
:og:description: Gloe is a small, typed language for building inspectable Python pipelines.
```

# Gloe

Gloe connects ordinary typed Python callables into immutable, inspectable
pipelines. The 0.8 API has one execution model: build with `>>`, invoke with
`await pipe(value)`, or use `pipe.sync(value)` from synchronous code.

Start with [the canonical pipeline](getting-started/transformers.md), then read
the [migration table](migration.md) when moving from 0.7. The
[cookbooks](cookbooks.md) show how to keep reductions, `map`-over-data, loops,
and domain-specific algorithms as ordinary Python functions.

```{toctree}
:caption: Learn
:maxdepth: 2
:hidden:

getting-started/index
examples/index
patterns/index
advanced/index
migration
cookbooks
faq
limitations
philosophy
```

```{toctree}
:caption: Reference
:maxdepth: 2
:hidden:

api-reference/index
```
