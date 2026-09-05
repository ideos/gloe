# Operation factories

## `transformer`

`@gloe.transformer` always returns a configuration factory. Positional
parameters are pipeline inputs; keyword-only parameters are configuration.
Calling the factory binds configuration and returns an ordinary callable with
only its input signature. A no-configuration decorated function is called as
`stage()` before composition.

## `map` and `filter`

```python
gloe.map(callback)
gloe.filter(predicate)
```

Both consume iterables sequentially and return ordered lists. Callbacks may be
sync or async. `filter` requires actual boolean results.

## `condition`

```python
gloe.condition(predicate, then=when_true, otherwise=when_false)
```

It evaluates the predicate once and executes exactly one branch.

## `parallel` and `sequential`

```python
gloe.parallel(callables)
gloe.sequential(callables)
```

These factories accept runtime homogeneous collections. Both return ordered
lists. `parallel` runs independent branches concurrently, while `sequential`
invokes each callable in order. Static heterogeneous branches use a tuple after
`>>`.

## `unpack`

```python
gloe.unpack(function)
```

This explicit adapter turns one tuple value into positional arguments for
`function`. Gloe never spreads tuples implicitly.

## `ensure`

```python
gloe.ensure(incoming=..., outcome=..., changes=...)
```

Validators are synchronous, receive the unary data input, resolved output, or
both, and return `None` or raise. Configuration is excluded from the data
contract. Before values are references; use immutable outputs or an explicit
snapshot when necessary.
