# Main Concepts

The main idea behind Gloe is constraining the implementation of a specific processing into a formalized and type-safe **flow** (or execution graph). Every step (or node) of this flow is responsible for transforming its input into the input of the next step, thereby composing a sequential execution process. No code from this flow can be executed outside these steps, and each node in the graph is called a **transformer**.

Formally, a flow is defined as a DAG (Directed Acyclic Graph) with one source and one sink, meaning it has a beginning and an end. In practice, it is a sequence of steps that transform data from one form to another.

Basic structure of a flow:
``` 
(type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> ... -> (type X)
```
```{admonition} Naming things
:class: seealso
Type A is called **incoming type** and type X is called **outcome type** of
the graph.
```


A transformer must have an atomic and well-defined responsibility. As we will see later, implementing a transformer is an exceptionally straightforward task, so having many of them is not problematic. Keep it simple, hence making it easier to understand, document, and test!


## Lightness

Gloe is a lightweight library, it is not a development environment, an engine, or even a heavy framework; instead, it was built more on the basis of **strong concepts** than on an exhaustive amount of code.

Its dependencies are only other python libraries (currently, only [typing-extensions](https://pypi.org/project/typing-extensions/)), nothing external is required.

## Type-safety

Gloe was implemented to be completely type-safe. This means that when using Gloe, you must provide all the necessary type hints of the created transformers, which can be summed up in its incoming and outcome types. Using these definitions, Gloe can warn about a malformed flow right away in the IDE and make precise inferring of extremely complex types.

For example, consider the below Transformer:

``` text
(type A) -> [MyTransformer] -> (type B)
```

The next transformer that can be appended to `MyTransformer`
must have the following signature:

``` text
(type B) -> [NextTransformer] -> (some type C)
```

That is, the outcome type of `MyTransformer` must be the same as the incoming type of `NextTransformer`. When building your graphs, you will know about any problem with types immediately.

```{admonition} Naming things
:class: seealso
The representation of a transformer with its name and types is called
**signature**.
```

To perform this kind of behavior, Gloe uses the most recent and
sophisticated features of [Python typing
library](https://docs.python.org/3/library/typing.html).

## Immutability

An important concept adopted by Gloe is immutability. Every time a
Transformer is instantiated and appended as a next step of an existing
one, a new Transformer is created, **composing the internal operations of
both transformers sequentially**.

```
(type A) -> [Transformer 1] -> (type B) -> [Transformer 2] -> (type C)

Above graph is in fact this:

(type A) -> [Transformer 1 and 2] -> (type C)
```

This means that every time we talk about a flow, we are also referring to a transformer! Flow is the **concept**, and transformers are its implementation.

**Flow is a transformer** (intermediate types were omitted for simplicity):
```
                                 +--------- Transformer [ ... [[1 2] 3] ... N] --------+
                                 |                                                     |
                                 |                                                     |
                                 |                                                     |
                  +------ Transformer [[1 2] 3] -----+                                 |
                  |                                  |                                 |
      +-- Transformer [1 2] --+                      |                                 |
      |                       |                      |                                 |
[Transformer 1]   ->   [Transformer 2]   ->   [Transformer 3]   ->   ...   ->   [Transformer N]
```
```{admonition} Naming things
:class: seealso
In other places of this documentation, the term "flow" can be exchange by "graph" or "pipeline".
```

## Non-linearity

The term graph is motivated by the non-linearity characteristic of some
flows. A transformer can pass its data to more than one posterior
transformers:

```
[Transformer 1]   -+->   [Transformer 2]   ->   [Transformer 3]   -+
                   |                                               |
                   +->   [Transformer 4]   ->   [Transformer 5]   -+->   [Transformer 6]
```

Any branch or ramification (transformers 2 and 3 or transformers 4 and 5 in above example) can have its own output types, and it can be of any length and including others ramifications.
