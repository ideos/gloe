# API reference

The reference describes the small public 0.8 surface. It is written directly
so documentation builds do not depend on importing application modules or
auto-importing legacy package paths.

```{toctree}
:maxdepth: 2

gloe
factories
graph
typing
```

## Public exports

The top-level package exports:

```text
Transformer
input
transformer
map
filter
condition
parallel
sequential
unpack
ensure
```

Native `async def` functions, callable objects, bound methods, partials, and
other pipelines use these same exports. There are no separate async, multi-input
or branch-class variants.
